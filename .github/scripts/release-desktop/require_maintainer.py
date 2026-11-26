"""Refuse a published-release run unless the actor can publish on this repository.

GitHub lets collaborators with write, maintain, or admin publish a release.
This is defense in depth on top of the repository's collaborator policy.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

ALLOWED = frozenset({"admin", "maintain", "write"})
API_VERSION = "2022-11-28"


class MaintainerError(ValueError):
    pass


def permission_url(repo: str, login: str) -> str:
    return f"https://api.github.com/repos/{repo}/collaborators/{login}/permission"


def read_permission(repo: str, login: str, token: str, opener=None) -> str:
    if not repo or "/" not in repo:
        raise MaintainerError("repository is missing")
    if not login:
        raise MaintainerError("actor login is missing")
    if not token:
        raise MaintainerError("a token is needed to check collaborator permission")
    request = urllib.request.Request(
        permission_url(repo, login),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "blowhorn-site-release-desktop",
        },
    )
    open_url = opener or urllib.request.urlopen
    try:
        with open_url(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        # Close the error's response body (it is a file), then drop the error: do
        # not include the request or headers, the token is in the Authorization header.
        code = error.code
        error.close()
        raise MaintainerError(f"could not read collaborator permission (HTTP {code})") from None
    except urllib.error.URLError:
        raise MaintainerError("could not read collaborator permission") from None
    permission = data.get("permission") if isinstance(data, dict) else None
    if not isinstance(permission, str) or not permission:
        raise MaintainerError("collaborator permission response was not a permission name")
    return permission


def require_maintainer(repo: str, login: str, token: str, lookup=None) -> str:
    permission = (lookup or read_permission)(repo, login, token)
    if permission not in ALLOWED:
        raise MaintainerError(
            f"{login} has {permission} on {repo}; publishing a desktop release needs write, maintain, or admin"
        )
    return permission


def main(argv: list[str] | None = None) -> int:
    del argv
    repo = os.environ.get("GITHUB_REPOSITORY") or ""
    login = os.environ.get("RELEASE_ACTOR") or os.environ.get("GITHUB_ACTOR") or ""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    try:
        permission = require_maintainer(repo, login, token)
    except MaintainerError as error:
        print(str(error), file=sys.stderr)
        return 1
    print(f"publisher: ok {login} ({permission})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
