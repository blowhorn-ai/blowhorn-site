#!/usr/bin/env python3
"""Tests for publish-dmg/pin-download.sh: run it in a clone of a throwaway remote.

After a public desktop release, data/download.json on master must pin the new
version and site.yml must be started so the site redeploys. A draft, a
prerelease, the version already pinned, or an older version change nothing.
Real git and jq run; gh is a stand-in that records its arguments.

Run with `make test-scripts` (CI runs it too).
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("publish-dmg") / "pin-download.sh"
PINNED = '{"$schema":"../schemas/download.schema.json","version":"1.27.3"}'


@unittest.skipUnless(shutil.which("git") and shutil.which("jq"), "needs git and jq")
class PinDownloadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        bindir = self.tmp / "bin"
        bindir.mkdir()
        self.calls = self.tmp / "gh-calls"
        gh = bindir / "gh"
        gh.write_text(f'#!/bin/sh\necho "$@" >> "{self.calls}"\n')
        gh.chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@example.com",
            "GH_TOKEN": "test",
        }
        self.origin = self.tmp / "origin.git"
        self.git(self.tmp, "init", "-q", "--bare", "-b", "master", str(self.origin))
        self.work = self.tmp / "work"
        self.git(self.tmp, "clone", "-q", str(self.origin), str(self.work))
        (self.work / "data").mkdir()
        (self.work / "data" / "download.json").write_text(PINNED)
        self.git(self.work, "add", ".")
        self.git(self.work, "commit", "-q", "-m", "seed")
        self.git(self.work, "push", "-q", "origin", "master")

    def git(self, cwd, *args):
        return subprocess.run(["git", *args], cwd=cwd, env=self.env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def pin(self, version, draft="false", prerelease="false"):
        env = {**self.env, "VERSION": version, "DRAFT": draft, "PRERELEASE": prerelease}
        return subprocess.run([str(SCRIPT)], cwd=self.work, env=env, capture_output=True, text=True, timeout=60)

    def origin_version(self):
        blob = self.git(self.tmp, "--git-dir", str(self.origin), "show", "master:data/download.json")
        return json.loads(blob)["version"]

    def gh_calls(self):
        return self.calls.read_text() if self.calls.exists() else ""

    def test_a_public_release_pins_master_and_redeploys(self):
        result = self.pin("v1.28.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.origin_version(), "1.28.0")
        self.assertEqual(self.gh_calls(), "workflow run site.yml --ref master\n")

    def test_the_file_keeps_its_schema_reference(self):
        self.pin("v1.28.0")
        blob = self.git(self.tmp, "--git-dir", str(self.origin), "show", "master:data/download.json")
        self.assertEqual(json.loads(blob)["$schema"], "../schemas/download.schema.json")

    def test_a_draft_changes_nothing(self):
        self.assertEqual(self.pin("v1.28.0", draft="true").returncode, 0)
        self.assertEqual(self.origin_version(), "1.27.3")
        self.assertEqual(self.gh_calls(), "")

    def test_a_prerelease_changes_nothing(self):
        self.assertEqual(self.pin("v1.28.0-rc.1", prerelease="true").returncode, 0)
        self.assertEqual(self.origin_version(), "1.27.3")
        self.assertEqual(self.gh_calls(), "")

    def test_the_pinned_version_again_is_a_no_op(self):
        result = self.pin("v1.27.3")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("already pins", result.stdout)
        self.assertEqual(self.gh_calls(), "")

    def test_an_older_release_never_moves_the_site_back(self):
        result = self.pin("v1.27.1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.origin_version(), "1.27.3")
        self.assertEqual(self.gh_calls(), "")

    def test_numeric_order_not_string_order(self):
        result = self.pin("v1.100.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.origin_version(), "1.100.0")

    def test_a_master_that_moved_on_is_rebased_onto(self):
        other = self.tmp / "other"
        self.git(self.tmp, "clone", "-q", str(self.origin), str(other))
        (other / "README.md").write_text("later\n")
        self.git(other, "add", ".")
        self.git(other, "commit", "-q", "-m", "later")
        self.git(other, "push", "-q", "origin", "master")
        result = self.pin("v1.28.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.origin_version(), "1.28.0")
        self.git(self.tmp, "--git-dir", str(self.origin), "show", "master:README.md")


if __name__ == "__main__":
    unittest.main()
