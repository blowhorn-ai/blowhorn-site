#!/usr/bin/env python3
"""Run the product repository's test suite and print only a summary.

This repository is public, so its Actions logs are public. The product
repository is private: its test names, file paths, assertion diffs and source
lines must never reach a log here. Every command's output goes to a log file
outside the workspace that is never printed, and never uploaded except as age
ciphertext (below). The only lines
printed are this script's fixed step labels, each step's exit status, and the
pass/fail counts parsed out of the test runners' summary lines (numbers and a
fixed set of words, nothing copied verbatim), plus, for a failed pytest, cargo or
vitest run, the id of each failing test (path and test name only for pytest;
crate or test binary and test name only for cargo; tests/ path and title only
for vitest) and, for vitest, the 'Unhandled Errors' / 'Unhandled Error' /
'Unhandled Rejection' heading names; each checked against a strict pattern;
never its message, diff, assertion text, stack or source lines). The commands run without the
runner's file-command variables (GITHUB_STEP_SUMMARY and the like), so they
cannot write a job summary, step output or environment change either, and
without the calling make's state (MAKEFLAGS, MAKELEVEL), so they run as the
product's own CI runs them.

When a step fails and --encrypted-dir is given, the suite's full log is
encrypted with age to LOG_RECIPIENT (the public half of the maintainers' key;
the private half is kept off the runner, in no repository) into
<encrypted-dir>/<suite>.log.age, by the shared encrypted-log/encrypted_log.py.
That ciphertext is the one thing product-ci.yml uploads, as a short-lived
artifact; the upload directory never holds the plaintext log or a copy of it.
Read it with `make product-ci-log RUN=<run id> SUITE=<suite>`.

Usage: run.py --product DIR --log FILE [--encrypted-dir DIR] python|desktop|rust
Exit status: 0 when every step passed, else the failing step's status.
To see why a step failed, decrypt the log artifact, or run the same suite
locally in the product checkout (`make tests`).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "encrypted-log"))
import encrypted_log  # noqa: E402

ANSI =re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
PYTEST_SUMMARY = re.compile(r"^=*\s*(.*?) in \d+(?:\.\d+)?s(?: \(\d+:\d\d:\d\d\))?\s*=*\s*$")
PYTEST_COUNT = re.compile(r"\b(\d+) (passed|failed|skipped|xfailed|xpassed|errors?|deselected|warnings?)\b")
#: pytest's short summary ("-rfE"): "FAILED tests/x.py::Case::test_y - message".
#: A failed subtest (pytest-subtests, which the product uses) puts its
#: description first: "(command='x') SUBFAIL tests/x.py::Case::test_y - message".
#: Only the node id is kept, and only when it is a plain path::name id: the
#: subtest description, the parametrize id and the message are all dropped.
PYTEST_FAILED = re.compile(
    r"^(?:(FAILED|ERROR)|.*? SUBFAIL) "
    r"(tests/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+\.py(?:::[A-Za-z0-9_]+){1,3})(?:\[.*?\])?(?: - .*)?$"
)
MAX_FAILED_IDS = 20
VITEST_LINE = re.compile(r"^\s*(Test Files|Tests|Errors)\s+(.*)$")
VITEST_COUNT = re.compile(r"\b(\d+) (passed|failed|skipped|todo|errors?)\b")
VITEST_LABEL = {"Test Files": "files", "Tests": "tests", "Errors": "errors"}
#: Vitest 4 banners: divider + heading + divider (U+23AF or ASCII/box dashes).
VITEST_UNHANDLED = re.compile(
    r"^[⎯─\-]{2,}\s*(Unhandled Errors|Unhandled Error|Unhandled Rejection)\s*[⎯─\-]{2,}\s*$"
)
#: A test file under tests/; no '..' or absolute paths.
VITEST_TEST_FILE = r"tests/(?:[A-Za-z0-9._-]+/)*[A-Za-z0-9._-]+\.(?:ts|tsx|js|jsx|mts|cts|mjs|cjs)"
VITEST_TEST_FILE_RE = re.compile(VITEST_TEST_FILE)
VITEST_FAIL_SUFFIX = re.compile(rf" \[ ({VITEST_TEST_FILE}) \]$")
CARGO_RESULT = re.compile(
    r"^test result: (?:ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out"
)
#: cargo/libtest identifiers: a crate or test binary, or a ::-separated test path.
#: No slashes, dots or spaces, so source paths and assertion text cannot pass.
CARGO_IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
CARGO_TEST_PATH = rf"(?:{CARGO_IDENT}::){{0,8}}{CARGO_IDENT}"
#: "     Running unittests src/lib.rs (target/debug/deps/crate-abc123)"
#: The source path is ignored; only the deps/binary-hash name is kept.
CARGO_RUNNING = re.compile(
    rf"^\s*Running .*\((?:[A-Za-z0-9._-]+/)*deps/({CARGO_IDENT})-[0-9a-f]+\)\s*$"
)
#: Verbose: Running `.../deps/crate-abc123 --exact`
CARGO_RUNNING_CMD = re.compile(
    rf"^\s*Running `[^`]*?/(?:deps/)?({CARGO_IDENT})-[0-9a-f]+\b[^`]*`\s*$"
)
CARGO_TEST_FAILED = re.compile(rf"^test ({CARGO_TEST_PATH}) \.\.\. FAILED\s*$")
CARGO_FAILURES_ITEM = re.compile(rf"^    ({CARGO_TEST_PATH})\s*$")
FILE_COMMANDS = frozenset({"GITHUB_ENV", "GITHUB_OUTPUT", "GITHUB_PATH", "GITHUB_STATE", "GITHUB_STEP_SUMMARY"})
#: `make product-ci` starts this script, so its environment carries the calling
#: make's state. The product's own CI runs pytest directly, and its tests run
#: `make` and compare the output: an inherited MAKELEVEL adds "Entering
#: directory" lines and MAKEFLAGS passes this make's variables down.
MAKE_STATE = frozenset({"MAKEFLAGS", "MAKELEVEL", "MFLAGS", "MAKEOVERRIDES"})
# Checkout tokens must never reach the product's pytest, pnpm or cargo.
SECRET_ENV = frozenset({
    "DMG_SOURCE_TOKEN",
    "INPUT_PRODUCT_TOKEN",
    "INPUT_TOKEN",
    "GH_TOKEN",
    "GITHUB_TOKEN",
})


@dataclass(frozen=True)
class Step:
    label: str
    argv: tuple[str, ...]
    cwd: str = "."
    timeout_s: int = 600
    counts: str = ""  # "pytest" or "vitest": parse that runner's summary


def python_suite_workers() -> int:
    """Cores this dedicated runner should give pytest-xdist: every core, at least 2."""
    return max(2, os.cpu_count() or 2)


def python_steps(python: str) -> list[Step]:
    """The Python job of the product's own ci.yml, step for step."""
    return [
        Step("install dependencies", (python, "-m", "pip", "install", "--disable-pip-version-check",
                                      "-r", "engine/requirements-dev.txt"), timeout_s=600),
        Step("playwright import boundary", (python, "release/scripts/check_playwright_imports.py"), timeout_s=120),
        # The product's own CI runs `make cli-tests`. Its default PYTEST_WORKERS
        # is half the cores, which is 1 (no xdist) on a 2-core runner, and a
        # single pytest process hits the 900 s timeout. This job is a dedicated
        # runner, so use every core, and at least 2 so xdist is on.
        Step("test suite", ("timeout", "-s", "ABRT", "900", "make", "cli-tests",
                            f"PYTHON={python} -u",
                            "PYTEST_ARGS=tests/ -q -rfE -o faulthandler_timeout=300",
                            f"PYTEST_WORKERS={python_suite_workers()}"),
             timeout_s=960, counts="pytest"),
    ]


def rust_steps() -> list[Step]:
    """The Rust engine tests (`make cli-rust-tests` in the product checkout).

    Live Google Chrome tests in that suite skip when Chrome is not installed.
    """
    return [
        Step("test suite", ("make", "cli-rust-tests"), timeout_s=2400, counts="cargo"),
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
    """'6905 passed, 526 skipped' from pytest's last summary line ('... in 300.12s'); '' when there is none."""
    for line in reversed(ANSI.sub("", text).splitlines()):
        summary = PYTEST_SUMMARY.match(line)
        if summary:
            return ", ".join(f"{n} {word}" for n, word in PYTEST_COUNT.findall(summary.group(1)))
    return ""


def pytest_failed_ids(text: str) -> list[str]:
    """Node ids of failing pytest tests from the short summary; parametrize ids and messages dropped."""
    ids: list[str] = []
    for line in ANSI.sub("", text).splitlines():
        match = PYTEST_FAILED.match(line.strip())
        if match:
            word = (match.group(1) or "FAILED").lower()  # a SUBFAIL is a failed test
            _add_failed_id(ids, f"{word} {match.group(2)}")
    return ids[:MAX_FAILED_IDS]


def vitest_counts(text: str) -> str:
    """'files: 98 passed; tests: 1367 passed' from vitest's summary; '' when there is none.

    The optional 'Errors N error(s)' line is included when present, so an
    unhandled-error run is not reported as a clean pass/fail count.
    """
    parts = []
    for line in ANSI.sub("", text).splitlines():
        match = VITEST_LINE.match(line)
        if not match:
            continue
        found = VITEST_COUNT.findall(match.group(2))
        if found:
            name = VITEST_LABEL[match.group(1)]
            parts.append(f"{name}: " + ", ".join(f"{n} {word}" for n, word in found))
    return "; ".join(parts[-3:])


def vitest_failed_ids(text: str) -> list[str]:
    """Failing vitest test names and Unhandled Errors headings; stacks and source dropped."""
    ids: list[str] = []
    for raw in ANSI.sub("", text).splitlines():
        line = raw.strip()
        banner = VITEST_UNHANDLED.match(line)
        if banner:
            _add_failed_id(ids, banner.group(1).lower())
            continue
        if not line.startswith("FAIL  "):
            continue
        rest = line[len("FAIL  "):]
        suffix = VITEST_FAIL_SUFFIX.search(rest)
        file_in_suffix = suffix.group(1) if suffix else None
        if suffix:
            rest = rest[:suffix.start()]
        rest = re.sub(r" \(\d+\)$", "", rest)
        file_in_head = None
        title = None
        head = VITEST_TEST_FILE_RE.match(rest)
        if head and (head.end() == len(rest) or rest[head.end():].startswith(" > ")):
            file_in_head = head.group(0)
            if rest[head.end():].startswith(" > "):
                title = rest[head.end() + 3:]
        elif file_in_suffix:
            title = rest or None
        path = file_in_head or file_in_suffix
        if not path or ".." in path:
            continue
        if title and ".." in title:
            title = None
        entry = f"failed {path}" + (f" > {title}" if title else "")
        _add_failed_id(ids, entry)
    return ids[:MAX_FAILED_IDS]


def cargo_counts(text: str) -> str:
    """'40 passed, 2 ignored' aggregated from cargo's 'test result:' lines; '' when there is none.

    Only the counts and a fixed set of words are returned here. Failing test
    names are collected separately by cargo_failed_ids.
    """
    passed = failed = ignored = 0
    found = False
    for line in ANSI.sub("", text).splitlines():
        match = CARGO_RESULT.match(line.strip())
        if not match:
            continue
        found = True
        passed += int(match.group(1))
        failed += int(match.group(2))
        ignored += int(match.group(3))
    if not found:
        return ""
    parts = [f"{passed} passed"]
    if failed:
        parts.append(f"{failed} failed")
    if ignored:
        parts.append(f"{ignored} ignored")
    return ", ".join(parts)


def cargo_failed_ids(text: str) -> list[str]:
    """Crate or test binary plus test name of failing cargo tests; assertion text and source paths dropped."""
    ids: list[str] = []
    binary = ""
    lines = ANSI.sub("", text).splitlines()
    i = 0
    while i < len(lines) and len(ids) < MAX_FAILED_IDS:
        line = lines[i]
        running = CARGO_RUNNING.match(line) or CARGO_RUNNING_CMD.match(line)
        if running:
            binary = running.group(1)
            i += 1
            continue
        failed = CARGO_TEST_FAILED.match(line)
        if failed:
            _add_failed_id(ids, _cargo_failed_entry(binary, failed.group(1)))
            i += 1
            continue
        if line.strip() == "failures:":
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].lstrip().startswith("----"):
                i = j + 1
                while i < len(lines):
                    nxt = lines[i]
                    if nxt.strip() == "failures:":
                        break
                    if CARGO_RUNNING.match(nxt) or CARGO_RUNNING_CMD.match(nxt):
                        break
                    if nxt.startswith("test result:"):
                        break
                    i += 1
                continue
            i += 1
            while i < len(lines):
                item = CARGO_FAILURES_ITEM.match(lines[i])
                if item:
                    _add_failed_id(ids, _cargo_failed_entry(binary, item.group(1)))
                    i += 1
                    continue
                break
            continue
        i += 1
    return ids[:MAX_FAILED_IDS]


def _cargo_failed_entry(binary: str, test: str) -> str:
    ident = f"{binary}::{test}" if binary else test
    return f"failed {ident}"


def _add_failed_id(ids: list[str], entry: str) -> None:
    if entry not in ids and len(ids) < MAX_FAILED_IDS:
        ids.append(entry)


COUNTERS = {"pytest": pytest_counts, "vitest": vitest_counts, "cargo": cargo_counts}
FAILED_IDS = {"pytest": pytest_failed_ids, "vitest": vitest_failed_ids, "cargo": cargo_failed_ids}


def encrypt_log(log: Path, suite: str, encrypted_dir: Path, env: dict[str, str], out=sys.stdout) -> bool:
    """Encrypt *log* to LOG_RECIPIENT as <encrypted_dir>/<suite>.log.age; print one fixed line."""
    refusal = encrypted_log.upload_dir_refusal(encrypted_dir, (log.parent,))
    if refusal:
        return encrypted_log.unavailable(refusal, out)
    return encrypted_log.encrypt(log.read_bytes(), encrypted_log.PRODUCT_CI, suite, encrypted_dir, env, out=out)


def run_steps(steps: list[Step], product: Path, log: Path, out=sys.stdout, *,
              suite: str = "", encrypted_dir: Path | None = None) -> int:
    """Run *steps* in order inside *product*, every byte of output to *log*; stop at the first failure.

    On a failure, when *encrypted_dir* is given, the whole log is encrypted
    there (encrypt_log) for the workflow to upload.
    """
    log.parent.mkdir(parents=True, exist_ok=True)
    env = {name: value for name, value in os.environ.items()
           if name not in FILE_COMMANDS | MAKE_STATE | SECRET_ENV}
    with log.open("ab") as sink:
        for step in steps:
            started = time.monotonic()
            sink.write(f"\n===== {step.label} =====\n".encode())
            sink.flush()
            before = sink.tell()
            try:
                status = subprocess.run(step.argv, cwd=product / step.cwd, env=env, stdin=subprocess.DEVNULL,
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
            if status != 0 and step.counts in FAILED_IDS:
                with log.open("rb") as read:
                    read.seek(before)
                    for entry in FAILED_IDS[step.counts](read.read().decode("utf-8", "replace")):
                        print(f"  {entry}", file=out, flush=True)
            if status != 0:
                print("Output is withheld because the product repository is private; "
                      "run the same suite in a local checkout to see it.", file=out, flush=True)
                if encrypted_dir is not None:
                    encrypt_log(log, suite, encrypted_dir, env, out=out)
                return status
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("suite", choices=("python", "desktop", "rust"))
    parser.add_argument("--product", required=True, type=Path, help="the product repository checkout")
    parser.add_argument("--log", required=True, type=Path, help="private log file, never printed")
    parser.add_argument("--encrypted-dir", type=Path,
                        help="on a failure, write the log's age ciphertext here (the workflow uploads it)")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args(argv)
    if args.suite == "python":
        steps = python_steps(args.python)
    elif args.suite == "desktop":
        steps = desktop_steps()
    else:
        steps = rust_steps()
    return run_steps(steps, args.product, args.log, suite=args.suite, encrypted_dir=args.encrypted_dir)


if __name__ == "__main__":
    sys.exit(main())
