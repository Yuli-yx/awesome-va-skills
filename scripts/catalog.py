"""Shared catalogue loading and structural validation (Python 3.10+)."""

from datetime import date
from pathlib import Path, PurePosixPath
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("zh", "en")
EXECUTION = {"npu", "offline", "host", "depends-on-checks"}


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate mapping keys rather than silently replacing values."""


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


def read_yaml(path):
    with path.open(encoding="utf-8") as stream:
        return yaml.load(stream, Loader=UniqueLoader)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, expected, context):
    require(isinstance(value, dict), f"{context}: expected a mapping")
    require(set(value) == set(expected.split()), f"{context}: expected fields {expected}")


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def bilingual(value, context):
    keys(value, "zh en", context)
    require(all(nonempty(value[lang]) for lang in LANGUAGES), f"{context}: missing translation")


def iso_date(value, context):
    require(isinstance(value, str), f"{context}: quote dates as YYYY-MM-DD strings")
    date.fromisoformat(value)


def local_file(root, value):
    require(nonempty(value), "Expected a local file path")
    path = (root / value).resolve()
    require(path.is_relative_to(root.resolve()), f"Path escapes repository: {value}")
    require(path.is_file(), f"Missing file: {value}")
    return path


def load_catalog(root=ROOT):
    taxonomy = read_yaml(root / "catalog/categories.yaml")
    keys(taxonomy, "schema_version categories", "categories.yaml")
    require(taxonomy["schema_version"] == 1, "Unsupported taxonomy schema")
    require(isinstance(taxonomy["categories"], list), "categories must be a list")
    categories = {}
    for item in taxonomy["categories"]:
        keys(item, "id title description", "category")
        ident = item["id"]
        require(isinstance(ident, str) and re.fullmatch(r"[a-z][a-z0-9-]*", ident), "Invalid category ID")
        require(ident not in categories, f"Duplicate category: {ident}")
        bilingual(item["title"], ident)
        bilingual(item["description"], ident)
        categories[ident] = item

    source_data = read_yaml(root / "catalog/sources.yaml")
    keys(source_data, "schema_version sources", "sources.yaml")
    require(source_data["schema_version"] == 1, "Unsupported source schema")
    require(isinstance(source_data["sources"], dict), "sources must be a mapping")
    sources = source_data["sources"]
    for ident, source in sources.items():
        keys(source, "repository revision license maintainer", ident)
        require(isinstance(source["repository"], str) and re.fullmatch(
            r"https://(?:github|gitcode)\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source["repository"]
        ), f"{ident}: expected a GitHub or GitCode repository URL")
        require(isinstance(source["revision"], str) and re.fullmatch(r"[0-9a-f]{40}", source["revision"]), f"{ident}: expected full commit revision")
        require(nonempty(source["license"]) and nonempty(source["maintainer"]), f"{ident}: missing provenance")

    skills = []
    seen = set()
    for path in sorted((root / "catalog/skills").glob("*.yaml")):
        item = read_yaml(path)
        keys(item, "id category summary tags execution role source review validation", str(path))
        ident = item["id"]
        require(isinstance(ident, str) and re.fullmatch(r"[a-z][a-z0-9-]*", ident), f"{path}: invalid ID")
        require(ident == path.stem and ident not in seen, f"{path}: duplicate ID or filename mismatch")
        seen.add(ident)
        require(item["category"] in categories, f"{ident}: unknown category")
        bilingual(item["summary"], ident)
        require(isinstance(item["tags"], list) and item["tags"] and all(nonempty(t) for t in item["tags"]), f"{ident}: invalid tags")
        require(len(set(item["tags"])) == len(item["tags"]), f"{ident}: duplicate tags")
        require(item["execution"] in EXECUTION, f"{ident}: invalid execution condition")
        require(item["role"] in {"task", "workflow"}, f"{ident}: invalid role")
        source = item["source"]
        keys(source, "project path sha256", ident)
        require(source["project"] in sources, f"{ident}: unknown source project")
        require(nonempty(source["path"]), f"{ident}: missing source path")
        relative = PurePosixPath(source["path"])
        require(not relative.is_absolute() and ".." not in relative.parts and relative.name == "SKILL.md", f"{ident}: invalid source path")
        require(isinstance(source["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", source["sha256"]), f"{ident}: invalid source hash")
        review = item["review"]
        keys(review, "status date evidence", ident)
        require(review["status"] == "definition-reviewed", f"{ident}: definition review required")
        iso_date(review["date"], ident)
        local_file(root, review["evidence"])
        validation = item["validation"]
        keys(validation, "status cases", ident)
        require(validation["status"] in {"not-recorded", "reproduced"}, f"{ident}: invalid validation status")
        require(isinstance(validation["cases"], list), f"{ident}: cases must be a list")
        require(bool(validation["cases"]) == (validation["status"] == "reproduced"), f"{ident}: validation status/cases mismatch")
        for case in validation["cases"]:
            keys(case, "date source_revision environment scope evidence", ident)
            iso_date(case["date"], ident)
            require(case["source_revision"] == sources[source["project"]]["revision"], f"{ident}: validation revision mismatch")
            require(nonempty(case["scope"]), f"{ident}: missing validation scope")
            keys(case["environment"], "hardware software", ident)
            require(nonempty(case["environment"]["hardware"]) and nonempty(case["environment"]["software"]), f"{ident}: missing validation environment")
            local_file(root, case["evidence"])
        skills.append(item)
    require(bool(skills), "Catalogue has no skills")
    return categories, sources, skills


def source_url(item, sources, raw=False):
    source = item["source"]
    project = sources[source["project"]]
    base = project["repository"]
    if raw:
        if base.startswith("https://gitcode.com/"):
            base = base.replace("https://gitcode.com/", "https://raw.gitcode.com/")
            return f"{base}/raw/{project['revision']}/{source['path']}"
        base = base.replace("https://github.com/", "https://raw.githubusercontent.com/")
        return f"{base}/{project['revision']}/{source['path']}"
    return f"{base}/blob/{project['revision']}/{source['path']}"
