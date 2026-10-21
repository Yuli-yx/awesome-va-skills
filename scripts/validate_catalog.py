"""Validate metadata, local links, and optionally upstream source content."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import yaml

from catalog import ROOT, load_catalog, require, source_url


def anchors(text):
    result = set(re.findall(r'<a\s+id="([^"]+)"', text))
    used = {}
    for title in re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE):
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = used.get(slug, 0)
        result.add(slug if count == 0 else f"{slug}-{count}")
        used[slug] = count + 1
    return result


def check_links(root):
    checked = 0
    documents = [root / "README.md", root / "README.en.md", root / "CONTRIBUTING.md", root / "AGENTS.md"]
    for folder in ("docs", "evidence", "assets", ".github"):
        documents.extend((root / folder).rglob("*.md"))
    for document in documents:
        text = document.read_text(encoding="utf-8")
        # Example commands and templates do not create rendered links.
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        links = re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", text)
        links += re.findall(r'(?:src|srcset)="([^"]+)"', text)
        for link in links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            target = (document.parent / unquote(parsed.path)).resolve() if parsed.path else document.resolve()
            require(target.is_relative_to(root.resolve()), f"{document.name}: link escapes repository: {link}")
            require(target.exists(), f"{document.name}: broken link: {link}")
            if parsed.fragment and target.suffix == ".md":
                require(unquote(parsed.fragment) in anchors(target.read_text(encoding="utf-8")), f"{document.name}: missing anchor: {link}")
            checked += 1
    for svg in (root / "assets").glob("*.svg"):
        require(ET.parse(svg).getroot().tag == "{http://www.w3.org/2000/svg}svg", f"Invalid SVG: {svg}")
    return checked


def check_sources(sources, skills, mappings):
    for mapping in mappings:
        ident, separator, value = mapping.partition("=")
        require(separator and ident in sources and value, f"Invalid source mapping: {mapping}")
        root = Path(value).resolve()
        revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        require(revision == sources[ident]["revision"], f"{ident}: checkout revision differs from catalogue")
        for item in skills:
            if item["source"]["project"] == ident:
                file = (root / item["source"]["path"]).resolve()
                require(file.is_relative_to(root), f"{item['id']}: source path escapes checkout")
                require(hashlib.sha256(file.read_bytes()).hexdigest() == item["source"]["sha256"], f"{item['id']}: local source hash differs")


def check_remote(item, sources):
    try:
        request = Request(source_url(item, sources, raw=True), headers={"User-Agent": "awesome-mindie-skills-catalog-check"})
        with urlopen(request, timeout=20) as response:
            content = response.read()
        require(hashlib.sha256(content).hexdigest() == item["source"]["sha256"], "source hash differs")
        return None
    except Exception as error:
        return f"{item['id']}: {error}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--source-root", action="append", default=[], metavar="PROJECT=PATH", help="Verify a local upstream checkout and SKILL.md hashes")
    parser.add_argument("--check-remote", action="store_true", help="Fetch pinned upstream SKILL.md files and verify their hashes")
    args = parser.parse_args()
    try:
        categories, sources, skills = load_catalog(args.root)
        links = check_links(args.root)
        check_sources(sources, skills, args.source_root)
        if args.check_remote:
            with ThreadPoolExecutor(max_workers=6) as executor:
                failures = [result for result in executor.map(lambda item: check_remote(item, sources), skills) if result]
            require(not failures, "Remote source check failed:\n" + "\n".join(failures))
        print(f"Validated {len(skills)} skills, {len(categories)} taxonomy categories, {len(sources)} source project(s), and {links} local links.")
        if args.source_root:
            print("Local source revisions and SKILL.md hashes match.")
        if args.check_remote:
            print("All pinned upstream SKILL.md files are reachable and match their recorded hashes.")
    except (ValueError, OSError, KeyError, TypeError, yaml.YAMLError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
