#!/usr/bin/env python3
"""Fail if content/ or data/ repeat banned absolute custody claims.

Live pages used to say passwords never leave the computer, or that
the company's keys stay local. LinkedIn, X, Reddit and Hacker News
sessions stay in Chrome on the user's Mac; Slack is stored in the
account; some profile passwords can live in profile config. This
check holds the source to that.

Usage: check-custody-claims.py [ROOT]
ROOT defaults to the repository root (two levels above this script).
Scans content/ and data/.
"""

from __future__ import annotations

import sys
from pathlib import Path

PHRASES = (
    "never leave your",
    "keep its keys",
    "keys stay",
)

SCAN_DIRS = ("content", "data")


def hits_in(root: Path) -> list[str]:
    found = []
    for name in SCAN_DIRS:
        base = root / name
        if not base.is_dir():
            continue
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            lower = text.lower()
            rel = path.relative_to(root).as_posix()
            for phrase in PHRASES:
                if phrase in lower:
                    found.append(f"{rel}: {phrase!r}")
    return found


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parents[2]
    found = hits_in(root)
    if found:
        print("check-custody-claims: banned absolute custody phrasing:", file=sys.stderr)
        for line in found:
            print(line, file=sys.stderr)
        return 1
    listed = ", ".join(repr(p) for p in PHRASES)
    print(f"check-custody-claims: content/ and data/ carry none of {listed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
