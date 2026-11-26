#!/usr/bin/env python3
"""Download and decrypt a failed job's encrypted log (`make product-ci-log`, `make build-dmg-log`).

product-ci.yml (a failed suite) and build-dmg.yml (a failed Mac build) upload
the job's full log only as age ciphertext to LOG_RECIPIENT (encrypted_log.py),
as the artifact <kind>-<name>-log-attempt<n>. This script downloads that
artifact with `gh run download` into a new private temporary directory outside
the repository, decrypts it with the maintainers' private key, deletes the
ciphertext and prints the plaintext file's path. It never prints the log's
contents: the log holds private product code and must not reach a terminal
transcript, an issue, a pull request or this public repository.

The private key never leaves the machine that holds it. This script only
reads it, through `age -d -i KEY`.

Usage: fetch_log.py --kind product-ci|build-dmg --name NAME --run RUN_ID --key FILE
                    [--attempt N] [--repo OWNER/NAME]
       (NAME is a suite, python|desktop|rust, or a Build DMG job, signed|adhoc)
Exit status: 0 with the decrypted file's path printed, 2 on a refused
request (no key, bad run id or name, missing tool), 1 when a download or
decryption fails.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from encrypted_log import KINDS, Kind  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REPO = "blowhorn-ai/blowhorn-site"
DOWNLOAD_TIMEOUT_S = 300
DECRYPT_TIMEOUT_S = 120


class Refused(Exception):
    """A request this script will not carry out; exit 2."""


class Failed(Exception):
    """A download or decryption that did not work; exit 1."""


def artifact_dir_attempt(dirname: str, kind: Kind, name: str) -> int | None:
    """The run attempt in a downloaded artifact directory's name, or None."""
    match = re.fullmatch(rf"{re.escape(kind.prefix)}-{re.escape(name)}-log-attempt(\d+)", dirname)
    return int(match.group(1)) if match else None


def fetch(kind: Kind, name: str, run: str, key: Path, *, attempt: str = "", repo: str = DEFAULT_REPO,
          workdir: Path | None = None) -> Path:
    """Download and decrypt one job's log; return the plaintext file's path."""
    if not run.isdigit():
        raise Refused(f"RUN must be a workflow run id (digits), not {run!r}.")
    if name not in kind.names:
        raise Refused(f"{kind.make_var} must be one of {', '.join(kind.names)}.")
    if attempt and not attempt.isdigit():
        raise Refused("ATTEMPT must be a run attempt number.")
    if not key.is_file():
        raise Refused(f"No private key at {key}. Pass KEY=<path to the age identity file>.")
    for tool in ("gh", "age"):
        if shutil.which(tool) is None:
            raise Refused(f"{tool} is not installed.")

    out_dir = Path(tempfile.mkdtemp(prefix=f"{kind.prefix}-log-", dir=workdir)).resolve()
    if out_dir.is_relative_to(ROOT):
        shutil.rmtree(out_dir)
        raise Refused("The temporary directory is inside the repository; set TMPDIR elsewhere.")
    try:
        download = out_dir / "download"
        pattern = f"{kind.prefix}-{name}-log-attempt{attempt or '*'}"
        try:
            done = subprocess.run(("gh", "run", "download", run, "-R", repo, "-p", pattern, "-D", str(download)),
                                  stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                  timeout=DOWNLOAD_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise Failed(f"gh run download timed out after {DOWNLOAD_TIMEOUT_S} s.") from None
        if done.returncode != 0:
            raise Failed(f"gh run download found no {pattern} artifact on run {run} "
                         f"(it is kept 3 days, and only a failed job uploads one): {done.stderr.strip()}")
        found = {}
        for child in download.iterdir() if download.is_dir() else ():
            number = artifact_dir_attempt(child.name, kind, name)
            if number is not None and child.is_dir():
                found[number] = child
        if not found:
            raise Failed(f"Run {run} has no {pattern} artifact.")
        latest = max(found)
        ciphertext = found[latest] / kind.ciphertext(name)
        if not ciphertext.is_file():
            raise Failed(f"The artifact holds no {kind.ciphertext(name)}.")
        plaintext = out_dir / f"{kind.prefix}-{name}-run{run}-attempt{latest}.log"
        try:
            done = subprocess.run(("age", "--decrypt", "--identity", str(key), "--output", str(plaintext),
                                   str(ciphertext)), stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                  timeout=DECRYPT_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise Failed(f"age timed out after {DECRYPT_TIMEOUT_S} s.") from None
        if done.returncode != 0:
            raise Failed(f"age could not decrypt the log (is KEY the right identity?): {done.stderr.strip()}")
        shutil.rmtree(download)
        plaintext.chmod(0o600)
        return plaintext
    except BaseException:
        shutil.rmtree(out_dir, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kind", required=True, choices=sorted(KINDS))
    parser.add_argument("--name", required=True, help="the suite (product-ci) or the Mac job (build-dmg)")
    parser.add_argument("--run", required=True, help="the workflow run id")
    parser.add_argument("--key", required=True, type=Path, help="the age identity file (private key)")
    parser.add_argument("--attempt", default="", help="run attempt (default: the latest one with a log)")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    args = parser.parse_args(argv)
    kind = KINDS[args.kind]
    try:
        path = fetch(kind, args.name, args.run, args.key.expanduser(), attempt=args.attempt, repo=args.repo)
    except (Refused, Failed) as exc:
        print(f"{kind.make_target}: {exc}", file=sys.stderr)
        return 2 if isinstance(exc, Refused) else 1
    print(f"Decrypted log: {path}")
    print("It holds private product code: read it here, never paste it anywhere public, "
          f"and delete it when done (rm -r {path.parent}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
