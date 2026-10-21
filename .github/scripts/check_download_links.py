#!/usr/bin/env python3
"""Fail if the built site links to a /releases/latest/download URL.

layer5io/blowhorn-site also publishes blowhorn-axi releases, and GitHub's
"latest" release is whichever stable release was created most recently, so
/releases/latest/download/Blowhorn-mac.dmg 404s or serves the wrong file
whenever an axi release is newer. Every download URL is built from the
pinned version in data/download.json instead (docs/distribution.md).

Reads every built .html, .js, .json and .xml file, so JSON-LD, feeds and
scripts are covered as well as links.

Usage: check_download_links.py [BUILD_DIR]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

LATEST_DOWNLOAD_RE = re.compile(r"github\.com/[\w.-]+/[\w.-]+/releases/latest/download[^\s\"'<>)]*")
SUFFIXES = {".html", ".js", ".json", ".xml"}


def find(build_dir: Path) -> list[str]:
    hits = []
    for path in sorted(build_dir.rglob("*")):
        if path.suffix not in SUFFIXES or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in LATEST_DOWNLOAD_RE.finditer(text):
            hits.append(f"{path.relative_to(build_dir)}: {match.group(0)}")
    return hits


def main(argv: list[str]) -> int:
    build_dir = Path(argv[1] if len(argv) > 1 else "public")
    if not build_dir.is_dir():
        print(f"check_download_links: {build_dir} is not a directory", file=sys.stderr)
        return 2
    hits = find(build_dir)
    for hit in hits:
        print(f"::error::{hit} uses /releases/latest/download; build it from data/download.json")
    if hits:
        return 1
    print("check_download_links: no /releases/latest/download URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
