#!/usr/bin/env python3
"""Tests for the build-dmg payload, manifest, checkout guard and public log."""

import importlib.util
import io
import json
import os
import re
import shlex
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE / "build-dmg"))
import checkout_guard  # noqa: E402
import require_signed_ref  # noqa: E402
import manifest as manifest_mod  # noqa: E402
import payload as payload_mod  # noqa: E402

import timed_run  # noqa: E402

real_popen = timed_run.subprocess.Popen

SPEC = importlib.util.spec_from_file_location("build_dmg_run", HERE / "build-dmg" / "run_build.py")
run_build = importlib.util.module_from_spec(SPEC)
sys.modules["build_dmg_run"] = run_build
SPEC.loader.exec_module(run_build)

REF = "0123456789abcdef0123456789abcdef01234567"
SHA = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
SECRET = "private source token=hunter2 and a stack trace"


class PayloadTest(unittest.TestCase):
    def test_accepts_a_complete_payload(self):
        parsed = payload_mod.parse_inputs(REF, "2.14.1", "adhoc")
        self.assertEqual(parsed["event_type"], "build-dmg")
        self.assertEqual(parsed["client_payload"]["mode"], "adhoc")

    def test_refuses_a_short_sha_a_leading_v_and_an_unknown_mode(self):
        with self.assertRaises(payload_mod.PayloadError):
            payload_mod.parse_inputs("abc", "2.14.1", "adhoc")
        with self.assertRaises(payload_mod.PayloadError):
            payload_mod.parse_inputs(REF, "v2.14.1", "adhoc")
        with self.assertRaises(payload_mod.PayloadError):
            payload_mod.parse_inputs(REF, "2.14.1", "signed")


class ManifestTest(unittest.TestCase):
    def test_accepts_a_complete_manifest(self):
        data = {
            "version": "2.14.1",
            "ref": REF,
            "signing_mode": "developer-id",
            "sha256": SHA,
            "size_bytes": 12,
            "dmg_name": "Blowhorn-2.14.1-universal.dmg",
        }
        self.assertEqual(manifest_mod.parse_manifest(data), data)
        self.assertEqual(manifest_mod.parse_manifest(json.dumps(data)), data)

    def test_refuses_extra_fields_and_a_zero_size(self):
        base = {
            "version": "2.14.1",
            "ref": REF,
            "signing_mode": "adhoc",
            "sha256": SHA,
            "size_bytes": 12,
            "dmg_name": "Blowhorn-2.14.1-universal.dmg",
        }
        with self.assertRaises(manifest_mod.ManifestError):
            manifest_mod.parse_manifest({**base, "extra": 1})
        with self.assertRaises(manifest_mod.ManifestError):
            manifest_mod.parse_manifest({**base, "size_bytes": 0})


class CheckoutGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.product = Path(self.tmp.name) / "product"
        self.product.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_ok_when_internal_paths_are_absent(self):
        (self.product / "desktop").mkdir()
        (self.product / "release").mkdir()
        (self.product / "release" / "internal-paths.txt").write_text("release/signing/\ninternal/\n")
        self.assertEqual(checkout_guard.main([str(self.product)]), 0)

    def test_refuses_a_signing_tree(self):
        signing = self.product / "release" / "signing"
        signing.mkdir(parents=True)
        (signing / "README.md").write_text("no")
        buf = io.StringIO()
        with mock.patch("sys.stderr", buf):
            status = checkout_guard.main([str(self.product)])
        self.assertEqual(status, 1)
        self.assertIn("release/signing/", buf.getvalue())
        self.assertNotIn("no", buf.getvalue())  # never print the file contents
        self.assertFalse(signing.exists())

    def test_other_internal_paths_are_refused_without_naming_them(self):
        hidden = self.product / "internal"
        hidden.mkdir()
        (hidden / "secret.md").write_text("no")
        (self.product / "release").mkdir()
        (self.product / "release" / "internal-paths.txt").write_text("internal/\n")
        buf = io.StringIO()
        with mock.patch("sys.stderr", buf):
            status = checkout_guard.main([str(self.product)])
        self.assertEqual(status, 1)
        self.assertIn("1 internal path(s)", buf.getvalue())
        self.assertNotIn("internal/", buf.getvalue())
        self.assertNotIn("secret.md", buf.getvalue())
        self.assertFalse(hidden.exists())

    def test_rejects_parent_directory_entries_in_internal_paths(self):
        (self.product / "release").mkdir()
        (self.product / "release" / "internal-paths.txt").write_text("../etc/\n")
        with self.assertRaises(SystemExit):
            checkout_guard.parse_internal_paths((self.product / "release" / "internal-paths.txt").read_text())

    def test_excludes_start_with_signing(self):
        paths = checkout_guard.read_excludes()
        self.assertEqual(paths[0], "release/signing/")


class RunBuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.product = Path(self.tmp.name) / "product"
        desktop = self.product / "desktop" / "scripts"
        desktop.mkdir(parents=True)
        (desktop / "release-mac.mjs").write_text("// stub\n")
        self.log = Path(self.tmp.name) / "private" / "build.log"

    def tearDown(self):
        self.tmp.cleanup()

    def _main(self, popen, *extra):
        buf = io.StringIO()
        with mock.patch.object(timed_run.subprocess, "Popen", popen), mock.patch("sys.stdout", buf):
            status = run_build.main([
                "--product", str(self.product),
                "--log", str(self.log),
                "--version", "2.14.1",
                "--mode", "adhoc",
                *extra,
            ])
        return status, buf.getvalue()

    def test_a_failure_does_not_print_private_output(self):
        def popen(cmd, cwd, env, stdout, stderr, start_new_session):
            return real_popen([sys.executable, "-c", f"print({SECRET!r}); raise SystemExit(1)"], stdout=stdout, stderr=stderr, start_new_session=start_new_session)

        status, out = self._main(popen)
        self.assertEqual(status, 1)
        self.assertIn("build-dmg: failed (exit 1", out)
        self.assertNotIn("hunter2", out)
        self.assertIn(SECRET, self.log.read_text())

    def test_progress_lines_reach_stdout_and_nothing_else_does(self):
        script = (
            "print('==> dmg'); print('Submission ID received');"
            "print('  id: 2d8f1c3a-1111-2222-3333-444455556666');"
            "print('  path: /Users/runner/private.dmg');"
            "print('Current status: In Progress...', end='\\r'); print('Current status: Accepted....');"
            f"print({SECRET!r}); raise SystemExit(1)"
        )

        def popen(cmd, cwd, env, stdout, stderr, start_new_session):
            return real_popen([sys.executable, "-c", script], stdout=stdout, stderr=stderr, start_new_session=start_new_session)

        status, out = self._main(popen)
        self.assertEqual(status, 1)
        for expected in ("build: phase dmg", "notarization: submitted", "notarization: submission id 2d8f1c3a-1111-2222-3333-444455556666", "notarization: status In Progress", "notarization: status Accepted"):
            self.assertIn(expected, out)
        self.assertNotIn("private.dmg", out)
        self.assertNotIn("hunter2", out)

    def test_a_hung_build_is_killed_at_its_limit_with_a_clear_message(self):
        def popen(cmd, cwd, env, stdout, stderr, start_new_session):
            return real_popen([sys.executable, "-c", "import time; print('==> engine', flush=True); time.sleep(60)"], stdout=stdout, stderr=stderr, start_new_session=start_new_session)

        status, out = self._main(popen, "--timeout-minutes", "0.02")
        self.assertEqual(status, 124)
        self.assertIn("build: phase engine", out)
        self.assertIn("timed out after", out)
        self.assertIn("build-dmg: failed (timed out", out)

    def test_child_env_drops_github_file_commands(self):
        env = run_build.child_env({"GITHUB_STEP_SUMMARY": "/tmp/sum", "PATH": "/bin", "MAKELEVEL": "1"})
        self.assertNotIn("GITHUB_STEP_SUMMARY", env)
        self.assertNotIn("MAKELEVEL", env)
        self.assertEqual(env["BLOWHORN_BUILD_CLEANUP"], "1")
        self.assertEqual(env["PATH"], "/bin")

    def test_child_env_drops_signing_secrets_and_the_product_token(self):
        env = run_build.child_env({
            "PATH": "/bin",
            "DEVELOPER_ID_P12": "p12",
            "DEVELOPER_ID_P12_PASSPHRASE": "pw",
            "DMG_SOURCE_TOKEN": "tok",
            "INPUT_PRODUCT_TOKEN": "tok",
            "INPUT_TOKEN": "tok",
            "APPLE_API_KEY": "/tmp/key.p8",
        })
        self.assertNotIn("DEVELOPER_ID_P12", env)
        self.assertNotIn("DEVELOPER_ID_P12_PASSPHRASE", env)
        self.assertNotIn("DMG_SOURCE_TOKEN", env)
        self.assertNotIn("INPUT_PRODUCT_TOKEN", env)
        self.assertNotIn("INPUT_TOKEN", env)
        self.assertEqual(env["APPLE_API_KEY"], "/tmp/key.p8")


class RequireSignedRefTest(unittest.TestCase):
    REF = "0123456789abcdef0123456789abcdef01234567"
    OTHER = "abcdef0123456789abcdef0123456789abcdef01"

    def test_accepts_the_desktop_tag_or_the_temporary_release_ref(self):
        def lookup(_token, name):
            return {"tags/desktop-v2.14.1": self.REF}.get(name)

        self.assertEqual(
            require_signed_ref.require_signed_ref(self.REF, "2.14.1", "t", lookup=lookup),
            "tags/desktop-v2.14.1",
        )

        def lookup_tmp(_token, name):
            return {"releases/desktop-v2.14.1": self.REF}.get(name)

        self.assertEqual(
            require_signed_ref.require_signed_ref(self.REF, "2.14.1", "t", lookup=lookup_tmp),
            "releases/desktop-v2.14.1",
        )

    def test_refuses_a_commit_the_version_refs_do_not_name(self):
        def lookup(_token, name):
            return {"tags/desktop-v2.14.1": self.OTHER}.get(name)

        with self.assertRaises(require_signed_ref.RefError):
            require_signed_ref.require_signed_ref(self.REF, "2.14.1", "t", lookup=lookup)


class SchemaSyncTest(unittest.TestCase):
    def test_schema_files_exist_and_name_the_same_required_fields(self):
        dispatch = json.loads((ROOT / ".github" / "schemas" / "build-dmg-dispatch.schema.json").read_text())
        result = json.loads((ROOT / ".github" / "schemas" / "build-dmg-manifest.schema.json").read_text())
        self.assertEqual(dispatch["properties"]["event_type"]["const"], "build-dmg")
        self.assertEqual(set(result["required"]), {"version", "ref", "signing_mode", "sha256", "size_bytes", "dmg_name"})


def _shell_statements(script):
    statements = []
    pending = ""
    for line in script.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.endswith("\\"):
            pending += stripped[:-1] + " "
            continue
        pending += stripped
        statements.append(pending)
        pending = ""
    if pending:
        statements.append(pending)
    return statements


def _python_argv(script, program):
    found = []
    for statement in _shell_statements(script):
        words = shlex.split(statement, posix=True)
        for index, word in enumerate(words):
            if word == "python3" and index + 1 < len(words) and words[index + 1] == program:
                found.append(words[index + 1:])
    if len(found) != 1:
        raise AssertionError(f"{program} invoked {len(found)} times")
    return found[0]


def _flag(argv, name):
    index = argv.index(name)
    return argv[index + 1]


class PublicLogAuditTest(unittest.TestCase):
    def test_build_dmg_mac_does_not_take_a_product_token(self):
        action = (ROOT / ".github" / "actions" / "build-dmg-mac" / "action.yml").read_text()
        self.assertNotIn("product_token", action)
        self.assertNotIn("INPUT_PRODUCT_TOKEN", action)
        workflow = (ROOT / ".github" / "workflows" / "build-dmg.yml").read_text()
        self.assertNotIn("product_token:", workflow)
        self.assertIn("uses: ./.github/actions/checkout-product", workflow)


    def test_the_mac_action_installs_the_product_toolchain_file_not_a_copied_version(self):
        action = (ROOT / ".github" / "actions" / "build-dmg-mac" / "action.yml").read_text()
        self.assertIn("product/engine/rust/rust-toolchain.toml", action)
        self.assertIn("rustup toolchain install", action)
        self.assertNotIn("1.85", action)
        self.assertNotRegex(action, r"default-toolchain [0-9]")

    def test_the_keychain_import_and_the_build_run_under_a_time_limit(self):
        # Oracle: intent requires a 5-minute keychain import, a 100-minute
        # build, and a cargo cache of registry index, registry cache, and git
        # db keyed on runner OS, arch, the installed toolchain, and Cargo.lock.
        # A 100-minute import, or a target-dir cache path, must fail.
        action = yaml.safe_load((ROOT / ".github" / "actions" / "build-dmg-mac" / "action.yml").read_text())
        steps = action["runs"]["steps"]

        import_step = next(step for step in steps if step.get("name") == "Import the temporary signing keychain")
        self.assertEqual(import_step["if"], "inputs.mode == 'developer-id'")
        import_argv = _python_argv(import_step["run"], ".github/scripts/build-dmg/timed_run.py")
        self.assertEqual(_flag(import_argv, "--timeout-minutes"), "5")
        self.assertEqual(_flag(import_argv, "--label"), "keychain import")
        self.assertNotIn("100", import_argv)

        build_step = next(step for step in steps if step.get("name") == "Build, sign, notarize and verify (output withheld)")
        self.assertNotIn("if", build_step)
        build_argv = _python_argv(build_step["run"], ".github/scripts/build-dmg/run_build.py")
        self.assertEqual(_flag(build_argv, "--timeout-minutes"), "100")

        cache = next(step for step in steps if str(step.get("uses", "")).startswith("actions/cache@"))
        paths = [line.strip() for line in cache["with"]["path"].splitlines() if line.strip()]
        self.assertEqual(paths, [
            "~/.cargo/registry/index",
            "~/.cargo/registry/cache",
            "~/.cargo/git/db",
        ])
        expressions = re.findall(r"\$\{\{\s*(.*?)\s*\}\}", cache["with"]["key"])
        self.assertEqual(expressions, [
            "runner.os",
            "runner.arch",
            "env.RUST_TOOLCHAIN_ID",
            "hashFiles('product/engine/rust/Cargo.lock')",
        ])

    def test_the_desktop_package_is_installed_before_the_build(self):
        # Oracle: release-mac.mjs cannot start without desktop/node_modules
        # (ajv), so the install must come before the build, without lifecycle
        # scripts, under a time limit.
        action = yaml.safe_load((ROOT / ".github" / "actions" / "build-dmg-mac" / "action.yml").read_text())
        names = [step.get("name") for step in action["runs"]["steps"]]
        install = names.index("Install the desktop package")
        self.assertLess(install, names.index("Import the temporary signing keychain"))
        self.assertLess(install, names.index("Build, sign, notarize and verify (output withheld)"))
        argv = _python_argv(action["runs"]["steps"][install]["run"], "../../.github/scripts/build-dmg/timed_run.py")
        self.assertEqual(_flag(argv, "--timeout-minutes"), "10")
        # The statement ends "...; then", so compare the command words only.
        self.assertEqual(argv[argv.index("--") + 1:][:4], ["pnpm", "install", "--frozen-lockfile", "--ignore-scripts;"])

    def test_progress_line_lets_through_only_fixed_vocabulary(self):
        self.assertEqual(timed_run.progress_line("==> remote-dmg"), "phase remote-dmg")
        self.assertEqual(timed_run.progress_line("  status: Invalid"), "notarization: status Invalid")
        for private in ("  path: /tmp/x.dmg", "==> " + "x" * 60, "  id: not-a-uuid", "status: Accepted token=abc", SECRET):
            self.assertIsNone(timed_run.progress_line(private))

    def test_materialize_does_not_write_github_env(self):
        script = (ROOT / ".github" / "scripts" / "build-dmg" / "materialize_signing.sh").read_text()
        self.assertNotIn('>>"$GITHUB_ENV"', script)
        self.assertNotIn("${GITHUB_ENV", script)


if __name__ == "__main__":
    unittest.main()
