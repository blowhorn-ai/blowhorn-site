#!/usr/bin/env python3
"""Run the product repository's test suite and print only a summary.

This repository is public, so its Actions logs are public. The product
repository is private: its test names, file paths, assertion diffs and source
lines must never reach a log here. Every command's output goes to a log file
outside the workspace that is never printed or uploaded. The only lines
printed are this script's fixed step labels, each step's exit status, and the
pass/fail counts parsed out of the test runners' summary lines (numbers and a
fixed set of words, nothing copied verbatim).

Usage: run.py --product DIR --log FILE python|desktop
Exit status: 0 when every step passed, else the failing step's status.
To see why a step failed, run the same suite locally in the product checkout
(`make tests`).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
PYTEST_COUNT = re.compile(r"\b(\d+) (passed|failed|skipped|xfailed|xpassed|errors?|deselected|warnings?)\b")
VITEST_LINE = re.compile(r"^\s*(Test Files|Tests)\s+(.*)$")
VITEST_COUNT = re.compile(r"\b(\d+) (passed|failed|skipped|todo)\b")


@dataclass(frozen=True)
class Step:
    label: str
    argv: tuple[str, ...]
    cwd: str = "."
    timeout_s: int = 600
    counts: str = ""  # "pytest" or "vitest": parse that runner's summary


def python_steps(python: str) -> list[Step]:
    """The Python job of the product's own ci.yml, step for step."""
    return [
        Step("install dependencies", (python, "-m", "pip", "install", "--disable-pip-version-check",
                                      "-r", "engine/requirements-dev.txt"), timeout_s=600),
        Step("playwright import boundary", (python, "release/scripts/check_playwright_imports.py"), timeout_s=120),
        Step("test suite", ("timeout", "-s", "ABRT", "900", python, "-u", "-m", "pytest", "tests/", "-q",
                            "-p", "no:cacheprovider", "-o", "faulthandler_timeout=300"),
             timeout_s=960, counts="pytest"),
    ]


def desktop_steps(pnpm: str = "pnpm") -> list[Step]:
    """The desktop job of the product's own ci.yml: install, typecheck, lint, test, build."""
    return [
        Step("install", (pnpm, "install", "--frozen-lockfile"), cwd="desktop", timeout_s=600),
        Step("typecheck", (pnpm, "typecheck"), cwd="desktop", timeout_s=600),
        Step("lint", (pnpm, "lint"), cwd="desktop", timeout_s=600),
        Step("test", (pnpm, "test"), cwd="desktop", timeout_s=900, counts="vitest"),
        Step("build", (pnpm, "build"), cwd="desktop", timeout_s=600),
    ]


def pytest_counts(text: str) -> str:
    """'6905 passed, 526 skipped' from pytest's last summary line; '' when there is none."""
    for line in reversed(ANSI.sub("", text).splitlines()):
        found = PYTEST_COUNT.findall(line)
        if found:
            return ", ".join(f"{n} {word}" for n, word in found)
    return ""


def vitest_counts(text: str) -> str:
    """'files: 98 passed; tests: 1367 passed' from vitest's summary; '' when there is none."""
    parts = []
    for line in ANSI.sub("", text).splitlines():
        match = VITEST_LINE.match(line)
        if not match:
            continue
        found = VITEST_COUNT.findall(match.group(2))
        if found:
            name = "files" if match.group(1) == "Test Files" else "tests"
            parts.append(f"{name}: " + ", ".join(f"{n} {word}" for n, word in found))
    return "; ".join(parts[-2:])


COUNTERS = {"pytest": pytest_counts, "vitest": vitest_counts}


def run_steps(steps: list[Step], product: Path, log: Path, out=sys.stdout) -> int:
    """Run *steps* in order inside *product*, every byte of output to *log*; stop at the first failure."""
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("ab") as sink:
        for step in steps:
            started = time.monotonic()
            sink.write(f"\n===== {step.label} =====\n".encode())
            sink.flush()
            before = sink.tell()
            try:
                status = subprocess.run(step.argv, cwd=product / step.cwd, stdin=subprocess.DEVNULL,
                                        stdout=sink, stderr=subprocess.STDOUT, timeout=step.timeout_s).returncode
                verdict = "ok" if status == 0 else f"failed (exit {status})"
            except subprocess.TimeoutExpired:
                status, verdict = 124, f"failed (timed out after {step.timeout_s} s)"
            except OSError as exc:
                status, verdict = 127, f"failed (could not start: {type(exc).__name__})"
            sink.flush()
            line = f"{step.label}: {verdict} in {time.monotonic() - started:.0f} s"
            if step.counts:
                with log.open("rb") as read:
                    read.seek(before)
                    counts = COUNTERS[step.counts](read.read().decode("utf-8", "replace"))
                if counts:
                    line += f" [{counts}]"
            print(line, file=out, flush=True)
            if status != 0:
                print("Output is withheld because the product repository is private; "
                      "run the same suite in a local checkout to see it.", file=out, flush=True)
                return status
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("suite", choices=("python", "desktop"))
    parser.add_argument("--product", required=True, type=Path, help="the product repository checkout")
    parser.add_argument("--log", required=True, type=Path, help="private log file, never printed")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args(argv)
    steps = python_steps(args.python) if args.suite == "python" else desktop_steps()
    return run_steps(steps, args.product, args.log)


if __name__ == "__main__":
    sys.exit(main())
