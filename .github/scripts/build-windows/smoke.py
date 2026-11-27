#!/usr/bin/env python3
"""Smoke for a built Windows preview installer, run on the Windows runner.

Installs the per-user NSIS installer silently into a throwaway folder, runs the packaged
Rust-only engine with every user folder pointed at throwaway ones, and removes it again.
This site is public and the product is private, so nothing the product prints is ever echoed:
each check reports only a fixed label and ok or failed, and its output is discarded.

What it proves: the installer installs with no prompt, the engine answers `--version`,
`config show` and `platforms capabilities --json` (parsable JSON), and the uninstaller runs.
It also registers the native host as the app does and reads the HKCU value back, and runs the
commands a tester meets first. Chrome loading the extension, the app's own registrations, its
window and the uninstall cleanup are `chrome_lab.py`, which the workflow runs after this.

Usage: smoke.py <installer.exe>
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TIMEOUT = 300
# The native messaging host's registry key under HKEY_CURRENT_USER (Chrome reads it on Windows).
HOST_KEY = r"HKCU\Software\Google\Chrome\NativeMessagingHosts\com.blowhorn.chrome_extension"
# The one line of the engine's own the smoke may repeat: the front door's fixed trace sentence saying
# why it handed a command to Python ("blowhorn: <words> goes to Python: <why>"), switched on by
# BLOWHORN_FRONT_DOOR_TRACE. Nothing else the program prints is ever shown.
HANDOVER = re.compile(
    r"^(blowhorn: [a-z ]{1,40} goes to Python: [A-Za-z0-9 ,.'()=_-]{1,160}"
    r"|The native host was not registered: [A-Za-z0-9 ,.'():_\\/-]{1,200})$"
)


# A Rust panic's own location and message, the one thing a crash (exit 101) may say, kept to a narrow
# alphabet so nothing else the program printed leaves here ("panicked at <file>:<line>:<col>:" and the line after).
PANIC_AT = re.compile(r"^(thread '[A-Za-z0-9_ <>:-]{1,40}'( \(\d+\))? )?panicked at [A-Za-z0-9_./\\:-]{1,160}:\d+:\d+:$")
PANIC_WHY = re.compile(r"^[A-Za-z0-9 ,.'`()_:\\/<>=-]{1,200}$")


def panic_lines(text):
    """The panic's location line and the message line after it, when the program crashed; else nothing."""
    lines = [line.strip() for line in text.splitlines()]
    for at, line in enumerate(lines):
        if PANIC_AT.match(line):
            why = lines[at + 1] if at + 1 < len(lines) and PANIC_WHY.match(lines[at + 1]) else ""
            return line, why
    return None


def handover_line(text):
    """The program's one fixed handover sentence, when it printed one; nothing else of `text` leaves here."""
    return next((line.strip() for line in text.splitlines() if HANDOVER.match(line.strip())), None)


def run(label, argv, env=None, want_json=False, ok_codes=(0,), cwd=None):
    """Run one check; print its label and ok/failed; never print what the program said."""
    try:
        done = subprocess.run(
            argv, env=env, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT, check=False, stdin=subprocess.DEVNULL
        )
        ok = done.returncode in ok_codes
        why = f"exit {done.returncode & 0xFFFFFFFF:#x}"
        handover = handover_line(done.stderr) or handover_line(done.stdout)
        if handover and not ok:
            why += f"; {handover}"
        panic = panic_lines(done.stderr) if done.returncode == 101 else None
        if panic and not ok:
            print(f"smoke: {label}: panic: {panic[0]} {panic[1]}".rstrip())
        if ok and want_json:
            json.loads(done.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError) as error:
        ok = False
        why = type(error).__name__
    # Only the exit status or the exception's class: never what the program printed.
    print(f"smoke: {label}: {'ok' if ok else f'failed ({why})'}")
    return ok


# Words only (no secrets, no ids of anything real): commands the Windows engine answers natively.
SWEEP = [
    ["config", "get", "defaults"],
    ["profile", "list"],
    ["profile", "current"],
    ["profile", "get", "nobody"],
    ["content", "list"],
    ["content", "get", "1"],
    ["content", "posts"],
    ["schedule", "list"],
    ["schedule", "get", "1"],
    ["schedule", "why", "1"],
    ["schedule", "destinations"],
    ["schedule", "fleet"],
    ["org", "members"],
    ["store"],
    ["risk", "show"],
    ["analytics", "activity", "1"],
    ["analytics", "activities", "1"],
    ["analytics", "operations"],
    ["analytics", "history"],
    ["analytics", "pages", "list"],
]


def pause_stands(engine, env, cwd):
    """Whether `schedule status --json` reports this computer paused (a fixed true or false is all that leaves here)."""
    try:
        done = subprocess.run(
            [str(engine), "schedule", "status", "--json"], env=env, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT, check=False, stdin=subprocess.DEVNULL
        )
        return json.loads(done.stdout).get("pause", {}).get("paused") is True
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return False


def main(installer):
    root = Path(tempfile.mkdtemp(prefix="blowhorn-smoke-"))
    app = root / "app"
    home = root / "home"
    for folder in (app, home / "AppData" / "Roaming", home / "AppData" / "Local"):
        folder.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(
        USERPROFILE=str(home),
        HOME=str(home),
        APPDATA=str(home / "AppData" / "Roaming"),
        LOCALAPPDATA=str(home / "AppData" / "Local"),
        BLOWHORN_CLOUD_CONFIG_DIR=str(home / "cloud"),
        BLOWHORN_FRONT_DOOR_TRACE="1",
    )
    results = []
    # NSIS: /S is silent and /D= (last, unquoted) is the install folder.
    results.append(run("install", [installer, "/S", f"/D={app}"], env))
    engine = app / "resources" / "engine" / "bin" / "blowhorn.exe"
    present = engine.is_file() and (app / "resources" / "engine" / "RUST_ENGINE").is_file()
    print(f"smoke: engine present: {'ok' if present else 'failed'}")
    results.append(present)
    if present:
        results.append(run("engine --version", [str(engine), "--version"], env))
        results.append(run("config show", [str(engine), "config", "show"], env))
        results.append(run("platforms capabilities", [str(engine), "platforms", "capabilities", "--json"], env, True))
        # What a tester runs first, with no account: each answers on the Windows engine with no sign-in
        # and no network, and fails the build if it stops doing so.
        results.append(run("config path", [str(engine), "config", "path"], env))
        # Signed out, the engine answers `ok: false` as JSON and exits 3 (a named cause): that is the answer.
        results.append(run("auth status (offline, signed out)", [str(engine), "auth", "status", "--offline", "--json"], env, True, (3,)))
        results.append(run("desktop activity kinds", [str(engine), "desktop", "activity-kinds", "--json"], env, True))
        results.append(run("risk grid (signed out)", [str(engine), "risk", "grid", "--json"], env, True, (3,)))
        results.append(run("service status", [str(engine), "service", "status", "--json"], env, True))
        # What the app runs when a person presses Sign in, as a dry run: the engine names where it would send them
        # and starts no browser and no listener; and the matching sign-out, which removes nothing in a dry run.
        results.append(run("sign-in (dry run)", [str(engine), "auth", "login", "--no-browser", "--dry-run", "--json"], env, True))
        results.append(run("sign-out (dry run)", [str(engine), "auth", "logout", "--dry-run", "--json"], env, True))
        # A no-crash sweep over the rest of the commands the Windows engine answers natively: each is run
        # signed out, in a throwaway folder, and may answer or refuse (exit 0 to 3) but must never crash
        # (a Rust panic is exit 101, a fault 0xC0000005). `schedule status` once panicked here for want of a handler.
        sweep = root / "sweep"
        sweep.mkdir(exist_ok=True)
        crashed = []
        for words in SWEEP:
            done = None
            try:
                done = subprocess.run([str(engine), *words, "--json"], env=env, cwd=sweep, capture_output=True, text=True, timeout=TIMEOUT, check=False, stdin=subprocess.DEVNULL)
            except (OSError, subprocess.TimeoutExpired):
                pass
            if done is None or done.returncode not in (0, 1, 2, 3):
                code = "no answer" if done is None else f"exit {done.returncode & 0xFFFFFFFF:#x}"
                crashed.append(f"{' '.join(words)} ({code})")
                panic = panic_lines(done.stderr) if done is not None and done.returncode == 101 else None
                if panic:
                    print(f"smoke: sweep {' '.join(words)}: panic: {panic[0]} {panic[1]}".rstrip())
        print(f"smoke: no-crash sweep of {len(SWEEP)} commands: {'ok' if not crashed else 'failed (' + '; '.join(crashed) + ')'}")
        results.append(not crashed)
        # This computer's own pause - the file the On duty switch writes, in a throwaway working folder: pause,
        # see it paused in `schedule status`, resume. No sign-in is needed for any of the three.
        work = root / "work"
        work.mkdir(exist_ok=True)
        results.append(run("schedule pause", [str(engine), "schedule", "pause", "--json"], env, True, cwd=work))
        results.append(run("schedule status sees the pause", [str(engine), "schedule", "status", "--json"], env, True, cwd=work) and pause_stands(engine, env, work))
        results.append(run("schedule resume", [str(engine), "schedule", "resume", "--json"], env, True, cwd=work))
        # The native host registration: write it, read the registry value back, and remove it so the
        # runner's profile is left as found. The key names a throwaway manifest under the smoke's own folder.
        # Called as the desktop app calls it: with the runner's own --json --tee-stdout and --log-dir.
        results.append(run("host registration", [str(engine), "chrome", "extension-install", "--json", "--tee-stdout", "--log-dir", str(root / "logs")], env, True))
        results.append(run("host registry value", ["reg", "query", HOST_KEY, "/ve"], env))
        run("host registry cleanup", ["reg", "delete", HOST_KEY, "/f"], env)
    uninstaller = next(iter(sorted(app.glob("Uninstall*.exe"))), None)
    if uninstaller is None:
        print("smoke: uninstall: failed")
        results.append(False)
    else:
        results.append(run("uninstall", [str(uninstaller), "/S", f"_?={app}"], env))
    failed = results.count(False)
    print(f"smoke: {len(results) - failed} ok, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: smoke.py <installer.exe>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
