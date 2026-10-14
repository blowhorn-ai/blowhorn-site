#!/usr/bin/env python3
"""Tests for sync-docs-base-branch.sh: run it in a clone of a throwaway remote.

The docs-sync branch must sit on the open same-repo sync PR's head, and on
origin/master otherwise (a branch left behind by a merged PR is stale; a fork
PR from a branch of the same name is not ours). Real git and jq run; only gh
is a stand-in, answering `gh pr list` from fixture PRs and applying the
script's own --jq filter the way gh does.

Run with `make test-scripts` (CI runs it too).
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("sync-docs-base-branch.sh")

FAKE_GH = """#!/usr/bin/env bash
# gh stand-in: `gh pr list ... --json F --jq EXPR` prints EXPR applied to
# the PRs in $GH_FIXTURE, as gh does; every other call fails.
set -euo pipefail
[ "$1 $2" = "pr list" ] || { echo "unexpected gh call: $*" >&2; exit 1; }
jq_expr=""
while [ $# -gt 0 ]; do
  [ "$1" = "--jq" ] && jq_expr="$2"
  shift
done
printf '%s' "$GH_FIXTURE" | jq -r "$jq_expr"
"""

OWN_OPEN = {"number": 69, "isCrossRepository": False}
FORK_OPEN = {"number": 77, "isCrossRepository": True}


@unittest.skipUnless(shutil.which("git") and shutil.which("jq"), "needs git and jq")
class BaseBranchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        bindir = self.tmp / "bin"
        bindir.mkdir()
        gh = bindir / "gh"
        gh.write_text(FAKE_GH, encoding="utf-8")
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
        }
        self.env.pop("GITHUB_OUTPUT", None)
        self.origin = self.tmp / "origin.git"
        self.git(self.tmp, "init", "-q", "--bare", "-b", "master", str(self.origin))
        seed = self.clone("seed")
        self.master = self.commit(seed, "master")
        self.git(seed, "push", "-q", "origin", "master")

    def git(self, cwd, *args):
        return subprocess.run(
            ["git", *args], cwd=cwd, env=self.env, check=True,
            capture_output=True, text=True,
        ).stdout.strip()

    def clone(self, name):
        path = self.tmp / name
        self.git(self.tmp, "clone", "-q", str(self.origin), str(path))
        return path

    def commit(self, repo, message):
        self.git(repo, "commit", "-q", "--allow-empty", "-m", message)
        return self.git(repo, "rev-parse", "HEAD")

    def push_docs_sync(self, name, message):
        """Put a docs-sync commit on origin, as an earlier sync did."""
        repo = self.clone(name)
        self.git(repo, "checkout", "-q", "-B", "docs-sync", "origin/master")
        sha = self.commit(repo, message)
        self.git(repo, "push", "-q", "-f", "origin", "docs-sync")
        return sha

    def run_base(self, prs):
        """Run the script in a fresh job checkout; return (checkout, open_pr)."""
        job = self.clone("job")
        output = self.tmp / "github_output"
        env = {**self.env, "GH_FIXTURE": json.dumps(prs), "GITHUB_OUTPUT": str(output)}
        subprocess.run(
            [str(SCRIPT), "docs-sync"], cwd=job, env=env, check=True,
            capture_output=True, text=True,
        )
        lines = output.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1, lines)
        key, _, value = lines[0].partition("=")
        self.assertEqual(key, "open_pr")
        self.assertEqual(self.git(job, "symbolic-ref", "--short", "HEAD"), "docs-sync")
        return job, value

    def test_open_pr_builds_on_its_branch(self):
        head = self.push_docs_sync("earlier", "docs: sync from v1")
        job, open_pr = self.run_base([OWN_OPEN])
        self.assertEqual(open_pr, "69")
        self.assertEqual(self.git(job, "rev-parse", "HEAD"), head)

    def test_branch_left_by_merged_pr_restarts_from_master(self):
        # gh lists open PRs only, so a merged sync PR leaves the list empty.
        self.push_docs_sync("earlier", "docs: sync from v1 (pre-squash)")
        job, open_pr = self.run_base([])
        self.assertEqual(open_pr, "")
        self.assertEqual(self.git(job, "rev-parse", "HEAD"), self.master)

    def test_fork_pr_with_the_same_branch_name_is_ignored(self):
        self.push_docs_sync("earlier", "docs: sync from v1 (pre-squash)")
        job, open_pr = self.run_base([FORK_OPEN])
        self.assertEqual(open_pr, "")
        self.assertEqual(self.git(job, "rev-parse", "HEAD"), self.master)

    def test_own_pr_is_picked_over_a_fork_pr(self):
        head = self.push_docs_sync("earlier", "docs: sync from v1")
        job, open_pr = self.run_base([FORK_OPEN, OWN_OPEN])
        self.assertEqual(open_pr, "69")
        self.assertEqual(self.git(job, "rev-parse", "HEAD"), head)

    def test_first_sync_starts_from_master(self):
        job, open_pr = self.run_base([])
        self.assertEqual(open_pr, "")
        self.assertEqual(self.git(job, "rev-parse", "HEAD"), self.master)

    # sync-docs.yml pushes with --force-with-lease, which needs the script to
    # leave origin/docs-sync at what it saw.
    PUSH = ["git", "push", "-q", "--force-with-lease", "origin", "docs-sync"]

    def test_lease_replaces_a_stale_branch(self):
        self.push_docs_sync("earlier", "docs: sync from v1 (pre-squash)")
        job, _ = self.run_base([])
        new = self.commit(job, "docs: sync from v2")
        subprocess.run(self.PUSH, cwd=job, env=self.env, check=True, capture_output=True)
        self.assertEqual(self.git(job, "ls-remote", "origin", "docs-sync").split()[0], new)
        self.assertEqual(self.git(job, "rev-parse", "HEAD~1"), self.master)

    def test_lease_rejects_a_concurrent_push(self):
        self.push_docs_sync("earlier", "docs: sync from v1 (pre-squash)")
        job, _ = self.run_base([])
        self.commit(job, "docs: sync from v2")
        racer = self.push_docs_sync("racer", "concurrent push")
        result = subprocess.run(self.PUSH, cwd=job, env=self.env, capture_output=True)
        self.assertNotEqual(result.returncode, 0, "the lease must refuse to overwrite it")
        self.assertEqual(self.git(job, "ls-remote", "origin", "docs-sync").split()[0], racer)

if __name__ == "__main__":
    unittest.main()
