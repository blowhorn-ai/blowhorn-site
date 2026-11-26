#!/usr/bin/env python3
"""Tests for the build-dmg payload, manifest, checkout guard and public log."""

import base64
import importlib.util
import io
import json
import os
import re
import shlex
import stat
import subprocess
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
import encrypt_logs  # noqa: E402
import encrypted_log  # noqa: E402  (encrypt_logs put its folder on sys.path)
from test_product_ci_run import _every_file, _fake_age  # noqa: E402

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
        (self.product / "desktop" / "tests").mkdir()
        (self.product / "desktop" / "tests" / "child-teardown.test.ts").write_text("// stub\n")
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

    def test_a_failure_names_the_sub_step_its_exit_and_failing_test_files_only(self):
        script = (
            "print('==> build');"
            "print('    --- pnpm test ---');"
            "print('\\x1b[41m FAIL \\x1b[49m tests/child-teardown.test.ts > childTeardown > a SIGINT stops every child');"
            "print(' FAIL  tests/child-teardown.test.ts > childTeardown > another');"
            "print(' FAIL  tests/../../etc/passwd.ts > x');"
            "print(' FAIL  tests/ghp_secretvalue.test.ts > x');"
            "print('AssertionError: /Users/runner/work/product/desktop/x.ts token=abc');"
            "print('    --- end of pnpm test (failed) ---');"
            "print('    --- end of build the checkout' + chr(39) + 's Rust binaries (passed) ---');"
            "print(\"    $ /Users/runner/setup-pnpm/pnpm exec electron-builder --mac -c.directories.output=/Users/runner/private\");"
            "print('release-mac: pnpm test failed (exit 1)');"
            f"print({SECRET!r}); raise SystemExit(1)"
        )

        def popen(cmd, cwd, env, stdout, stderr, start_new_session):
            return real_popen([sys.executable, "-c", script], stdout=stdout, stderr=stderr, start_new_session=start_new_session)

        status, out = self._main(popen)
        self.assertEqual(status, 1)
        self.assertIn("build: step failed: pnpm test", out)
        self.assertIn("build: failed step: pnpm test (exit 1)", out)
        self.assertEqual(out.count("failing test file: tests/child-teardown.test.ts"), 1)
        for private in ("passwd", "ghp_", "/Users/runner", "token=abc", "hunter2", "SIGINT", "electron-builder", "passed"):
            self.assertNotIn(private, out)

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

    def test_both_mac_jobs_run_on_the_pinned_macos_26_image(self):
        # Oracle: macos-latest migrates between images, and with it the Xcodes
        # the select step below can name; a pinned label keeps them still.
        workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "build-dmg.yml").read_text())
        for job_id in ("build-mac-adhoc", "build-mac-signed"):
            with self.subTest(job=job_id):
                self.assertEqual(workflow["jobs"][job_id]["runs-on"], "macos-26")

    def test_the_icon_compiling_xcode_is_selected_before_anything_builds(self):
        # Oracle: run 45577422514 failed in actool on the image's default Xcode
        # 26.6; the build must run with DEVELOPER_DIR on an exact Xcode path.
        action = yaml.safe_load((ROOT / ".github" / "actions" / "build-dmg-mac" / "action.yml").read_text())
        steps = action["runs"]["steps"]
        names = [step.get("name") for step in steps]
        select = names.index("Select the Xcode that compiles the app icon")
        for later in ("Install the product's pinned Rust toolchain and both macOS targets", "Install the desktop package", "Build, sign, notarize and verify (output withheld)"):
            self.assertLess(select, names.index(later))
        self.assertRegex(steps[select]["env"]["XCODE_APP"], r"^/Applications/Xcode_\d+\.\d+(\.\d+)?\.app$")

    def test_the_xcode_select_step_exports_developer_dir_or_refuses_by_name(self):
        action = yaml.safe_load((ROOT / ".github" / "actions" / "build-dmg-mac" / "action.yml").read_text())
        step = next(s for s in action["runs"]["steps"] if s.get("name") == "Select the Xcode that compiles the app icon")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            app = tmp_path / "Xcode_26.3.app"
            (app / "Contents" / "Developer").mkdir(parents=True)
            bin_dir = tmp_path / "bin"
            bin_dir.mkdir()
            fake = bin_dir / "xcodebuild"
            fake.write_text('#!/bin/sh\necho "Xcode 26.3 from $DEVELOPER_DIR"\necho "Build version 17C529"\n')
            fake.chmod(0o755)
            github_env = tmp_path / "github_env"
            github_env.write_text("")
            base = {"PATH": f"{bin_dir}:/usr/bin:/bin", "GITHUB_ENV": str(github_env)}
            ok = subprocess.run(["bash", "-c", step["run"]], env={**base, "XCODE_APP": str(app)}, capture_output=True, text=True, timeout=30)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertEqual(github_env.read_text(), f"DEVELOPER_DIR={app}/Contents/Developer\n")
            self.assertEqual(ok.stdout, f"build-dmg: Xcode 26.3 from {app}/Contents/Developer selected\n")
            github_env.write_text("")
            missing = subprocess.run(["bash", "-c", step["run"]], env={**base, "XCODE_APP": str(tmp_path / "Xcode_9.9.app")}, capture_output=True, text=True, timeout=30)
            self.assertEqual(missing.returncode, 1)
            self.assertIn("Xcode_9.9.app is not on this runner image", missing.stdout)
            self.assertIn("XCODE_APP in .github/actions/build-dmg-mac/action.yml", missing.stdout)
            self.assertEqual(github_env.read_text(), "")
            fake.write_text("#!/bin/sh\nexit 69\n")
            unusable = subprocess.run(["bash", "-c", step["run"]], env={**base, "XCODE_APP": str(app)}, capture_output=True, text=True, timeout=30)
            self.assertEqual(unusable.returncode, 69)
            self.assertNotIn("selected", unusable.stdout)
            self.assertEqual(github_env.read_text(), "")

    def test_progress_line_lets_through_only_fixed_vocabulary(self):
        self.assertEqual(timed_run.progress_line("==> remote-dmg"), "phase remote-dmg")
        self.assertEqual(timed_run.progress_line("  status: Invalid"), "notarization: status Invalid")
        for private in ("  path: /tmp/x.dmg", "==> " + "x" * 60, "  id: not-a-uuid", "status: Accepted token=abc", SECRET):
            self.assertIsNone(timed_run.progress_line(private))

    def test_progress_line_names_each_failed_sub_step_and_nothing_of_its_output(self):
        cases = {
            "    --- end of pnpm typecheck (failed) ---": "step failed: typecheck",
            "    --- end of pnpm lint (stopped) ---": "step stopped: lint",
            "    --- end of build the checkout's Rust binaries (failed) ---": "step failed: checkout rust build",
            "    --- end of verify reconcile (fixture) (failed) ---": "step failed: fixture check reconcile",
            "release-mac: building the bundled engine failed (exit 1)": "failed step: bundled engine build (exit 1)",
            "release-mac: /Users/runner/pnpm exec electron-builder --mac dir -c.directories.output=/private failed (exit 1)": "failed step: electron-builder (exit 1)",
            "release-mac: signing the DMG failed (exit 1)": "failed step: codesign (exit 1)",
            "release-mac: xcrun notarytool submit /private/x.dmg --key /private/key.p8 --wait failed (exit 69)": "failed step: notarytool (exit 69)",
            "release-mac: /Users/runner/pnpm build failed (exit 2)": "failed step: pnpm build (exit 2)",
            "release-mac: '/Users/runner/pnpm' 'build' failed (exit 2)": "failed step: pnpm build (exit 2)",
            "release-mac: 'pnpm' 'test' failed (exit 1)": "failed step: pnpm test (exit 1)",
            "release-mac: pnpm typecheck failed (exit 2)": "failed step: typecheck (exit 2)",
            "release-mac: something new failed (spawn ENOENT)": "failed step: unrecognized step (no exit code)",
            " FAIL  tests/a/b.test.ts > suite > name": "failing test file: tests/a/b.test.ts",
        }
        known = frozenset({"tests/a/b.test.ts"})
        for line, public in cases.items():
            self.assertEqual(timed_run.progress_line(line, known), public, line)
        for private in ("    --- end of pnpm test (passed) ---", " FAIL  /abs/x.test.ts", " FAIL  tests/../x.test.ts", " FAIL  tests/ghp_secret.test.ts > x", "release-mac: the build produced no /private/x.dmg."):
            self.assertIsNone(timed_run.progress_line(private, known), private)
        # Without the product's inventory no test file name is ever echoed.
        self.assertIsNone(timed_run.progress_line(" FAIL  tests/a/b.test.ts > suite > name"))

    def test_test_files_lists_only_the_products_own_test_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            desktop = Path(tmp)
            (desktop / "tests" / "sub").mkdir(parents=True)
            (desktop / "tests" / "a.test.ts").write_text("")
            (desktop / "tests" / "sub" / "b.test.tsx").write_text("")
            (desktop / "tests" / "fixture.json").write_text("")
            self.assertEqual(timed_run.test_files(desktop), frozenset({"tests/a.test.ts", "tests/sub/b.test.tsx"}))
            self.assertEqual(timed_run.test_files(desktop / "missing"), frozenset())

    def test_materialize_does_not_write_github_env(self):
        script = (ROOT / ".github" / "scripts" / "build-dmg" / "materialize_signing.sh").read_text()
        self.assertNotIn('>>"$GITHUB_ENV"', script)
        self.assertNotIn("${GITHUB_ENV", script)

    def test_child_env_keeps_the_diagnostics_key(self):
        env = run_build.child_env({
            "PATH": "/bin",
            "BLOWHORN_DIAGNOSTICS_KEY": "cdk_example.secret",
            "DEVELOPER_ID_P12": "p12",
        })
        self.assertEqual(env["BLOWHORN_DIAGNOSTICS_KEY"], "cdk_example.secret")
        self.assertNotIn("DEVELOPER_ID_P12", env)

    def test_only_the_signed_job_stages_the_diagnostics_key(self):
        workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "build-dmg.yml").read_text())
        adhoc = workflow["jobs"]["build-mac-adhoc"]
        signed = workflow["jobs"]["build-mac-signed"]
        self.assertNotIn("BLOWHORN_DIAGNOSTICS_KEY", yaml.dump(adhoc))
        self.assertNotIn("env", adhoc)
        self.assertNotIn("env", signed)
        stage = next(step for step in signed["steps"] if step.get("name") == "Stage the diagnostics client key")
        self.assertEqual(stage["env"], {"BLOWHORN_DIAGNOSTICS_KEY": "${{ secrets.BLOWHORN_DIAGNOSTICS_KEY }}"})
        self.assertEqual(stage["run"], ".github/scripts/build-dmg/stage_diagnostics_key.sh")
        mac = next(step for step in signed["steps"] if str(step.get("uses", "")).startswith("./.github/actions/build-dmg-mac"))
        self.assertNotIn("env", mac)
        self.assertNotIn("diagnostics_key", mac.get("with") or {})

    def test_build_dmg_mac_does_not_take_a_diagnostics_key_input(self):
        # A composite-action input would set INPUT_DIAGNOSTICS_KEY on every
        # step, including rustup, setup-node and pnpm install.
        action = yaml.safe_load((ROOT / ".github" / "actions" / "build-dmg-mac" / "action.yml").read_text())
        self.assertNotIn("diagnostics_key", action.get("inputs") or {})
        raw = (ROOT / ".github" / "actions" / "build-dmg-mac" / "action.yml").read_text()
        self.assertNotIn("INPUT_DIAGNOSTICS_KEY", raw)
        build = next(step for step in action["runs"]["steps"] if step.get("name") == "Build, sign, notarize and verify (output withheld)")
        self.assertNotIn("BLOWHORN_DIAGNOSTICS_KEY", (build.get("env") or {}))
        self.assertIn("blowhorn-diagnostics/key", build["run"])
        self.assertIn('export BLOWHORN_DIAGNOSTICS_KEY', build["run"])
        teardown = next(step for step in action["runs"]["steps"] if step.get("name") == "Delete the temporary signing keychain")
        self.assertIn("$RUNNER_TEMP/blowhorn-diagnostics", teardown["run"])

    def test_stage_diagnostics_key_writes_a_private_file_and_not_github_env(self):
        script = ROOT / ".github" / "scripts" / "build-dmg" / "stage_diagnostics_key.sh"
        source = script.read_text()
        self.assertNotIn('>>"$GITHUB_ENV"', source)
        self.assertNotIn("${GITHUB_ENV", source)
        with tempfile.TemporaryDirectory() as tmp:
            env = {
                "RUNNER_TEMP": tmp,
                "BLOWHORN_DIAGNOSTICS_KEY": "cdk_example.secret\n",
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            }
            result = subprocess.run(["bash", str(script)], env=env, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("cdk_example.secret", result.stdout)
            self.assertNotIn("cdk_example.secret", result.stderr)
            path = Path(tmp) / "blowhorn-diagnostics" / "key"
            self.assertEqual(path.read_text(), "cdk_example.secret")
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            missing = subprocess.run(
                ["bash", str(script)],
                env={"RUNNER_TEMP": tmp, "PATH": env["PATH"]},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(missing.returncode, 2)

    def test_cut_desktop_release_passes_the_diagnostics_key_only_to_build_dmg(self):
        # PyYAML treats the workflow key `on` as boolean True, so read the
        # reusable-workflow secrets from the source text.
        called = (ROOT / ".github" / "workflows" / "build-dmg.yml").read_text()
        block = called.split("workflow_call:", 1)[1].split("run-name:", 1)[0]
        self.assertRegex(block, r"BLOWHORN_DIAGNOSTICS_KEY:\s*\n\s+required: false")
        cut = yaml.safe_load((ROOT / ".github" / "workflows" / "cut-desktop-release.yml").read_text())
        build = cut["jobs"]["build"]
        self.assertEqual(build["uses"], "./.github/workflows/build-dmg.yml")
        self.assertEqual(build["with"]["mode"], "developer-id")
        self.assertEqual(
            build["secrets"]["BLOWHORN_DIAGNOSTICS_KEY"],
            "${{ secrets.BLOWHORN_DIAGNOSTICS_KEY }}",
        )
        for name in ("guard", "prepare", "publish"):
            self.assertNotIn("BLOWHORN_DIAGNOSTICS_KEY", yaml.dump(cut["jobs"][name]))


#: The job name the Mac action derives from its mode input; the encrypt step
#: and the upload step must both use exactly this expression.
JOB_EXPR = "${{ inputs.mode == 'developer-id' && 'signed' || 'adhoc' }}"
#: Fake staged secrets. Never real key material.
PASSPHRASE = "pass-phrase-for-the-p12"
P8_LINES = ["-----BEGIN PRIVATE KEY-----",
            "MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgFAKEFAKEFAKEFAKE",
            "FAKEFAKEFAKEFAKEFAKEFAKEFAKEoAoGCCqGSM49AwEHoUQDQgAEFAKEFAKEFAKE",
            "QzKz9Xw1",
            "-----END PRIVATE KEY-----"]
KEYCHAIN_PASS = "0123456789abcdef0123456789abcdef"
DIAG_KEY = "cdk_live01.diagnostics-secret-half"
P12_BYTES = bytes(range(256)) * 3


class EncryptLogsTest(unittest.TestCase):
    """A failed Mac build's logs leave the runner only as age ciphertext, staged secrets removed first."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)  # RUNNER_TEMP
        self.logs = self.root / "build-dmg"
        self.logs.mkdir()
        self.upload = self.root / "build-dmg-encrypted"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.env = {"PATH": os.pathsep.join([str(self.bin), "/usr/bin", "/bin"])}
        self.run_env = mock.patch.dict(os.environ, {"GITHUB_RUN_ATTEMPT": "2", "GITHUB_RUN_ID": "1234"})
        self.run_env.start()

    def tearDown(self):
        self.run_env.stop()
        self.tmp.cleanup()

    def _encrypt(self, job="adhoc", upload=None):
        out = io.StringIO()
        ok = encrypt_logs.encrypt_logs(job, self.logs, upload or self.upload, self.root, self.env, out=out)
        return ok, out.getvalue()

    def _stage_secrets(self):
        signing = self.root / "blowhorn-signing"
        signing.mkdir()
        (signing / "p12-passphrase").write_text(PASSPHRASE)
        (signing / "api-key.p8").write_text("\n".join(P8_LINES) + "\n")
        (signing / "keychain.pass").write_text(KEYCHAIN_PASS + "\n")
        (signing / "developer-id.p12").write_bytes(P12_BYTES)
        (signing / "env.sh").write_text("export APPLE_TEAM_ID=TEAM123456\n")
        diagnostics = self.root / "blowhorn-diagnostics"
        diagnostics.mkdir()
        (diagnostics / "key").write_text(DIAG_KEY)

    def _age_stdin(self):
        return (self.bin / "age-stdin").read_bytes()

    def test_a_failed_build_is_encrypted_in_phase_order_and_only_the_ciphertext_is_written(self):
        _fake_age(self.bin, "encrypt")
        (self.logs / "build.log").write_text(f"==> preflight\n{SECRET}\nrelease-mac: electron-builder failed (exit 1)\n")
        (self.logs / "install.log").write_text("install ok\n")
        ok, out = self._encrypt()
        self.assertTrue(ok)
        argv = json.loads((self.bin / "age-argv.json").read_text())
        self.assertEqual(argv[argv.index("--recipient") + 1], encrypted_log.LOG_RECIPIENT)
        self.assertEqual([p.name for p in _every_file(self.upload)], ["adhoc.log.age"])
        self.assertTrue((self.upload / "adhoc.log.age").read_bytes().startswith(encrypted_log.AGE_HEADER))
        for path in _every_file(self.upload):
            self.assertNotIn(b"hunter2", path.read_bytes())
        plain = self._age_stdin()
        self.assertLess(plain.index(b"===== install.log ====="), plain.index(b"===== build.log ====="))
        self.assertIn(b"hunter2", plain)
        self.assertEqual(out, "Encrypted log: available as artifact build-dmg-adhoc-log-attempt2, readable only "
                              "with the maintainers' key (make build-dmg-log RUN=1234 JOB=adhoc).\n")

    def test_without_age_or_with_a_broken_age_nothing_is_written_for_upload(self):
        (self.logs / "build.log").write_text(SECRET + "\n")
        for behaviour, reason in ((None, "age is not installed on this runner"),
                                  ("fail", "age failed with exit 1"),
                                  ("copy", "age wrote something that is not age ciphertext"),
                                  ("prefix", "age wrote something that is not age ciphertext")):
            with self.subTest(behaviour=behaviour):
                if behaviour:
                    _fake_age(self.bin, behaviour)
                ok, out = self._encrypt()
                self.assertFalse(ok)
                self.assertEqual(_every_file(self.upload), [])
                self.assertEqual(out, f"Encrypted log: none ({reason}).\n")

    def test_every_line_holding_a_staged_secret_is_removed_before_age_sees_it(self):
        self._stage_secrets()
        _fake_age(self.bin, "encrypt")
        encoded = base64.b64encode(P12_BYTES).decode()
        planted = [
            f"security import -P {PASSPHRASE}",
            f"key line {P8_LINES[2]}",
            f"tail {P8_LINES[3]} of the key",
            "".join(P8_LINES[1:4]),
            f"keychain password {KEYCHAIN_PASS}",
            f"header x-diagnostics-key: {DIAG_KEY}",
            "secret half only: " + DIAG_KEY.split(".", 1)[1],
            encoded[64:128],
            encoded[76:152],
            encoded,
        ]
        kept = ["==> package", "signing identity Developer ID Application: Example (TEAM123456)",
                "notarytool submit --key /tmp/blowhorn-signing/api-key.p8 --key-id ABC123"]
        (self.logs / "build.log").write_text("\n".join(kept[:1] + planted + kept[1:]) + "\n")
        (self.logs / "import.log").write_text(f"==> import\n{PASSPHRASE}\n")
        ok, out = self._encrypt(job="signed")
        self.assertTrue(ok)
        plain = self._age_stdin()
        for value in [PASSPHRASE, KEYCHAIN_PASS, DIAG_KEY, DIAG_KEY.split(".", 1)[1], encoded[64:128],
                      encoded[76:152], *P8_LINES[1:4]]:
            self.assertNotIn(value.encode(), plain)
        for line in kept:
            self.assertIn(line.encode(), plain)
        self.assertEqual(plain.count(encrypt_logs.REMOVED), len(planted) + 1)
        self.assertIn(f"Encrypted log: removed {len(planted) + 1} line(s) holding a staged secret value "
                      "before encryption.\n", out)
        self.assertIn("artifact build-dmg-signed-log-attempt2", out)
        for path in _every_file(self.upload):
            self.assertNotIn(PASSPHRASE.encode(), path.read_bytes())

    def test_a_secret_too_short_to_match_safely_uploads_nothing(self):
        self._stage_secrets()
        (self.root / "blowhorn-signing" / "p12-passphrase").write_text("abc")
        _fake_age(self.bin, "encrypt")
        (self.logs / "build.log").write_text("abc\n")
        ok, out = self._encrypt(job="signed")
        self.assertFalse(ok)
        self.assertEqual(_every_file(self.upload), [])
        self.assertFalse((self.bin / "age-argv.json").exists())
        self.assertEqual(out, "Encrypted log: none (a staged secret is shorter than 8 characters, "
                              "too short to redact safely).\n")

    def test_no_log_or_an_overlapping_upload_directory_uploads_nothing(self):
        _fake_age(self.bin, "encrypt")
        ok, out = self._encrypt()
        self.assertFalse(ok)
        self.assertEqual(out, "Encrypted log: none (no private build log was written before the failure).\n")
        (self.logs / "build.log").write_text(SECRET + "\n")
        for upload in (self.logs, self.logs / "encrypted", self.root, self.root / "blowhorn-signing" / "out"):
            with self.subTest(upload=upload):
                ok, out = self._encrypt(upload=upload)
                self.assertFalse(ok)
                self.assertIn("Encrypted log: none (the upload directory must not hold or sit inside", out)
        self.assertEqual([p.name for p in _every_file(self.logs)], ["build.log"])
        self.assertFalse((self.bin / "age-argv.json").exists())

    def test_what_the_staging_scripts_really_write_is_classified_and_redacted(self):
        # Run the real staging scripts with fake secrets, then plant every
        # secret value in a log: each line holding one must be removed.
        scripts = ROOT / ".github" / "scripts" / "build-dmg"
        secrets = {
            "DEVELOPER_ID_P12": base64.b64encode(P12_BYTES).decode(),
            "DEVELOPER_ID_P12_PASSPHRASE": PASSPHRASE,
            "APPLE_API_KEY": "\n".join(P8_LINES),
            "APPLE_TEAM_ID": "TEAM123456",
            "APPLE_API_KEY_ID": "KEYID12345",
            "APPLE_API_ISSUER": "issuer-uuid",
            "BLOWHORN_DIAGNOSTICS_KEY": DIAG_KEY,
        }
        env = {"RUNNER_TEMP": str(self.root), "PATH": os.environ.get("PATH", "/usr/bin:/bin"), **secrets}
        for script in ("materialize_signing.sh", "stage_diagnostics_key.sh"):
            done = subprocess.run(["bash", str(scripts / script)], env=env, capture_output=True, text=True, timeout=60)
            self.assertEqual(done.returncode, 0, done.stderr)
        written = {p.relative_to(self.root).as_posix() for p in _every_file(self.root)
                   if p.parent.name in ("blowhorn-signing", "blowhorn-diagnostics")}
        self.assertIn("blowhorn-signing/developer-id.p12", written)
        self.assertIn("blowhorn-diagnostics/key", written)
        classified = set(encrypt_logs.SECRET_FILES) | set(encrypt_logs.BINARY_SECRET_FILES) | set(encrypt_logs.UNMATCHED_FILES)
        self.assertEqual(written - classified, set())
        _fake_age(self.bin, "encrypt")
        key_material = ("DEVELOPER_ID_P12", "DEVELOPER_ID_P12_PASSPHRASE", "BLOWHORN_DIAGNOSTICS_KEY")
        planted = [f"value {secrets[name]} here" for name in key_material] + P8_LINES[1:4]
        (self.logs / "build.log").write_text("\n".join(["==> package", *planted]) + "\n")
        ok, _out = self._encrypt(job="signed")
        self.assertTrue(ok)
        plain = self._age_stdin()
        for value in [secrets[name] for name in key_material] + P8_LINES[1:4]:
            self.assertNotIn(value.encode(), plain)
        self.assertEqual(plain.count(encrypt_logs.REMOVED), len(planted))
        self.assertIn(b"==> package", plain)

    def test_make_writes_the_ciphertext_where_the_upload_step_looks(self):
        _fake_age(self.bin, "encrypt")
        (self.logs / "build.log").write_text(SECRET + "\n")
        env = {"PATH": os.pathsep.join([str(self.bin), os.environ.get("PATH", "")]), "RUNNER_TEMP": str(self.root),
               "HOME": str(self.root)}
        done = subprocess.run(["make", "-s", "build-dmg-encrypt-log", "JOB=adhoc"], cwd=ROOT, env=env,
                              capture_output=True, text=True, timeout=60)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn("hunter2", done.stdout + done.stderr)
        self.assertEqual(_every_file(self.root / "build-dmg-encrypted"), [self.root / "build-dmg-encrypted" / "adhoc.log.age"])


class BuildDmgEncryptedLogWorkflowTest(unittest.TestCase):
    """Both Mac jobs install age; the action encrypts and uploads only on failure, before the teardown."""

    def test_both_mac_jobs_install_age_before_any_secret_is_staged(self):
        workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "build-dmg.yml").read_text())
        for job_id in ("build-mac-adhoc", "build-mac-signed"):
            with self.subTest(job=job_id):
                steps = workflow["jobs"][job_id]["steps"]
                names = [step.get("name", "") for step in steps]
                install = steps[names.index("Install age")]
                self.assertEqual(install["run"], "brew install --quiet age >/dev/null")
                self.assertEqual(install["env"]["HOMEBREW_NO_AUTO_UPDATE"], "1")
                self.assertIs(install.get("continue-on-error"), True)
                self.assertLessEqual(install["timeout-minutes"], 5)
                self.assertNotIn("secrets.", yaml.dump(install))
                first_secret = min(i for i, step in enumerate(steps) if "secrets." in yaml.dump(step))
                self.assertLess(names.index("Install age"), first_secret)

    def test_the_action_encrypts_and_uploads_only_the_ciphertext_on_failure(self):
        action = yaml.safe_load((ROOT / ".github" / "actions" / "build-dmg-mac" / "action.yml").read_text())
        steps = action["runs"]["steps"]
        names = [step.get("name", "") for step in steps]
        encrypt = steps[names.index("Encrypt the failed build's log (ciphertext only)")]
        upload = steps[names.index("Upload the encrypted log (failed build only)")]
        self.assertEqual(encrypt["if"], "failure()")
        self.assertEqual(encrypt["env"], {"BUILD_DMG_JOB": JOB_EXPR})
        self.assertEqual(encrypt["run"], 'make build-dmg-encrypt-log JOB="$BUILD_DMG_JOB"')
        self.assertEqual(upload["if"], "failure()")
        self.assertEqual(upload["uses"], "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9")
        name = f"build-dmg-{JOB_EXPR}-log-attempt${{{{ github.run_attempt }}}}"
        self.assertEqual(upload["with"], {
            "name": name,
            "path": "${{ runner.temp }}/build-dmg-encrypted/*.age",
            "retention-days": 3,
            "if-no-files-found": "ignore",
            "compression-level": 0,
        })
        for mode, job in (("developer-id", "signed"), ("adhoc", "adhoc")):
            rendered = name.replace(JOB_EXPR, job).replace("${{ github.run_attempt }}", "3")
            self.assertEqual(rendered, encrypted_log.BUILD_DMG.artifact(job, "3"), mode)
        build = names.index("Build, sign, notarize and verify (output withheld)")
        teardown = names.index("Delete the temporary signing keychain")
        self.assertLess(build, names.index(encrypt["name"]))
        self.assertLess(names.index(encrypt["name"]), names.index(upload["name"]))
        self.assertLess(names.index(upload["name"]), teardown)


class BuildDmgFetchLogTest(unittest.TestCase):
    """make build-dmg-log reads the Mac job's artifact through the shared fetch_log.py."""

    def setUp(self):
        spec = importlib.util.spec_from_file_location("build_dmg_fetch_log", HERE / "encrypted-log" / "fetch_log.py")
        self.fetch_log = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.fetch_log)
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.argv_file = root / "gh-argv"
        self.bin = root / "bin"
        self.bin.mkdir()
        self.key = root / "key.txt"
        self.key.write_text("AGE-SECRET-KEY-FAKE")
        self.workdir = root / "work"
        self.workdir.mkdir()
        (self.bin / "gh").write_text(f"""#!{sys.executable}
import sys
from pathlib import Path
args = sys.argv[1:]
Path({str(self.argv_file)!r}).write_text(" ".join(args))
folder = Path(args[args.index("-D") + 1]) / "build-dmg-signed-log-attempt1"
folder.mkdir(parents=True)
(folder / "signed.log.age").write_text("CIPHER hunter2")
""")
        (self.bin / "age").write_text(f"""#!{sys.executable}
import sys
from pathlib import Path
args = sys.argv[1:]
Path(args[args.index("--output") + 1]).write_text(Path(args[-1]).read_text().replace("CIPHER", "PLAIN"))
""")
        for tool in ("gh", "age"):
            (self.bin / tool).chmod(0o755)
        self.env = mock.patch.dict(os.environ, {"PATH": os.pathsep.join([str(self.bin), "/usr/bin", "/bin"])})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def _main(self, job):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(self.fetch_log.tempfile, "tempdir", str(self.workdir)), \
                mock.patch("sys.stdout", out), mock.patch("sys.stderr", err):
            status = self.fetch_log.main(["--kind", "build-dmg", "--name", job, "--run", "42", "--key", str(self.key)])
        return status, out.getvalue(), err.getvalue()

    def test_an_unknown_job_is_refused_before_anything_is_downloaded(self):
        status, _out, err = self._main("release")
        self.assertEqual(status, 2)
        self.assertEqual(err, "build-dmg-log: JOB must be one of signed, adhoc.\n")
        self.assertFalse(self.argv_file.exists())

    def test_the_job_log_is_decrypted_outside_the_repo_and_only_its_path_printed(self):
        status, out, _err = self._main("signed")
        self.assertEqual(status, 0)
        self.assertIn("-p build-dmg-signed-log-attempt* ", self.argv_file.read_text())
        files = _every_file(self.workdir)
        self.assertEqual([f.name for f in files], ["build-dmg-signed-run42-attempt1.log"])
        self.assertEqual(files[0].read_text(), "PLAIN hunter2")
        self.assertFalse(files[0].resolve().is_relative_to(ROOT))
        self.assertIn(f"Decrypted log: {files[0].resolve()}\n", out)
        self.assertNotIn("hunter2", out)

if __name__ == "__main__":
    unittest.main()
