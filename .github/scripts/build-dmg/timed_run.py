"""Run one build-dmg phase with a hard time limit and a private log.

The child's output goes only to the log, which is never printed, uploaded or
cached. Stdout gets fixed labels: the phase start and end with UTC timestamps
and the elapsed time, and the few progress lines that `progress_line` lets
through (release phase headers and notarization submission id and status).
On timeout the whole process group is killed and the phase fails with a clear
message instead of running into the job's timeout.

Children start with the default SIGPIPE handler (subprocess restores it), so
a `producer | head` pipeline in a product script exits as it would in a
terminal rather than spinning under the runner's ignored SIGPIPE.

Usage: timed_run.py --label NAME --timeout-minutes N --log FILE -- CMD...
"""

from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

# Lines safe to echo from the private log. Each pattern matches the whole
# line and captures only fixed vocabulary, a UUID, or a phase name, so no
# path, identifier, key or tool output can pass.
_PROGRESS = (
    (re.compile(r"==> ([a-z][a-z0-9-]{0,40})"), "phase {0}"),
    (re.compile(r"Submission ID received"), "notarization: submitted"),
    (re.compile(r"\s*id: ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"), "notarization: submission id {0}"),
    (re.compile(r"\s*(?:Current )?status: (Accepted|Invalid|Rejected|In Progress)\.*"), "notarization: status {0}"),
    (re.compile(r"Processing complete"), "notarization: processing complete"),
)


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def progress_line(line: str) -> str | None:
    """The public form of *line*, or None when it must stay in the log."""
    for pattern, template in _PROGRESS:
        match = pattern.fullmatch(line.rstrip())
        if match:
            return template.format(*match.groups())
    return None


def say(label: str, message: str) -> None:
    print(f"build-dmg: [{stamp()}] {label}: {message}", flush=True)


def run_logged(
    cmd: list[str],
    *,
    label: str,
    log: Path,
    timeout_s: float,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    popen: Callable[..., subprocess.Popen] | None = None,
) -> tuple[int, int, bool]:
    """Run *cmd* with output to *log*; return (exit status, seconds, timed out)."""
    log.parent.mkdir(parents=True, exist_ok=True)
    say(label, f"start (limit {timeout_s / 60:g} min)")
    started = time.monotonic()
    timed_out = threading.Event()
    last = None
    with log.open("wb") as sink:
        proc = (popen or subprocess.Popen)(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)

        def expire() -> None:
            timed_out.set()
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                proc.kill()

        timer = threading.Timer(timeout_s, expire)
        timer.daemon = True
        timer.start()
        try:
            for raw in proc.stdout:
                sink.write(raw)
                sink.flush()
                # notarytool redraws its status line with carriage returns.
                for part in raw.decode("utf-8", "replace").replace("\r", "\n").split("\n"):
                    public = progress_line(part)
                    if public and public != last:
                        last = public
                        say(label, public)
            status = proc.wait()
        finally:
            timer.cancel()
    elapsed = int(time.monotonic() - started)
    if timed_out.is_set():
        say(label, f"timed out after {elapsed}s (limit {timeout_s / 60:g} min); the process group was killed. The private log has the output.")
        return 124, elapsed, True
    say(label, f"end (exit {status}, {elapsed}s)")
    return status, elapsed, False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", required=True)
    parser.add_argument("--timeout-minutes", required=True, type=float)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("cmd", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    cmd = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
    if not cmd:
        parser.error("a command is required after --")
    status, _, _ = run_logged(cmd, label=args.label, log=args.log, timeout_s=args.timeout_minutes * 60)
    return status


if __name__ == "__main__":
    sys.exit(main())
