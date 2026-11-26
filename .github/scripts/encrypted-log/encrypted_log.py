"""Encrypt a failed CI job's private log with age, for a short-lived artifact.

This repository is public, so its Actions logs and artifacts are public. Two
workflows run the private product repository's code and keep its output in a
private log under RUNNER_TEMP: Product CI (product-ci/run.py) and the Mac jobs
of Build DMG (build-dmg/encrypt_logs.py). When one fails, its log leaves the
runner only as age ciphertext to LOG_RECIPIENT, the public half of the
maintainers' key; the private half is in no repository, secret or runner.
fetch_log.py, beside this file, downloads and decrypts it for a key holder.

The rule both share lives here, once: the upload directory holds nothing but
age ciphertext. The plaintext reaches age on stdin, age writes to a hidden
partial file (the upload's *.age pattern never matches it), and only output
that starts with the age header is renamed into place. Any other outcome
(no age, age failing or timing out, output that is not age's) removes the
partial file, prints one fixed line and leaves nothing to upload.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

#: The public half of the maintainers' age key. Safe to print and commit.
LOG_RECIPIENT = "age14zuswrahtrqh7ksyjjv7u0vxqsrxzykhymfavt6x9yvuram67p9se6ngeq"
#: The first line of every binary age file. Anything else is not uploaded.
AGE_HEADER = b"age-encryption.org/v1\n"
AGE_TIMEOUT_S = 300


@dataclass(frozen=True)
class Kind:
    """One family of encrypted log artifacts: its names, and how a key holder reads one."""

    prefix: str
    names: tuple[str, ...]
    make_target: str
    make_var: str

    def artifact(self, name: str, attempt: str | None = None) -> str:
        """The artifact name the workflow uploads *name*'s log as (tests hold the YAML to it)."""
        return f"{self.prefix}-{name}-log-attempt{run_attempt(attempt)}"

    def ciphertext(self, name: str) -> str:
        """The one file inside that artifact."""
        return f"{name}.log.age"

    def read_command(self, name: str, run_id: str | None = None) -> str:
        """The make command that downloads and decrypts the log."""
        run_id = run_id if run_id is not None else os.environ.get("GITHUB_RUN_ID", "")
        run_arg = run_id if run_id.isdigit() else "<run id>"
        return f"make {self.make_target} RUN={run_arg} {self.make_var}={name}"


PRODUCT_CI = Kind("product-ci", ("python", "desktop", "rust"), "product-ci-log", "SUITE")
BUILD_DMG = Kind("build-dmg", ("signed", "adhoc"), "build-dmg-log", "JOB")
KINDS = {kind.prefix: kind for kind in (PRODUCT_CI, BUILD_DMG)}


def run_attempt(attempt: str | None = None) -> str:
    """This run's attempt number (GITHUB_RUN_ATTEMPT), "1" when unknown."""
    attempt = attempt if attempt is not None else os.environ.get("GITHUB_RUN_ATTEMPT", "")
    return attempt if attempt.isdigit() else "1"


def upload_dir_refusal(encrypted_dir: Path, private_dirs: Iterable[Path]) -> str:
    """Why *encrypted_dir* may not be the upload directory, or "" when it may.

    It must neither hold nor sit inside a directory with plaintext or secrets in it.
    """
    encrypted_dir = encrypted_dir.resolve()
    for private in private_dirs:
        private = private.resolve()
        if private.is_relative_to(encrypted_dir) or encrypted_dir.is_relative_to(private):
            return "the upload directory must not hold or sit inside a directory with the plaintext log or a secret"
    return ""


def unavailable(reason: str, out=sys.stdout) -> bool:
    print(f"Encrypted log: none ({reason}).", file=out, flush=True)
    return False


def encrypt(plaintext: bytes, kind: Kind, name: str, encrypted_dir: Path, env: dict[str, str],
            out=sys.stdout) -> bool:
    """Encrypt *plaintext* to LOG_RECIPIENT as <encrypted_dir>/<name>.log.age; print one fixed line.

    Returns True when the ciphertext is in place for the upload step.
    """
    age = shutil.which("age", path=env.get("PATH"))
    if age is None:
        return unavailable("age is not installed on this runner", out)
    encrypted_dir = encrypted_dir.resolve()
    encrypted_dir.mkdir(parents=True, exist_ok=True)
    target = encrypted_dir / kind.ciphertext(name)
    partial = encrypted_dir / f".{target.name}.partial"
    for stale in (target, partial):
        stale.unlink(missing_ok=True)
    try:
        status = subprocess.run((age, "--encrypt", "--recipient", LOG_RECIPIENT, "--output", str(partial)),
                                input=plaintext, env=env, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, timeout=AGE_TIMEOUT_S).returncode
        reason = "" if status == 0 else f"age failed with exit {status}"
    except subprocess.TimeoutExpired:
        reason = f"age timed out after {AGE_TIMEOUT_S} s"
    except OSError as exc:
        reason = f"age could not start: {type(exc).__name__}"
    if not reason:
        try:
            with partial.open("rb") as written:
                if written.read(len(AGE_HEADER)) != AGE_HEADER:
                    reason = "age wrote something that is not age ciphertext"
        except OSError:
            reason = "age wrote no output"
    if reason:
        partial.unlink(missing_ok=True)
        return unavailable(reason, out)
    os.replace(partial, target)
    print(f"Encrypted log: available as artifact {kind.artifact(name)}, readable only with the "
          f"maintainers' key ({kind.read_command(name)}).", file=out, flush=True)
    return True
