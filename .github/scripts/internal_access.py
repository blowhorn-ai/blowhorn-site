#!/usr/bin/env python3
"""Manage the Cloudflare Access application in front of the internal site.

Usage: internal_access.py check|ensure|verify-worker [--config PATH] [--env-out PATH]

  check          Read-only: confirm the API token can read the Zero Trust
                 organization, Access applications and policies, and the
                 Worker's workers.dev setting. Changes nothing.
  ensure         Idempotent: create or update the reusable allow policy and
                 the self-hosted Access application for the hostname in
                 internal-worker/access.json, then read them back and fail
                 unless the application is default-deny with exactly that
                 policy. Writes TEAM_DOMAIN and POLICY_AUD to --env-out
                 (GITHUB_ENV in the workflow) for the Worker deploy.
  verify-worker  Fail unless the Worker's workers.dev and preview URLs are
                 off, so Access cannot be bypassed.

Needs CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID in the environment.
Prints only status lines and Cloudflare API error codes: never a token,
never page content.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.cloudflare.com/client/v4"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_CONFIG = os.path.join(ROOT, "internal-worker", "access.json")
WORKER_CONFIG = os.path.join(ROOT, "internal-worker", "wrangler.json")

# What each call needs, so a 403 names the missing token permission.
PERM_ACCESS_APPS = "Account > Access: Apps and Policies > Edit"
PERM_ACCESS_ORG = "Account > Access: Organizations, Identity Providers, and Groups > Read"
PERM_WORKERS = "Account > Workers Scripts > Edit"


class ApiError(Exception):
    def __init__(self, status, errors, permission):
        self.status = status
        self.errors = errors
        self.permission = permission
        codes = ", ".join(f"{e.get('code')}: {e.get('message')}" for e in errors) or "no error body"
        hint = f" The API token may lack '{permission}'." if status in (401, 403) and permission else ""
        super().__init__(f"Cloudflare API {status} ({codes}).{hint}")


def call(method, path, permission, body=None):
    token = os.environ["CLOUDFLARE_API_TOKEN"]
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f"{API}{path}", data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            payload = json.loads(res.read() or b"{}")
            status = res.status
    except urllib.error.HTTPError as err:
        try:
            payload = json.loads(err.read() or b"{}")
        except ValueError:
            payload = {}
        raise ApiError(err.code, payload.get("errors") or [], permission) from None
    if not payload.get("success", False):
        raise ApiError(status, payload.get("errors") or [], permission)
    return payload


def list_all(path, permission):
    out, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        payload = call("GET", f"{path}{sep}page={page}&per_page=50", permission)
        out.extend(payload.get("result") or [])
        info = payload.get("result_info") or {}
        if not info or page >= int(info.get("total_pages") or 1):
            return out
        page += 1


def load_config(path):
    with open(path) as fh:
        cfg = json.load(fh)
    emails = [e.strip().lower() for e in cfg["allowed_emails"] if e.strip()]
    if not emails:
        sys.exit("internal_access: allowed_emails is empty; refusing to create an Access policy that admits nobody by mistake")
    cfg["allowed_emails"] = sorted(set(emails))
    return cfg


def account():
    return f"/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}"


def team_domain():
    org = call("GET", f"{account()}/access/organizations", PERM_ACCESS_ORG)["result"] or {}
    domain = org.get("auth_domain")
    if not domain:
        sys.exit("internal_access: no Zero Trust organization on this account. Open Zero Trust in the Cloudflare dashboard once to pick a team name (the free plan is enough), then rerun.")
    return domain


def app_hosts(app):
    hosts = [app.get("domain") or ""]
    hosts += app.get("self_hosted_domains") or []
    hosts += [d.get("uri", "") for d in app.get("destinations") or [] if d.get("type", "public") == "public"]
    return {h for h in hosts if h}


def matching_apps(apps, hostname):
    """Applications on the hostname itself or any path or subdomain of it."""
    hits = []
    for app in apps:
        for h in app_hosts(app):
            bare = h.split("/", 1)[0]
            if bare == hostname or bare.endswith("." + hostname) or bare == "*." + hostname:
                hits.append(app)
                break
    return hits


def policy_body(cfg):
    return {
        "name": cfg["policy_name"],
        "decision": "allow",
        "include": [{"email": {"email": e}} for e in cfg["allowed_emails"]],
        "exclude": [],
        "require": [],
        "session_duration": cfg["session_duration"],
    }


def app_body(cfg, policy_id):
    host = cfg["hostname"]
    return {
        "name": cfg["app_name"],
        "type": "self_hosted",
        "domain": host,
        "destinations": [{"type": "public", "uri": host}],
        "session_duration": cfg["session_duration"],
        "app_launcher_visible": False,
        "http_only_cookie_attribute": True,
        "same_site_cookie_attribute": "lax",
        "skip_interstitial": False,
        "policies": [{"id": policy_id, "precedence": 1}],
    }


def ensure(cfg):
    acct = account()
    domain = team_domain()
    print(f"internal_access: Zero Trust team domain found")

    policies = [p for p in list_all(f"{acct}/access/policies", PERM_ACCESS_APPS) if p.get("name") == cfg["policy_name"]]
    if len(policies) > 1:
        sys.exit(f"internal_access: {len(policies)} reusable policies are named '{cfg['policy_name']}'; delete the extras in Zero Trust > Access > Policies")
    if policies:
        policy = call("PUT", f"{acct}/access/policies/{policies[0]['id']}", PERM_ACCESS_APPS, policy_body(cfg))["result"]
        print("internal_access: allow policy updated")
    else:
        policy = call("POST", f"{acct}/access/policies", PERM_ACCESS_APPS, policy_body(cfg))["result"]
        print("internal_access: allow policy created")

    apps = matching_apps(list_all(f"{acct}/access/apps", PERM_ACCESS_APPS), cfg["hostname"])
    exact = [a for a in apps if a.get("domain") == cfg["hostname"] and a.get("type") == "self_hosted"]
    others = [a for a in apps if a not in exact]
    if others:
        # Another application on a path or subdomain could carry a bypass or
        # an Everyone rule and win for its paths. Refuse rather than guess.
        sys.exit(f"internal_access: {len(others)} other Access application(s) cover {cfg['hostname']} or a path under it; remove them so one default-deny application governs the whole hostname")
    if len(exact) > 1:
        sys.exit(f"internal_access: {len(exact)} Access applications exist for {cfg['hostname']}; keep one")
    if exact:
        app = call("PUT", f"{acct}/access/apps/{exact[0]['id']}", PERM_ACCESS_APPS, app_body(cfg, policy["id"]))["result"]
        print("internal_access: Access application updated")
    else:
        app = call("POST", f"{acct}/access/apps", PERM_ACCESS_APPS, app_body(cfg, policy["id"]))["result"]
        print("internal_access: Access application created")

    verify_app(cfg, app["id"], policy["id"])
    return domain, app["aud"]


def verify_app(cfg, app_id, policy_id):
    acct = account()
    app = call("GET", f"{acct}/access/apps/{app_id}", PERM_ACCESS_APPS)["result"]
    problems = []
    if app.get("domain") != cfg["hostname"]:
        problems.append("application domain differs from the configured hostname")
    if app.get("type") != "self_hosted":
        problems.append("application is not self_hosted")
    attached = app.get("policies") or []
    if [p.get("id") for p in attached] != [policy_id]:
        problems.append(f"application has {len(attached)} policies, expected exactly the managed allow policy")
    policy = call("GET", f"{acct}/access/policies/{policy_id}", PERM_ACCESS_APPS)["result"]
    if policy.get("decision") != "allow":
        problems.append("policy decision is not allow")
    if policy.get("exclude") or policy.get("require"):
        problems.append("policy has unexpected exclude or require rules")
    include = policy.get("include") or []
    emails = sorted({(r.get("email") or {}).get("email", "").lower() for r in include})
    if any(set(r) != {"email"} for r in include):
        problems.append("policy includes a rule other than a named email (for example Everyone or a domain)")
    if emails != cfg["allowed_emails"]:
        problems.append("policy emails differ from internal-worker/access.json")
    if not app.get("aud"):
        problems.append("application has no audience tag")
    if problems:
        sys.exit("internal_access: verification failed: " + "; ".join(problems))
    print(f"internal_access: verified: one self-hosted application, default deny, allow list of {len(emails)} named email(s)")


def worker_name():
    with open(WORKER_CONFIG) as fh:
        return json.load(fh)["name"]


def verify_worker():
    name = worker_name()
    sub = call("GET", f"{account()}/workers/scripts/{name}/subdomain", PERM_WORKERS)["result"] or {}
    if sub.get("enabled") or sub.get("previews_enabled"):
        sys.exit(f"internal_access: Worker {name} has workers.dev or preview URLs enabled; Access could be bypassed")
    print(f"internal_access: Worker {name}: workers.dev off, preview URLs off")


def check(cfg):
    acct = account()
    results = []
    probes = [
        ("Zero Trust organization", lambda: team_domain()),
        ("Access applications", lambda: list_all(f"{acct}/access/apps", PERM_ACCESS_APPS)),
        ("Access reusable policies", lambda: list_all(f"{acct}/access/policies", PERM_ACCESS_APPS)),
        ("Workers scripts", lambda: call("GET", f"{acct}/workers/scripts", PERM_WORKERS)),
    ]
    ok = True
    for label, fn in probes:
        try:
            fn()
            results.append(f"ok    {label}")
        except ApiError as err:
            ok = False
            results.append(f"FAIL  {label}: {err}")
        except SystemExit as err:
            ok = False
            results.append(f"FAIL  {label}: {err}")
    print("\n".join(results))
    if not ok:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["check", "ensure", "verify-worker"])
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--env-out", default=os.environ.get("GITHUB_ENV", ""))
    args = ap.parse_args()
    for var in ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"):
        if not os.environ.get(var):
            sys.exit(f"internal_access: {var} is not set")
    cfg = load_config(args.config)
    try:
        if args.command == "check":
            check(cfg)
        elif args.command == "verify-worker":
            verify_worker()
        else:
            domain, aud = ensure(cfg)
            if os.environ.get("GITHUB_ACTIONS") == "true":
                print(f"::add-mask::{aud}")
            if not args.env_out:
                sys.exit("internal_access: pass --env-out (or set GITHUB_ENV) to hand TEAM_DOMAIN and POLICY_AUD to the deploy")
            with open(args.env_out, "a") as fh:
                fh.write(f"TEAM_DOMAIN={domain}\nPOLICY_AUD={aud}\n")
    except ApiError as err:
        sys.exit(f"internal_access: {err}")


if __name__ == "__main__":
    main()
