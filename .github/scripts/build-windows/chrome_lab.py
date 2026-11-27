#!/usr/bin/env python3
"""Does the Blowhorn Chrome extension reach its native host on Windows? Run on the Windows runner.

Installs a published preview installer silently into a throwaway folder, registers the native host
for the runner's user (`chrome extension-install`), starts installed Google Chrome on a throwaway
`--user-data-dir` with the unpacked extension folder the installer ships, and looks for the host
program Chrome starts when the extension's worker connects (`chrome.runtime.connectNative`). Then it
stops Chrome, removes the registry entry and uninstalls.

Chrome 137+ only takes an unpacked extension over `--remote-debugging-pipe` with
`--enable-unsafe-extension-debugging` (`Extensions.loadUnpacked`), so this speaks the DevTools pipe
protocol itself: UTF-8 JSON messages, each ended by a NUL byte, over two inheritable handles named
by `--remote-debugging-io-pipes=<read>,<write>`, the Windows form of Linux's fds 3 and 4.

This site is public and the product is private: each check prints a fixed label and ok or failed, and
at most Chrome's own one-line DevTools error. Nothing the product prints is echoed. It never opens
or signs in to any website: Chrome stays on about:blank in a profile that is deleted afterwards.

Usage: chrome_lab.py <installer.exe>
"""

import json
import msvcrt
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHROME = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Google" / "Chrome" / "Application" / "chrome.exe"
HOST_KEY = r"HKCU\Software\Google\Chrome\NativeMessagingHosts\com.blowhorn.chrome_extension"
HOST_PROGRAM = "blowhorn-host.exe"
SERVICE_TASK = "ai.blowhorn.service"
TIMEOUT = 300
HOST_WAIT_S = 45


def say(label, ok, why=""):
    print(f"lab: {label}: {'ok' if ok else 'failed'}{f' ({why})' if why and not ok else ''}", flush=True)
    return ok


def run(argv, env=None):
    try:
        return subprocess.run(argv, env=env, capture_output=True, text=True, timeout=TIMEOUT, check=False, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None


class Pipe:
    """The DevTools pipe to a Chrome started by `start`."""

    def __init__(self, argv):
        to_chrome_r, self.to_chrome_w = os.pipe()
        self.from_chrome_r, from_chrome_w = os.pipe()
        theirs = [msvcrt.get_osfhandle(to_chrome_r), msvcrt.get_osfhandle(from_chrome_w)]
        for handle in theirs:
            os.set_handle_inheritable(handle, True)
        startup = subprocess.STARTUPINFO(lpAttributeList={"handle_list": theirs})
        self.proc = subprocess.Popen(
            argv + [f"--remote-debugging-io-pipes={theirs[0]},{theirs[1]}"],
            startupinfo=startup,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.close(to_chrome_r)
        os.close(from_chrome_w)
        self.buffer = b""
        self.next_id = 0

    def call(self, method, params=None, timeout=30):
        self.next_id += 1
        want = self.next_id
        os.write(self.to_chrome_w, json.dumps({"id": want, "method": method, "params": params or {}}).encode() + b"\0")
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            while b"\0" in self.buffer:
                raw, self.buffer = self.buffer.split(b"\0", 1)
                try:
                    message = json.loads(raw)
                except ValueError:
                    continue
                if message.get("id") == want:
                    return message
            chunk = os.read(self.from_chrome_r, 65536)
            if not chunk:
                return None
            self.buffer += chunk
        return None

    def stop(self):
        run(["taskkill", "/F", "/T", "/PID", str(self.proc.pid)])
        for fd in (self.to_chrome_w, self.from_chrome_r):
            try:
                os.close(fd)
            except OSError:
                pass


def service_task():
    """The name of the per-user service task (its name carries the user's id after the label), or None."""
    listed = run(["schtasks", "/Query", "/FO", "CSV", "/NH"])
    for line in listed.stdout.splitlines() if listed else []:
        name = line.split(",")[0].strip('"')
        if SERVICE_TASK in name:
            return name
    return None


def screenshot(name):
    """The whole screen to `name` (PNG), by PowerShell and System.Drawing; the lab shows only Blowhorn's own window."""
    script = (
        "Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
        "$b=[System.Windows.Forms.SystemInformation]::VirtualScreen;"
        "$bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height;"
        "$g=[System.Drawing.Graphics]::FromImage($bmp);"
        "$g.CopyFromScreen($b.Left,$b.Top,0,0,$bmp.Size);"
        f"$bmp.Save('{name}');"
    )
    done = run(["powershell", "-NoProfile", "-Command", script])
    return bool(done and done.returncode == 0 and Path(name).is_file())


def app_windows():
    """Titles of the visible top-level windows of the app (a bare count and the titles it shows)."""
    done = run(["powershell", "-NoProfile", "-Command", "Get-Process -Name Blowhorn -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle } | ForEach-Object { $_.MainWindowTitle }"])
    return [line.strip() for line in (done.stdout.splitlines() if done else []) if line.strip()]


def host_running():
    done = run(["tasklist", "/FI", f"IMAGENAME eq {HOST_PROGRAM}", "/NH"])
    return bool(done and HOST_PROGRAM.lower() in done.stdout.lower())


def main(installer):
    root = Path(tempfile.mkdtemp(prefix="blowhorn-lab-"))
    app = root / "app"
    profile = root / "chrome-profile"
    app.mkdir()
    profile.mkdir()
    ok = say("chrome installed", CHROME.is_file())
    installed = run([installer, "/S", f"/D={app}"])
    ok &= say("install", installed is not None and installed.returncode == 0, "no result" if installed is None else f"exit {installed.returncode}")
    engine = app / "resources" / "engine" / "bin" / "blowhorn.exe"
    extension = app / "resources" / "engine" / "extension"
    ok &= say("extension folder shipped", (extension / "manifest.json").is_file())
    if not (ok and engine.is_file()):
        return 1
    # The installed app on its own: does it register the native host by itself shortly after it starts?
    # (Before any explicit registration, so only the app can have written the key.)
    app_exe = next(iter(app.glob("Blowhorn.exe")), None)
    if app_exe is not None:
        run(["reg", "delete", HOST_KEY, "/f"])
        launched = subprocess.Popen([str(app_exe)], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        key_seen = False
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline and not key_seen:
            time.sleep(4)
            done = run(["reg", "query", HOST_KEY, "/ve"])
            key_seen = bool(done and done.returncode == 0)
        say("the app registered the native host by itself", key_seen)
        # The app also sets the background service's per-user task (start at sign-in); give it a minute more.
        task_name = None
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline and task_name is None:
            task_name = service_task()
            if task_name is None:
                time.sleep(4)
        say("the app set the background service task by itself", task_name is not None)
        titles = app_windows()
        say("the app shows a window", bool(titles))
        print("lab: window titles:", [re.sub(r"[^A-Za-z0-9 .,:'()_-]", "", t)[:60] for t in titles][:3], flush=True)
        shots = os.environ.get("LAB_SCREENSHOT_DIR")
        if shots:
            Path(shots).mkdir(parents=True, exist_ok=True)
            say("screenshot taken", screenshot(str(Path(shots) / "app.png")))
        run(["taskkill", "/F", "/T", "/PID", str(launched.pid)])
        run(["taskkill", "/F", "/IM", "Blowhorn.exe", "/T"])
        run(["reg", "delete", HOST_KEY, "/f"])
        if task_name:
            run(["schtasks", "/Delete", "/TN", task_name, "/F"])
    else:
        say("app executable found", False)
    registered = run([str(engine), "chrome", "extension-install", "--json"])
    ok &= say("host registration", bool(registered and registered.returncode == 0))
    pipe = None
    try:
        pipe = Pipe(
            [
                str(CHROME),
                f"--user-data-dir={profile}",
                "--no-first-run",
                "--no-default-browser-check",
                "--mute-audio",
                "--enable-unsafe-extension-debugging",
                "--remote-debugging-pipe",
                "about:blank",
            ]
        )
        loaded = pipe.call("Extensions.loadUnpacked", {"path": str(extension)})
        error = (loaded or {}).get("error", {}).get("message", "") if loaded else "no answer"
        ok &= say("extension loaded", bool(loaded and "result" in loaded), re.sub(r"[^A-Za-z0-9 .,:'()_-]", "", error)[:160])
        deadline = time.monotonic() + HOST_WAIT_S
        seen = False
        while time.monotonic() < deadline and not seen:
            seen = host_running()
            if not seen:
                time.sleep(2)
        ok &= say("chrome started the native host", seen)
    except OSError as error:
        ok &= say("chrome driven over the pipe", False, type(error).__name__)
    finally:
        if pipe:
            pipe.stop()
        run(["reg", "delete", HOST_KEY, "/f"])
        uninstaller = next(iter(sorted(app.glob("Uninstall*.exe"))), None)
        if uninstaller:
            run([str(uninstaller), "/S", f"_?={app}"])
    print(f"lab: {'all ok' if ok else 'something failed'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: chrome_lab.py <installer.exe>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
