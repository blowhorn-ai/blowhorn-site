#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Drive the shipped Blowhorn CLI's Cloud sign-in end to end, with no browser.

Runs the bundled engine of a Blowhorn release (the same `blowhorn auth ...`
a user runs) against Blowhorn Cloud, and plays the person's part over plain
HTTPS: it opens the authorize URL the CLI prints, fills in Cloud's own email
and password form, follows Hydra's consent and Cloud's callback, answers
Cloud's native sign-in consent page with Allow (releases that sign in with
PKCE), and hands the answer to the CLI's 127.0.0.1 listener, exactly where a
browser would.

    drive.py signin  --engine DIR --cloud URL   # login, status, logout, revoked token refused
    drive.py signup  --engine DIR --cloud URL   # a fresh account through Cloud's sign-up
    drive.py default --engine DIR --cloud URL   # the CLI's default Cloud is URL

The account comes from BLOWHORN_SMOKE_EMAIL and BLOWHORN_SMOKE_PASSWORD.
Every CLI run gets its own config dir, runs there, and never touches a Keychain. Nothing
here prints a password, a token or a cookie.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
from pathlib import Path

try:  # the bundled engine's Python has it; the unit tests do not need it
    import requests
except ImportError:  # pragma: no cover
    requests = None

UA = "blowhorn-cloud-auth-smoke/1"
TIMEOUT = 30
#: Cloud's native client consent page (meshery/schemas v1beta3/token): the
#: CLI's PKCE sign-in lands here once the account is signed in.
NATIVE_AUTHORIZE_PATH = "/api/identity/native/authorize"


class Failure(Exception):
    """One sentence naming what did not work."""


#: Set by `make cloud-auth-smoke` for a release up to 1.24.0, which predates the
#: cloud.blowhorn.ai default and the revoke fix: those two become warnings.
PREDATES_FIXES = "BLOWHORN_PREDATES_CLOUD_FIXES"


def log(msg: str) -> None:
    print(msg, flush=True)


def warn(msg: str) -> None:
    print(f"warn {msg}", flush=True)
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::warning::{msg}", flush=True)


def redact(url: str) -> str:
    """Scheme, host and path only: queries carry challenges, flows and tokens."""
    p = urllib.parse.urlparse(url)
    return f"{p.scheme}://{p.netloc}{p.path}"


# --- the shipped CLI ---------------------------------------------------------

class Cli:
    def __init__(self, engine: Path, cloud: str | None):
        self.engine = engine
        self.dir = Path(tempfile.mkdtemp(prefix="bh-auth-smoke-"))
        env = {k: v for k, v in os.environ.items() if not k.startswith(("BLOWHORN_SMOKE_", "BLOWHORN_CLOUD_"))}
        env.update({"BLOWHORN_CLOUD_CONFIG_DIR": str(self.dir), "BLOWHORN_KEYCHAIN": "0", "BLOWHORN_RUN_SOURCE": "smoke"})
        if cloud:
            env["BLOWHORN_CLOUD_API_BASE"] = cloud
        self.env = env

    def argv(self, *args: str) -> list[str]:
        return [str(self.engine / "bin" / "python"), str(self.engine / "engine" / "blowhorn.py"), *args]

    def run(self, *args: str, timeout: float = 120) -> dict:
        done = subprocess.run(self.argv(*args), env=self.env, cwd=self.dir, capture_output=True, text=True, timeout=timeout, check=False)
        final = trailing_json(done.stdout)
        if final is None:
            raise Failure(f"`blowhorn {' '.join(args)}` exited {done.returncode} with no JSON answer: {done.stderr[-300:]}")
        final["_exit"] = done.returncode
        return final

    def login_args(self) -> list[str]:
        """``auth login`` flags for a browserless run with the answer on 127.0.0.1.

        Releases with ``--redirect`` (up to the provider-token flow) need
        ``--redirect loopback``; the PKCE sign-in always answers on the loopback,
        and ``--json`` alone opens no browser.
        """
        done = subprocess.run(self.argv("auth", "login", "--help"), env=self.env, cwd=self.dir, capture_output=True,
                              text=True, timeout=60, check=False)
        if done.returncode != 0:
            raise Failure(f"`blowhorn auth login --help` exited {done.returncode}: {done.stderr[-300:]}")
        return ["--redirect", "loopback", "--json"] if "--redirect" in done.stdout else ["--json"]

    def start_login(self, *extra: str) -> tuple[subprocess.Popen, str, list[str]]:
        proc = subprocess.Popen(self.argv("auth", "login", *self.login_args(), *extra), env=self.env, cwd=self.dir,
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines: list[str] = []
        threading.Thread(target=lambda: lines.extend(proc.stdout), daemon=True).start()
        deadline = time.monotonic() + 60
        while not lines and proc.poll() is None and time.monotonic() < deadline:
            time.sleep(0.1)
        event = json.loads(lines[0]) if lines else {}
        url = event.get("authorize_url") or ""
        if event.get("event") != "authorize" or not url:
            proc.kill()
            raise Failure(f"auth login printed no authorize line (exit {proc.poll()}): {proc.stderr.read()[-300:] if proc.poll() is not None else ''}")
        return proc, url, lines

    def kept_token(self) -> str:
        return (self.dir / "cloud-token").read_text(encoding="utf-8").strip()

    def kept_token_id(self) -> str:
        """``api_token_id`` from the isolated cloud.yaml (a flat ``key: value`` file)."""
        for line in (self.dir / "cloud.yaml").read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition(":")
            if key.strip() == "api_token_id":
                return value.strip().strip("'\"")
        return ""


def trailing_json(stdout: str):
    start = stdout.find("{\n")
    for candidate in ([stdout[start:]] if start >= 0 else []) + stdout.strip().splitlines()[::-1]:
        try:
            value = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(value, dict):
            return value
    return None


# --- the person's part, over HTTPS -------------------------------------------

def session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = UA
    return s


def walk(s: requests.Session, url: str, *, data=None, headers=None, hops: int = 20) -> str:
    """Follow redirects by hand; stop at the loopback answer or a page. Returns the last URL."""
    method = "POST" if data is not None else "GET"
    for _ in range(hops):
        if url.startswith("http://127.0.0.1"):
            return url
        r = s.request(method, url, data=data, headers=headers, allow_redirects=False, timeout=TIMEOUT)
        method, data, headers = "GET", None, None
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        if urllib.parse.urlparse(url).path.rstrip("/") == "/error" or "error" in q:
            raise Failure(f"Cloud refused at {redact(url)}: {(q.get('error') or ['no message'])[0]}")
        loc = r.headers.get("location")
        if r.status_code in (301, 302, 303, 307, 308) and loc:
            url = urllib.parse.urljoin(url, loc)
            continue
        if r.status_code != 200:
            raise Failure(f"Cloud answered HTTP {r.status_code} at {redact(url)}")
        return url
    raise Failure(f"more than {hops} redirects, last at {redact(url)}")


def origin(url: str) -> str:
    p = urllib.parse.urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def flow_id(url: str) -> str:
    fid = (urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("flow") or [""])[0]
    if not fid:
        raise Failure(f"no Cloud flow on {redact(url)}")
    return fid


def get_flow(s: requests.Session, base: str, kind: str, fid: str) -> dict:
    r = s.get(f"{base}/api/auth/flow", params={"type": kind, "id": fid}, timeout=TIMEOUT)
    if r.status_code != 200:
        raise Failure(f"Cloud's {kind} flow answered HTTP {r.status_code}")
    body = r.json()
    return {"flow": body.get("flow") or {}, "config": body.get("config") or {}}


def nodes(flow: dict) -> dict:
    return {(n.get("attributes") or {}).get("name"): n for n in flow.get("nodes") or []}


def csrf(flow: dict) -> str:
    node = nodes(flow).get("csrf_token")
    if not node:
        raise Failure("Cloud's form carried no CSRF token")
    return node["attributes"]["value"]


def messages(flow: dict) -> list[str]:
    texts = [m.get("text", "") for m in flow.get("messages") or []]
    for n in flow.get("nodes") or []:
        texts += [m.get("text", "") for m in n.get("messages") or []]
    return [t for t in texts if t]


CONSENT_FORM = re.compile(r'<form\b[^>]*\baction="([^"]*)"[^>]*>(.*?)</form>', re.S | re.I)
HIDDEN_INPUT = re.compile(r'<input\b[^>]*>', re.I)
ATTR = re.compile(r'\b(type|name|value)="([^"]*)"', re.I)


def consent_form(page_html: str) -> tuple[str, dict]:
    """The action and hidden fields of Cloud's native consent form (the Allow button submits them as is)."""
    for action, body in CONSENT_FORM.findall(page_html):
        if html.unescape(action) != NATIVE_AUTHORIZE_PATH:
            continue
        fields = {}
        for tag in HIDDEN_INPUT.findall(body):
            attrs = {k.lower(): html.unescape(v) for k, v in ATTR.findall(tag)}
            if attrs.get("type", "").lower() == "hidden" and attrs.get("name"):
                fields[attrs["name"]] = attrs.get("value", "")
        return NATIVE_AUTHORIZE_PATH, fields
    raise Failure("Cloud's native sign-in consent page has no Allow form")


def allow_native_consent(s: requests.Session, page: str) -> str:
    """Choose Allow on Cloud's native consent page at *page*, as the browser would. Returns the loopback URL."""
    base = origin(page)
    shown = s.get(page, timeout=TIMEOUT)  # the page walk stopped at; it is rendered again, unchanged
    if shown.status_code != 200:
        raise Failure(f"Cloud's native sign-in consent page answered HTTP {shown.status_code}")
    action, fields = consent_form(shown.text)
    # Cloud refuses a cross-site post; a browser submitting its own form sends these.
    headers = {"Origin": base, "Referer": page, "Sec-Fetch-Site": "same-origin"}
    answer = walk(s, base + action, data=fields, headers=headers)
    if not answer.startswith("http://127.0.0.1"):
        raise Failure(f"Allow on Cloud's consent page led to {redact(answer)}, not the CLI's 127.0.0.1 listener")
    return answer


def sign_in_with_password(s: requests.Session, authorize_url: str, email: str, password: str) -> str:
    """From the CLI's authorize URL to the answer for its loopback. Returns the loopback URL."""
    page = walk(s, authorize_url)
    base = origin(page)
    if urllib.parse.urlparse(page).path != "/login":
        raise Failure(f"the authorize URL led to {redact(page)}, not Cloud's sign-in page")
    flow = get_flow(s, base, "login", flow_id(page))["flow"]
    if "password" not in nodes(flow):
        raise Failure("Cloud's sign-in page offers no email and password sign-in")
    answer = walk(s, base + flow["action"], data={"csrf_token": csrf(flow), "identifier": email,
                                                  "password": password, "method": "password"})
    if urllib.parse.urlparse(answer).path == NATIVE_AUTHORIZE_PATH:
        log("ok   Cloud signed the account in and showed its native sign-in consent page")
        answer = allow_native_consent(s, answer)
    if not answer.startswith("http://127.0.0.1"):
        again = get_flow(s, base, "login", flow_id(answer))["flow"] if "flow=" in answer else {}
        raise Failure(f"sign-in stopped at {redact(answer)}: {'; '.join(messages(again)) or 'no message'}")
    return answer


# --- the checks ----------------------------------------------------------------

def profile_status(base: str, token: str) -> int:
    return requests.get(f"{base}/api/identity/users/profile", headers={"Authorization": f"Bearer {token}", "User-Agent": UA},
                        timeout=TIMEOUT).status_code


def check_signin(engine: Path, cloud: str, email: str, password: str) -> None:
    cli = Cli(engine, cloud)
    proc, url, lines = cli.start_login()
    if not url.startswith(cloud + "/login?source="):
        proc.kill()
        raise Failure(f"auth login opened {redact(url)}, not {cloud}/login")
    log(f"ok   auth login printed its authorize URL on {redact(url)}")
    try:
        answer = sign_in_with_password(session(), url, email, password)
        log("ok   Cloud signed the account in and answered on 127.0.0.1")
        r = requests.get(answer, timeout=TIMEOUT)  # the browser's last hop: the CLI's own listener
        if r.status_code != 200:
            raise Failure(f"the CLI's loopback listener answered HTTP {r.status_code}")
        proc.wait(120)
    finally:
        if proc.poll() is None:
            proc.kill()
    time.sleep(0.5)
    final = trailing_json("".join(lines)) or {}
    if proc.returncode != 0 or final.get("ok") is not True or final.get("signed_in") is not True:
        raise Failure(f"auth login ended with exit {proc.returncode}: {final.get('error') or 'no final answer'}")
    if final.get("token_store") != "file" or not (cli.dir / "cloud-token").is_file():
        raise Failure("auth login did not keep its token in the isolated config dir")
    if (final.get("display_name") or "").lower() != email.lower():
        raise Failure("auth login named a different account than the one that signed in")
    log(f"ok   auth login kept a Blowhorn API token (entitled: {final.get('entitled')})")

    token = cli.kept_token()
    final_token_id = cli.kept_token_id()
    if profile_status(cloud, token) != 200:
        raise Failure("Cloud refused the kept Blowhorn API token")
    log("ok   the kept API token reads the account's profile")

    status = cli.run("auth", "status", "--json")
    if status["_exit"] != 0 or not (status.get("signed_in") or status.get("token_configured")):
        raise Failure(f"auth status does not see the sign-in: exit {status['_exit']}")
    log("ok   auth status sees the sign-in")

    out = cli.run("auth", "logout", "--json")
    if out["_exit"] != 0 or out.get("ok") is not True:
        raise Failure(f"auth logout failed: {out.get('error') or out['_exit']}")
    if (cli.dir / "cloud-token").exists():
        raise Failure("auth logout left the token file behind")
    code = profile_status(cloud, token)
    if code not in (401, 403) and os.environ.get(PREDATES_FIXES) == "1" and out.get("revoked") is False:
        # Releases up to 1.24.0 send the revoke as `id`, which Cloud ignores.
        # Say so, and revoke the token the way Cloud reads it so none stays live.
        token_id = final_token_id
        gone = requests.delete(f"{cloud}/api/identity/tokens", params={"tokenId": token_id},
                               headers={"Authorization": f"Bearer {token}", "User-Agent": UA}, timeout=TIMEOUT).status_code
        warn("this release's auth logout does not revoke its API token (fixed after 1.24.0); "
             f"revoked it directly (HTTP {gone})")
        code = profile_status(cloud, token)
    if code not in (401, 403):
        raise Failure(f"Cloud still accepts the API token auth logout revoked (HTTP {code})")
    log(f"ok   the API token is revoked (Cloud now answers HTTP {code}) and auth logout forgot it")
    after = cli.run("auth", "status", "--json")
    if after.get("signed_in") is True or after.get("token_configured") is True:
        raise Failure("auth status still reports a sign-in after logout")
    log("ok   auth status reports signed out")


def check_signup(engine: Path, cloud: str, email: str, password: str) -> None:
    cli = Cli(engine, cloud)
    proc, url, _ = cli.start_login("--sign-up")
    try:
        if not url.startswith(cloud + "/"):
            raise Failure(f"auth login --sign-up opened {redact(url)}, not {cloud}")
        log(f"ok   auth login --sign-up printed its authorize URL on {redact(url)}")
        s = session()
        page = walk(s, url)  # the page the person lands on; its Sign up link keeps the return cookie
        base = origin(page)
        reg_page = walk(s, f"{base}/api/auth/flow/init?type=registration")
        if urllib.parse.urlparse(reg_page).path != "/registration":
            raise Failure(f"Cloud's sign-up led to {redact(reg_page)}")
        fid = flow_id(reg_page)
        got = get_flow(s, base, "registration", fid)
        if got["config"].get("recaptchaSiteKey"):
            raise Failure("Cloud's sign-up on this host asks for reCAPTCHA, which no machine can pass")
        flow = got["flow"]
        traits = {"traits.email": email, "traits.name.first_name": "Blowhorn", "traits.name.last_name": "Smoke"}
        missing = [k for k in traits if k not in nodes(flow)]
        if missing:
            raise Failure(f"Cloud's sign-up form no longer asks for {missing}")
        step = walk(s, base + flow["action"], data={"csrf_token": csrf(flow), **traits, "method": "profile"})
        flow = get_flow(s, base, "registration", flow_id(step))["flow"]
        if "password" not in nodes(flow):
            raise Failure(f"Cloud's sign-up did not reach the password step: {'; '.join(messages(flow)) or 'no message'}")
        done = walk(s, base + flow["action"], data={"csrf_token": csrf(flow), **traits, "password": password, "method": "password"})
        if urllib.parse.urlparse(done).path != "/registered":
            after = get_flow(s, base, "registration", flow_id(done))["flow"] if "flow=" in done else {}
            raise Failure(f"Cloud's sign-up stopped at {redact(done)}: {'; '.join(messages(after)) or 'no message'}")
        log("ok   Cloud created the account and showed its registered page")
    finally:
        proc.kill()

    # The new account exists and waits on its emailed code: its password
    # sign-in is sent to Cloud's verification page, whose flow says the code
    # went out, instead of signing in.
    s = session()
    page = walk(s, f"{cloud}/api/auth/flow/init?type=login")
    base = origin(page)
    flow = get_flow(s, base, "login", flow_id(page))["flow"]
    answer = walk(s, base + flow["action"], data={"csrf_token": csrf(flow), "identifier": email, "password": password, "method": "password"})
    if urllib.parse.urlparse(answer).path != "/verification":
        said = "; ".join(messages(get_flow(s, base, "login", flow_id(answer))["flow"])) if "flow=" in answer else ""
        raise Failure(f"the new account's sign-in went to {redact(answer)}, not email verification: {said or 'no message'}")
    verification = get_flow(s, base, "verification", flow_id(answer))["flow"]
    if verification.get("state") != "sent_email":
        raise Failure(f"Cloud's verification flow for the new account is {verification.get('state')!r}, not sent_email")
    log("ok   the new account must verify its email before it can sign in, and Cloud sent the code")


def check_default(engine: Path, cloud: str) -> None:
    out = Cli(engine, None).run("auth", "login", "--dry-run", "--json")
    if out.get("login_url") != cloud + "/login":
        raise Failure(f"the CLI's default Cloud is {out.get('login_url')}, not {cloud}/login")
    log(f"ok   the CLI signs in at {cloud} by default")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("check", choices=("signin", "signup", "default"))
    ap.add_argument("--engine", required=True, type=Path, help="Blowhorn.app/Contents/Resources/engine")
    ap.add_argument("--cloud", default="https://cloud.blowhorn.ai")
    ap.add_argument("--signup-tag", default="", help="suffix for the fresh sign-up address")
    a = ap.parse_args()
    cloud = a.cloud.rstrip("/")
    try:
        if a.check == "default":
            check_default(a.engine, cloud)
            return 0
        email, password = os.environ.get("BLOWHORN_SMOKE_EMAIL", ""), os.environ.get("BLOWHORN_SMOKE_PASSWORD", "")
        if not email or not password:
            raise Failure("set BLOWHORN_SMOKE_EMAIL and BLOWHORN_SMOKE_PASSWORD (Actions secrets)")
        if a.check == "signin":
            check_signin(a.engine, cloud, email, password)
        else:
            local, _, domain = email.partition("@")
            fresh = f"{local.split('+')[0]}+bh-reg-{a.signup_tag or int(time.time())}@{domain}"
            check_signup(a.engine, cloud, fresh, password)
    except Failure as exc:
        print(f"FAIL {exc}", flush=True)
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::error::{exc}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
