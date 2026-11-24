#!/usr/bin/env python3
"""Tests for .github/scripts/publish-dmg/release.sh.

The script always creates a draft. A public stable release is published only
after blowhorn-cli-X.Y.Z-macos-universal.tar.gz and its .sha256 exist on that
draft. These tests drive the script with a stub `gh` on PATH and never talk
to GitHub.
"""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "publish-dmg" / "release.sh"
SHA = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
VERSION = "v1.2.3"
TARBALL = "blowhorn-cli-1.2.3-macos-universal.tar.gz"
SHAFILE = f"{TARBALL}.sha256"
DMG = "Blowhorn-1.2.3-mac-universal.dmg"


STUB_GH = r"""#!/usr/bin/env bash
set -euo pipefail
STATE="${GH_STUB_STATE:?}"
LOG="${GH_STUB_LOG:?}"
printf '%s\n' "$*" >>"$LOG"
cmd="${1:-}"
sub="${2:-}"
if [[ "$cmd" != "release" ]]; then
  echo "unexpected gh $*" >&2
  exit 2
fi
case "$sub" in
  view)
    if [[ ! -f "$STATE/created" ]]; then
      exit 1
    fi
    if [[ "$*" == *"--json"* ]]; then
      jq_prog=""
      prev=""
      for arg in "$@"; do
        if [[ "$prev" == "--jq" ]]; then
          jq_prog="$arg"
        fi
        prev="$arg"
      done
      payload="$(python3 -c '
import json, os
from pathlib import Path
state = Path(os.environ["GH_STUB_STATE"])
assets = json.loads((state / "assets").read_text())
draft = (state / "draft").read_text().strip() == "true"
views = state / "views"
n = int(views.read_text()) if views.exists() else 0
views.write_text(str(n + 1))
after = int(os.environ.get("GH_STUB_TARBALL_AFTER_VIEWS", "9999"))
if n >= after:
    names = {item["name"] for item in assets}
    for extra in os.environ.get("GH_STUB_EXTRA_ASSETS", "").split(","):
        if extra and extra not in names:
            assets.append({"name": extra})
    (state / "assets").write_text(json.dumps(assets))
print(json.dumps({"isDraft": draft, "assets": assets}))
')"
      if [[ -n "$jq_prog" ]]; then
        printf '%s
' "$payload" | jq -r "$jq_prog"
      else
        printf '%s
' "$payload"
      fi
    fi
    exit 0
    ;;
  create)
    if [[ " $* " != *" --draft "* ]]; then
      echo "create must be a draft" >&2
      exit 3
    fi
    mkdir -p "$STATE"
    echo true >"$STATE/draft"
    python3 -c '
import json, os, sys
from pathlib import Path
state = Path(os.environ["GH_STUB_STATE"])
skip = {"release", "create", "v1.2.3", "v1.2.3-beta.1"}
names = []
for arg in sys.argv[1:]:
    if arg.startswith("-") or arg in skip:
        continue
    names.append(Path(arg).name)
state.joinpath("assets").write_text(json.dumps([{"name": n} for n in names]))
' -- "$@"
    echo created >"$STATE/created"
    exit 0
    ;;
  edit)
    if [[ "$*" != *"--draft=false"* ]]; then
      echo "unexpected edit $*" >&2
      exit 3
    fi
    echo false >"$STATE/draft"
    echo edited >"$STATE/published"
    exit 0
    ;;
  *)
    echo "unexpected gh $*" >&2
    exit 2
    ;;
esac
"""


class ReleaseShTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state = self.root / "state"
        self.state.mkdir()
        self.log = self.root / "gh.log"
        self.log.write_text("")
        bindir = self.root / "bin"
        bindir.mkdir()
        stub = bindir / "gh"
        stub.write_text(STUB_GH)
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        dist = self.root / "dist"
        dist.mkdir()
        (dist / DMG).write_text("dmg")
        (dist / "SHA256SUMS.txt").write_text(f"deadbeef  {DMG}\n")
        self.env = {
            **os.environ,
            "PATH": f"{bindir}:{os.environ['PATH']}",
            "GH_TOKEN": "test-token",
            "GH_REPO": "blowhorn-ai/blowhorn-site",
            "VERSION": VERSION,
            "PRERELEASE": "false",
            "DRAFT": "false",
            "GITHUB_SHA": SHA,
            "CLI_TARBALL_WAIT": "4",
            "CLI_TARBALL_POLL": "1",
            "GH_STUB_STATE": str(self.state),
            "GH_STUB_LOG": str(self.log),
            "GH_STUB_EXTRA_ASSETS": f"{TARBALL},{SHAFILE}",
            "GH_STUB_TARBALL_AFTER_VIEWS": "9999",
        }
        self.env.pop("GITHUB_STEP_SUMMARY", None)

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, **env):
        merged = {**self.env, **env}
        return subprocess.run(
            ["bash", str(SCRIPT)],
            cwd=self.root,
            env=merged,
            capture_output=True,
            text=True,
        )

    def gh_log(self) -> str:
        return self.log.read_text()

    def test_a_requested_draft_is_created_and_not_published(self):
        result = self.run_script(DRAFT="true")
        self.assertEqual(result.returncode, 0, result.stderr)
        log = self.gh_log()
        self.assertIn("release create", log)
        self.assertIn("--draft", log)
        self.assertNotIn("--draft=false", log)
        self.assertFalse((self.state / "published").exists())

    def test_a_prerelease_publishes_without_waiting_for_the_tarball(self):
        result = self.run_script(PRERELEASE="true", VERSION="v1.2.3-beta.1")
        self.assertEqual(result.returncode, 0, result.stderr)
        log = self.gh_log()
        self.assertIn("--draft", log)
        self.assertIn("--draft=false", log)
        self.assertTrue((self.state / "published").exists())

    def test_a_public_release_publishes_only_after_the_cli_tarball_is_on_the_draft(self):
        result = self.run_script(GH_STUB_TARBALL_AFTER_VIEWS="1")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        log = self.gh_log()
        create_at = log.find("release create")
        publish_at = log.find("--draft=false")
        self.assertGreater(create_at, -1)
        self.assertGreater(publish_at, create_at)
        self.assertIn(DMG, log)
        self.assertIn("SHA256SUMS.txt", log)
        self.assertTrue((self.state / "published").exists())

    def test_a_public_release_stays_a_draft_when_the_tarball_never_arrives(self):
        result = self.run_script(CLI_TARBALL_WAIT="1", CLI_TARBALL_POLL="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("leaving it a draft", result.stderr + result.stdout)
        self.assertNotIn("--draft=false", self.gh_log())
        self.assertFalse((self.state / "published").exists())
        self.assertEqual((self.state / "draft").read_text().strip(), "true")

    def test_an_existing_release_is_not_overwritten(self):
        (self.state / "created").write_text("yes")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stderr + result.stdout)
        self.assertNotIn("release create", self.gh_log())


if __name__ == "__main__":
    unittest.main()
