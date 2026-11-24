"""Run the product's --build-dmg-only entry and print only a public summary.

Build and tool output goes to a log under RUNNER_TEMP that is never printed,
uploaded or cached. The only stdout is fixed labels, the exit status, the
duration, phase and notarization progress lines that timed_run.progress_line
allows, and (on success) the manifest sha256 and size. Commands run without
the runner's file-command variables. The build is killed after
--timeout-minutes so a hang fails with a clear message before the job times out.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import timed_run  # noqa: E402

FILE_COMMANDS = frozenset({"GITHUB_ENV", "GITHUB_OUTPUT", "GITHUB_PATH", "GITHUB_STATE", "GITHUB_STEP_SUMMARY"})
MAKE_STATE = frozenset({"MAKEFLAGS", "MAKELEVEL", "MFLAGS", "MAKEOVERRIDES"})
# Raw key material and checkout tokens must never reach node, pnpm or cargo.
SECRET_ENV = frozenset({
    "DEVELOPER_ID_P12",
    "DEVELOPER_ID_P12_PASSPHRASE",
    "DMG_SOURCE_TOKEN",
    "INPUT_PRODUCT_TOKEN",
    "INPUT_TOKEN",
    "GH_TOKEN",
    "GITHUB_TOKEN",
})


def child_env(src: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if src is None else src)
    for name in list(env):
        if name in FILE_COMMANDS or name in MAKE_STATE or name in SECRET_ENV:
            env.pop(name, None)
    env["BLOWHORN_BUILD_CLEANUP"] = "1"
    return env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--mode", required=True, choices=("adhoc", "developer-id"))
    parser.add_argument("--timeout-minutes", type=float, default=100.0)
    args = parser.parse_args(argv)

    product = args.product.resolve()
    log = args.log
    log.parent.mkdir(parents=True, exist_ok=True)

    script = product / "desktop" / "scripts" / "release-mac.mjs"
    if not script.is_file():
        print("build-dmg: release-mac.mjs is missing from the product checkout", file=sys.stderr)
        return 1

    cmd = [
        "node",
        str(script),
        "--build-dmg-only",
        "--version",
        args.version,
        "--skip-checks",
    ]
    print(f"build-dmg: starting ({args.mode})", flush=True)
    status, elapsed, timed_out = timed_run.run_logged(
        cmd,
        label="build",
        log=log,
        timeout_s=args.timeout_minutes * 60,
        cwd=product / "desktop",
        env=child_env(),
    )
    if timed_out:
        print(f"build-dmg: failed (timed out after {elapsed}s; the last phase line above shows where). Run the same --build-dmg-only command in a local checkout to see why.", flush=True)
        return status
    if status != 0:
        print(f"build-dmg: failed (exit {status}, {elapsed}s). Run the same --build-dmg-only command in a local checkout to see why.", flush=True)
        return status

    manifest_path = product / "desktop" / "release-prod" / "build-dmg-manifest.json"
    if not manifest_path.is_file():
        print("build-dmg: succeeded but the result manifest is missing", flush=True)
        return 1
    from manifest import parse_manifest

    manifest = parse_manifest(manifest_path.read_text())
    print(
        f"build-dmg: ok ({elapsed}s) sha256 {manifest['sha256']} size {manifest['size_bytes']} {manifest['dmg_name']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
