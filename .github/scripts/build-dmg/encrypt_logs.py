#!/usr/bin/env python3
"""Encrypt a failed Mac build's private logs for build-dmg-mac's upload step.

`make build-dmg-encrypt-log` runs this only when a step of the build-dmg-mac
action failed. The phases that run product code write their whole output to
private logs under RUNNER_TEMP/build-dmg/ (timed_run.py, run_build.py): the
desktop install (install.log), the signing keychain import (import.log) and
the build itself, preflight through package and verify (build.log). This
script joins whichever of them exist, each under a fixed header, and hands
them to the shared encrypted_log.encrypt, which writes only age ciphertext to
the upload directory (see encrypted-log/encrypted_log.py). The plaintext goes
to age on stdin and is never written anywhere new.

Secrets, a second guard: the build never prints key material (the keychain
import passes the passphrase only as argv to `security`, release-mac.mjs logs
the notarytool argv with the .p8's path and never its contents, and the
diagnostics key hook says only that it wrote the key). Even so, before
encrypting, every line that holds a staged secret's value is replaced with a
fixed marker, so the ciphertext never holds key material either. The values
are read from the files the signed job stages (SECRET_FILES); a value too
short to match safely refuses the whole upload instead of guessing. Apple's
public identifiers (team id, API key id, issuer) and file paths are not key
material and stay in the log.

Usage: encrypt_logs.py --job signed|adhoc --log-dir DIR --encrypted-dir DIR --secrets-root DIR
Exit status: 0 whether or not a log was encrypted (the job has already
failed; the public line says which), 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "encrypted-log"))
import encrypted_log  # noqa: E402

#: The private logs, in the order the action writes them; any other *.log in
#: the directory follows, by name.
PHASE_LOGS = ("install.log", "import.log", "build.log")
#: Text files holding key material, relative to --secrets-root (RUNNER_TEMP):
#: what materialize_signing.sh, the product's keychain import and
#: stage_diagnostics_key.sh write. test_build_dmg.py fails when the staging
#: scripts write a file that is in none of these tables.
SECRET_FILES = (
    "blowhorn-signing/p12-passphrase",
    "blowhorn-signing/api-key.p8",
    "blowhorn-signing/keychain.pass",
    "blowhorn-diagnostics/key",
)
#: Binary key material: matched in its base64 forms (one line, and wrapped at
#: 64 and 76 columns), the only way it could reach a text log.
BINARY_SECRET_FILES = ("blowhorn-signing/developer-id.p12",)
#: Staged files deliberately not matched, and why.
UNMATCHED_FILES = {
    "blowhorn-signing/env.sh": "file paths and Apple's public identifiers, which signed binaries carry anyway",
    "blowhorn-signing/github.env": "the same values as env.sh",
    "blowhorn-signing/ci-signing.keychain-db": "a binary keychain locked with keychain.pass, which is matched",
}
#: The shortest value matched. A shorter secret would match unrelated lines,
#: so it refuses the upload rather than redact by guess.
MIN_SECRET_LEN = 8
REMOVED = b"[build-dmg: line removed before encryption: it held a staged secret value]"


class TooShort(Exception):
    """A staged secret too short to redact without guessing."""


def _check(value: bytes) -> bytes:
    if len(value) < MIN_SECRET_LEN:
        raise TooShort
    return value


def secret_needles(root: Path) -> set[bytes]:
    """Every byte string whose presence in a log line means that line holds a staged secret."""
    needles: set[bytes] = set()
    for rel in SECRET_FILES:
        path = root / rel
        if not path.is_file():
            continue
        value = path.read_bytes().strip()
        if not value:
            continue
        needles.add(_check(value))
        lines = [line.strip() for line in value.splitlines() if line.strip()]
        if len(lines) > 1:
            # A PEM key: each body line, and the body unwrapped onto one line.
            needles.update(line for line in lines if len(line) >= MIN_SECRET_LEN)
            body = b"".join(line for line in lines if not line.startswith(b"-----"))
            if body:
                needles.add(_check(body))
        if rel == "blowhorn-diagnostics/key" and b"." in value:
            # key_id.secret: the secret half alone is key material too.
            needles.add(_check(value.split(b".", 1)[1]))
    for rel in BINARY_SECRET_FILES:
        path = root / rel
        if not path.is_file():
            continue
        data = path.read_bytes()
        if not data:
            continue
        encoded = _check(base64.b64encode(data))
        needles.add(encoded)
        for width in (64, 76):
            needles.update(chunk for chunk in (encoded[i:i + width] for i in range(0, len(encoded), width))
                           if len(chunk) >= MIN_SECRET_LEN)
    return needles


def redact(data: bytes, needles: set[bytes]) -> tuple[bytes, int]:
    """*data* with every line that holds a needle replaced by REMOVED, and how many were."""
    if not needles:
        return data, 0
    # One alternation, longest first, so a build log of many lines is scanned once per line.
    pattern = re.compile(b"|".join(re.escape(n) for n in sorted(needles, key=len, reverse=True)))
    kept, removed = [], 0
    for line in data.split(b"\n"):
        if pattern.search(line):
            kept.append(REMOVED)
            removed += 1
        else:
            kept.append(line)
    return b"\n".join(kept), removed


def phase_logs(log_dir: Path) -> list[Path]:
    """The private logs that exist, in phase order."""
    if not log_dir.is_dir():
        return []
    known = [log_dir / name for name in PHASE_LOGS if (log_dir / name).is_file()]
    others = sorted(p for p in log_dir.glob("*.log") if p.is_file() and p.name not in PHASE_LOGS)
    return known + others


def encrypt_logs(job: str, log_dir: Path, encrypted_dir: Path, secrets_root: Path, env: dict[str, str],
                 out=sys.stdout) -> bool:
    """Join, redact and encrypt the job's logs; print one fixed line (two when lines were removed)."""
    kind = encrypted_log.BUILD_DMG
    secret_dirs = {(secrets_root / rel).parent for rel in SECRET_FILES + BINARY_SECRET_FILES}
    refusal = encrypted_log.upload_dir_refusal(encrypted_dir, (log_dir, *sorted(secret_dirs)))
    if refusal:
        return encrypted_log.unavailable(refusal, out)
    logs = phase_logs(log_dir)
    if not logs:
        return encrypted_log.unavailable("no private build log was written before the failure", out)
    try:
        needles = secret_needles(secrets_root)
    except TooShort:
        return encrypted_log.unavailable(
            f"a staged secret is shorter than {MIN_SECRET_LEN} characters, too short to redact safely", out)
    except OSError as exc:
        return encrypted_log.unavailable(f"a staged secret could not be read: {type(exc).__name__}", out)
    parts, removed = [], 0
    for log in logs:
        text, count = redact(log.read_bytes(), needles)
        removed += count
        parts.append(b"===== " + log.name.encode() + b" =====\n" + text + (b"" if text.endswith(b"\n") else b"\n"))
    if removed:
        print(f"Encrypted log: removed {removed} line(s) holding a staged secret value before encryption.",
              file=out, flush=True)
    return encrypted_log.encrypt(b"".join(parts), kind, job, encrypted_dir, env, out=out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--job", required=True, choices=encrypted_log.BUILD_DMG.names)
    parser.add_argument("--log-dir", required=True, type=Path, help="the private logs (RUNNER_TEMP/build-dmg)")
    parser.add_argument("--encrypted-dir", required=True, type=Path, help="the upload directory, ciphertext only")
    parser.add_argument("--secrets-root", required=True, type=Path,
                        help="where the signed job staged its secrets (RUNNER_TEMP)")
    args = parser.parse_args(argv)
    encrypt_logs(args.job, args.log_dir, args.encrypted_dir, args.secrets_root, dict(os.environ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
