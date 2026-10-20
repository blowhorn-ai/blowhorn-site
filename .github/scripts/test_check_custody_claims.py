#!/usr/bin/env python3
"""Tests for check-custody-claims.py: banned phrases fail, the repo passes.

Run with `make test-scripts` (CI runs it too).
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check-custody-claims.py")
REPO = Path(__file__).resolve().parents[2]


class CheckCustodyClaimsTest(unittest.TestCase):
    def run_check(self, root):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(root)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr

    def write_tree(self, files):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        for name, text in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return tmp, root

    def test_clean_tree_passes(self):
        tmp, root = self.write_tree({
            "content/en/page.md": "LinkedIn, X, Reddit and Hacker News sessions stay in Chrome.",
            "data/roles.json": '{"headline": "You\'re the company\'s voice. Post as you."}',
        })
        with tmp:
            code, out, err = self.run_check(root)
        self.assertEqual(code, 0, err)
        self.assertIn("check-custody-claims:", out)

    def test_banned_phrases_fail(self):
        cases = (
            ("content/en/ai.md", "Your passwords never leave your computer."),
            ("data/roles.json", "You're the company's voice. Keep its keys."),
            ("content/en/x.md", "The keys stay on this laptop."),
        )
        for name, text in cases:
            with self.subTest(name=name):
                tmp, root = self.write_tree({name: text})
                with tmp:
                    code, _out, err = self.run_check(root)
                self.assertEqual(code, 1, err)
                self.assertIn("banned absolute custody phrasing", err)

    def test_layouts_are_not_scanned(self):
        tmp, root = self.write_tree({
            "layouts/home.html": "Your passwords never leave your computer.",
            "content/en/ok.md": "Posts go out from your Mac.",
        })
        with tmp:
            code, _out, err = self.run_check(root)
        self.assertEqual(code, 0, err)

    def test_repository_content_and_data_pass(self):
        code, _out, err = self.run_check(REPO)
        self.assertEqual(code, 0, err)


if __name__ == "__main__":
    unittest.main()
