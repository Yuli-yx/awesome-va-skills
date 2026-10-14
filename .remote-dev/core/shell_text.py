"""Read-only pre-upload checks for scripts executed by Unix shells."""
from __future__ import annotations

import re
from pathlib import Path

SHELL_SUFFIXES = {".sh", ".bash", ".zsh", ".ksh"}
SHELL_SHEBANG = re.compile(rb"^#![^\r\n]*\b(?:ba|da|z|k)?sh(?:\s|$)")


def shell_text_error(path: Path, remote_name: str = "") -> str | None:
    """Reject CR bytes/BOM in shell source without rewriting user content.

    Archives and other non-shell artifacts are deliberately not transformed.
    The destination suffix also catches local temporary files uploaded as .sh.
    """
    with path.open("rb") as stream:
        prefix = stream.read(4096)
        is_shell = (
            path.suffix.lower() in SHELL_SUFFIXES
            or Path(remote_name).suffix.lower() in SHELL_SUFFIXES
            or SHELL_SHEBANG.match(prefix.removeprefix(b"\xef\xbb\xbf")) is not None
        )
        if not is_shell:
            return None
        if prefix.startswith((b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")):
            reason = "BOM"
        else:
            chunk = prefix
            while chunk and b"\r" not in chunk:
                chunk = stream.read(1024 * 1024)
            reason = "CRLF/CR" if b"\r" in chunk else ""
        if reason:
            return (
                f"Shell upload blocked: {path} contains {reason}. "
                "Save the local script as UTF-8 without BOM and LF line endings, "
                "then upload again and run bash -n remotely before execution. "
                "No file was normalized or uploaded by this preflight."
            )
    return None
