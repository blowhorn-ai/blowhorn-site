#!/usr/bin/env python3
"""Tests for the CLI reference regeneration and the docs sync a release starts.

`make docs-cli-reference` runs the product's own generator (Rust xtask, or the older Python script) in its checkout
before the sync copies the pages; `make dmg-sync-docs` starts sync-docs.yml at
the product's release tag after a public release. Both run here against a fake
product checkout and a fake `gh`, so nothing touches GitHub.

Run with `make test-scripts` (CI runs it too).
"""

import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def make(target, env=None, **variables):
    args = ["make", "--no-print-directory", "-s", target] + [f"{k}={v}" for k, v in variables.items()]
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, env={**os.environ, **(env or {})}, timeout=60)


class DocsCliReference(unittest.TestCase):
    def test_runs_the_products_generator_in_its_checkout(self):
        with tempfile.TemporaryDirectory() as product:
            build = Path(product, "release", "scripts", "cli_reference", "build.py")
            build.parent.mkdir(parents=True)
            build.write_text(textwrap.dedent("""\
                import pathlib, sys
                out = pathlib.Path(__file__).resolve().parents[3] / "docs" / "reference" / "cli"
                out.mkdir(parents=True, exist_ok=True)
                (out / "slack.md").write_text("generated with " + " ".join(sys.argv[1:]) + "\\n")
            """))
            result = make("docs-cli-reference", SOURCE_DIR=product)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(Path(product, "docs", "reference", "cli", "slack.md").read_text(), "generated with \n")

    def test_a_failing_generator_fails_the_sync(self):
        with tempfile.TemporaryDirectory() as product:
            build = Path(product, "release", "scripts", "cli_reference", "build.py")
            build.parent.mkdir(parents=True)
            build.write_text("raise SystemExit(1)\n")
            self.assertNotEqual(make("docs-cli-reference", SOURCE_DIR=product).returncode, 0)

    def test_a_ref_with_the_rust_generator_runs_it_and_not_the_python_one(self):
        with tempfile.TemporaryDirectory() as product:
            docs = Path(product, "engine", "rust", "xtask", "src", "docs.rs")
            docs.parent.mkdir(parents=True)
            docs.write_text("// generator\n")
            xtask = Path(product, "tools", "bin", "xtask.sh")
            xtask.parent.mkdir(parents=True)
            xtask.write_text('#!/bin/sh\ncd "$(dirname "$0")/../.."\nmkdir -p docs/reference/cli\necho "rust $*" > docs/reference/cli/slack.md\n')
            xtask.chmod(0o755)
            build = Path(product, "release", "scripts", "cli_reference", "build.py")
            build.parent.mkdir(parents=True)
            build.write_text("raise SystemExit(1)\n")
            result = subprocess.run(["make", "--no-print-directory", "-s", "docs-cli-reference", f"SOURCE_DIR={product}"],
                                    cwd=ROOT, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(Path(product, "docs", "reference", "cli", "slack.md").read_text(), "rust docs cli-reference\n")

    def test_a_ref_without_the_generator_keeps_its_pages(self):
        with tempfile.TemporaryDirectory() as product:
            page = Path(product, "docs", "reference", "cli.md")
            page.parent.mkdir(parents=True)
            page.write_text("hand written\n")
            result = make("docs-cli-reference", SOURCE_DIR=product)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("no ", result.stdout)
            self.assertEqual(page.read_text(), "hand written\n")


class DmgSyncDocs(unittest.TestCase):
    def setUp(self):
        self.bin = tempfile.TemporaryDirectory()
        self.calls = Path(self.bin.name, "calls")
        gh = Path(self.bin.name, "gh")
        gh.write_text(f'#!/bin/sh\necho "$@" >> "{self.calls}"\n')
        gh.chmod(0o755)
        self.env = {"PATH": f"{self.bin.name}:{os.environ['PATH']}", "GH_TOKEN": "test"}

    def tearDown(self):
        self.bin.cleanup()

    def test_a_public_release_starts_the_sync_at_its_product_tag(self):
        result = make("dmg-sync-docs", env={**self.env, "VERSION": "v1.24.0", "DRAFT": "false"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls.read_text(), "workflow run sync-docs.yml -f ref=desktop-v1.24.0\n")

    def test_a_draft_starts_nothing(self):
        result = make("dmg-sync-docs", env={**self.env, "VERSION": "v1.24.0", "DRAFT": "true"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.calls.exists())

    def test_no_version_is_an_error_and_starts_nothing(self):
        env = {k: v for k, v in {**os.environ, **self.env}.items() if k != "VERSION"}
        result = subprocess.run(["make", "-s", "dmg-sync-docs"], cwd=ROOT, capture_output=True, text=True, env=env, timeout=60)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.calls.exists())


if __name__ == "__main__":
    unittest.main()
