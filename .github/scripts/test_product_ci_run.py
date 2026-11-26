#!/usr/bin/env python3
"""Tests for product-ci/run.py: a private suite's output never reaches the public log.

Run with `make test-scripts` (CI runs it too).
"""

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SPEC = importlib.util.spec_from_file_location("product_ci_run", HERE / "product-ci" / "run.py")
run = importlib.util.module_from_spec(SPEC)
sys.modules["product_ci_run"] = run
SPEC.loader.exec_module(run)

SECRET = "tests/test_private_module.py::test_secret_branch assert token == 'hunter2'"


def _py(code):
    return (sys.executable, "-c", code)


class RunStepsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.product = Path(self.tmp.name) / "product"
        self.product.mkdir()
        self.log = Path(self.tmp.name) / "private" / "suite.log"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, steps):
        out = io.StringIO()
        status = run.run_steps(steps, self.product, self.log, out=out)
        return status, out.getvalue()

    def test_a_passing_suite_prints_counts_and_none_of_its_output(self):
        code = f"import sys; print({SECRET!r}); print({SECRET!r}, file=sys.stderr); print('=== 12 passed, 3 skipped, 1 xfailed in 4.20s ===')"
        status, out = self._run([run.Step("test suite", _py(code), counts="pytest")])
        self.assertEqual(status, 0)
        self.assertNotIn("hunter2", out)
        self.assertNotIn("test_private_module", out)
        self.assertIn("test suite: ok", out)
        self.assertIn("[12 passed, 3 skipped, 1 xfailed]", out)
        self.assertIn("hunter2", self.log.read_text())

    def test_a_failing_step_stops_the_run_and_withholds_its_output(self):
        fail = f"import sys; print({SECRET!r}); print('1 failed, 4 passed in 1s'); sys.exit(3)"
        status, out = self._run([
            run.Step("lint", _py(fail), counts="pytest"),
            run.Step("never runs", _py("open('ran', 'w').write('x')")),
        ])
        self.assertEqual(status, 3)
        self.assertNotIn("hunter2", out)
        self.assertIn("lint: failed (exit 3)", out)
        self.assertIn("[1 failed, 4 passed]", out)
        self.assertIn("withheld", out)
        self.assertFalse((self.product / "ran").exists())
        self.assertNotIn("never runs", out)

    def test_a_summary_line_cannot_smuggle_text_through(self):
        code = f"print('7 passed ' + {SECRET!r} + ' 2 failed in 1.00s')"
        status, out = self._run([run.Step("test suite", _py(code), counts="pytest")])
        self.assertEqual(status, 0)
        self.assertNotIn("hunter2", out)
        self.assertIn("[7 passed, 2 failed]", out)

    def test_pytest_counts_come_from_its_summary_line_only(self):
        code = ("print('== 5 passed in 312.40s (0:05:12) ==');"
                "print('found 3 errors in the fixture');"
                "print('Fatal Python error: Aborted')")
        _status, out = self._run([run.Step("test suite", _py(code), counts="pytest")])
        self.assertIn("[5 passed]", out)
        self.assertNotIn("3 errors", out)

    def test_a_failing_pytest_run_names_its_failing_tests_and_nothing_else(self):
        code = ("import sys;"
                "print('FAILED tests/test_private_module.py::Case::test_secret_branch - assert token == \\'hunter2\\'');"
                "print('ERROR tests/sub/test_other.py::test_param[hunter2-x] - boom');"
                "print('FAILED tests/../etc/passwd.py::x - hunter2');"
                "print('FAILED /abs/hunter2.py::t');"
                "print('== 2 failed, 5 passed in 1.00s ==');"
                "sys.exit(1)")
        _status, out = self._run([run.Step("test suite", _py(code), counts="pytest")])
        self.assertIn("  failed tests/test_private_module.py::Case::test_secret_branch\n", out)
        self.assertIn("  error tests/sub/test_other.py::test_param\n", out)
        self.assertNotIn("hunter2", out)
        self.assertNotIn("passwd", out)
        self.assertIn("withheld", out)

    def test_a_passing_pytest_run_names_no_tests(self):
        code = "print('FAILED tests/test_a.py::test_b - flaky rerun'); print('== 5 passed in 1.00s ==')"
        _status, out = self._run([run.Step("test suite", _py(code), counts="pytest")])
        self.assertNotIn("tests/test_a.py", out)

    def test_a_failing_subtest_names_its_test_and_drops_its_description(self):
        # pytest-subtests' short summary line, as the product's suite prints it
        # (pytest -rfE with xdist): the subtest's description comes first.
        code = ("import sys;"
                "print(\"(command='hunter2 run') SUBFAIL tests/test_private_module.py::Case::test_secret - AssertionError: hunter2\");"
                "print(\"(command='other') SUBFAIL tests/test_private_module.py::Case::test_secret - AssertionError:...\");"
                "print('[hunter2] (x=1) SUBFAIL tests/test_fn.py::test_fn - assert False');"
                "print('FAILED tests/test_p.py::test_param[a]hunter2] - assert False');"
                "print('(x=1) SUBFAIL /abs/hunter2.py::t - boom');"
                "print('== 4 failed, 5 passed in 1.00s ==');"
                "sys.exit(1)")
        _status, out = self._run([run.Step("test suite", _py(code), counts="pytest")])
        listed = [line.strip() for line in out.splitlines() if line.startswith("  ")]
        self.assertEqual(listed, [
            "failed tests/test_private_module.py::Case::test_secret",
            "failed tests/test_fn.py::test_fn",
            "failed tests/test_p.py::test_param",
        ])
        self.assertNotIn("hunter2", out)
        self.assertNotIn("SUBFAIL", out)

    def test_failing_test_names_are_capped(self):
        lines = [f"FAILED tests/test_m.py::test_{i}" for i in range(run.MAX_FAILED_IDS + 5)]
        self.assertEqual(len(run.pytest_failed_ids("\n".join(lines))), run.MAX_FAILED_IDS)

    def test_no_pytest_summary_prints_no_counts(self):
        code = "import sys; print('found 3 errors'); print('2 failed checks'); sys.exit(134)"
        _status, out = self._run([run.Step("test suite", _py(code), counts="pytest")])
        self.assertIn("test suite: failed (exit 134)", out)
        self.assertNotIn("[", out)

    def test_vitest_counts_come_from_its_summary_lines_only(self):
        code = ("print('\\x1b[32m✓\\x1b[0m tests/private-file.test.ts (3)');"
                "print(' Test Files  \\x1b[1m98 passed\\x1b[0m (98)');"
                "print('      Tests  1367 passed | 2 skipped (1369)')")
        _status, out = self._run([run.Step("test", _py(code), counts="vitest")])
        self.assertNotIn("private-file", out)
        self.assertIn("[files: 98 passed; tests: 1367 passed, 2 skipped]", out)

    def test_vitest_counts_include_the_errors_line(self):
        code = ("print(' Test Files  330 passed (330)');"
                "print('      Tests  6265 passed | 10 skipped (6275)');"
                "print('     Errors  1 error')")
        _status, out = self._run([run.Step("test", _py(code), counts="vitest")])
        self.assertIn("[files: 330 passed; tests: 6265 passed, 10 skipped; errors: 1 error]", out)

    def test_a_failing_vitest_run_names_its_failing_tests_and_nothing_else(self):
        code = (
            "import sys;"
            "print('\\x1b[41m\\x1b[1m FAIL \\x1b[0m tests/cli-answers.test.ts > reports a run that timed out');"
            "print('AssertionError: expected hunter2 to be 0');"
            "print('  \\u276f tests/cli-answers.test.ts:154:7');"
            "print(' FAIL  tests/sub/other.test.ts > Case > test_param [ tests/sub/other.test.ts ]');"
            "print(' FAIL  tests/../etc/passwd.test.ts > x');"
            "print(' FAIL  /abs/hunter2.test.ts > t');"
            "print(' Test Files  1 failed | 329 passed (330)');"
            "print('      Tests  1 failed | 6264 passed (6265)');"
            "sys.exit(1)"
        )
        _status, out = self._run([run.Step("test", _py(code), counts="vitest")])
        self.assertIn("  failed tests/cli-answers.test.ts > reports a run that timed out\n", out)
        self.assertIn("  failed tests/sub/other.test.ts > Case > test_param\n", out)
        self.assertNotIn("hunter2", out)
        self.assertNotIn("passwd", out)
        self.assertNotIn(":154", out)
        self.assertIn("withheld", out)

    def test_a_passing_vitest_run_names_no_tests(self):
        code = ("print(' FAIL  tests/cli-answers.test.ts > leftover from a retry');"
                "print(' Test Files  330 passed (330)');"
                "print('      Tests  6265 passed (6265)')")
        _status, out = self._run([run.Step("test", _py(code), counts="vitest")])
        self.assertNotIn("cli-answers", out)
        self.assertNotIn("failed tests/", out)

    def test_failing_vitest_test_names_are_capped(self):
        lines = [f"FAIL  tests/m.test.ts > test_{i}" for i in range(run.MAX_FAILED_IDS + 5)]
        self.assertEqual(len(run.vitest_failed_ids("\n".join(lines))), run.MAX_FAILED_IDS)

    def test_a_vitest_run_with_unhandled_errors_prints_the_heading_and_no_source(self):
        banner = "⎯⎯⎯⎯⎯⎯ Unhandled Errors ⎯⎯⎯⎯⎯⎯"
        per_error = "⎯⎯⎯⎯⎯⎯ Unhandled Error ⎯⎯⎯⎯⎯⎯"
        code = (
            "import sys;"
            f"print({banner!r});"
            "print('Vitest caught 1 unhandled error during the test run.');"
            f"print({per_error!r});"
            "print('Error: worker exited unexpectedly hunter2');"
            "print('  \\u276f /home/runner/work/blowhorn/desktop/tests/secret.test.ts:12:3');"
            "print(' Test Files  330 passed (330)');"
            "print('      Tests  6265 passed | 10 skipped (6275)');"
            "print('     Errors  1 error');"
            "sys.exit(1)"
        )
        _status, out = self._run([run.Step("test", _py(code), counts="vitest")])
        self.assertIn("[files: 330 passed; tests: 6265 passed, 10 skipped; errors: 1 error]", out)
        self.assertIn("  unhandled errors\n", out)
        self.assertIn("  unhandled error\n", out)
        self.assertNotIn("hunter2", out)
        self.assertNotIn("secret.test.ts", out)
        self.assertNotIn("worker exited", out)
        self.assertIn("withheld", out)

    def test_vitest_failed_ids_drop_source_paths_and_unsafe_names(self):
        text = (
            " FAIL  tests/../etc/passwd.test.ts > x\n"
            " FAIL  /abs/hunter2.test.ts > t\n"
            " FAIL  src/not-under-tests.test.ts > t\n"
            "Error: hunter2 at /etc/passwd:1\n"
            "⎯⎯⎯⎯ Unhandled Rejection ⎯⎯⎯⎯\n"
        )
        ids = run.vitest_failed_ids(text)
        self.assertEqual(ids, ["unhandled rejection"])
        self.assertNotIn("hunter2", " ".join(ids))
        self.assertNotIn("passwd", " ".join(ids))


    def test_a_hung_step_times_out_and_fails(self):
        status, out = self._run([run.Step("hang", _py("import time; time.sleep(30)"), timeout_s=1)])
        self.assertEqual(status, 124)
        self.assertIn("hang: failed (timed out after 1 s)", out)

    def test_a_missing_command_fails_without_a_traceback(self):
        status, out = self._run([run.Step("missing", ("definitely-not-a-command-xyz",))])
        self.assertEqual(status, 127)
        self.assertIn("missing: failed (could not start", out)
        self.assertNotIn("Traceback", out)

    def test_a_step_cannot_write_to_the_runner_file_commands(self):
        files = {name: Path(self.tmp.name) / name.lower() for name in sorted(run.FILE_COMMANDS)}
        for path in files.values():
            path.write_text("")
        write_all = ("import os\n"
                     f"for name in {sorted(files)!r}:\n"
                     "    if os.environ.get(name):\n"
                     f"        open(os.environ[name], 'a').write({SECRET!r})\n"
                     "print('KEEP=' + os.environ.get('KEEP', ''))")
        with mock.patch.dict("os.environ", {**{k: str(v) for k, v in files.items()}, "KEEP": "kept"}):
            status, _out = self._run([run.Step("summary", _py(write_all))])
        self.assertEqual(status, 0)
        for name, path in files.items():
            self.assertEqual(path.read_text(), "", name)
        self.assertIn("KEEP=kept", self.log.read_text())

    def test_a_step_does_not_inherit_the_calling_make(self):
        show = "import os; print('MAKE_STATE=' + repr([os.environ.get(n) for n in ('MAKEFLAGS', 'MAKELEVEL', 'MFLAGS', 'MAKEOVERRIDES')]))"
        calling_make = {"MAKEFLAGS": " -- SUITE=python PRODUCT_DIR=product", "MAKELEVEL": "1", "MFLAGS": "-s",
                        "MAKEOVERRIDES": "${-*-command-variables-*-}"}
        with mock.patch.dict("os.environ", calling_make):
            status, _out = self._run([run.Step("make state", _py(show))])
        self.assertEqual(status, 0)
        self.assertIn("MAKE_STATE=[None, None, None, None]", self.log.read_text())

    def test_a_step_does_not_inherit_checkout_tokens(self):
        show = (
            "import os; print('TOKENS=' + repr([os.environ.get(n) for n in "
            "('DMG_SOURCE_TOKEN', 'INPUT_PRODUCT_TOKEN', 'INPUT_TOKEN', 'GH_TOKEN', 'GITHUB_TOKEN')]))"
        )
        secrets = {
            "DMG_SOURCE_TOKEN": "source-token-value",
            "INPUT_PRODUCT_TOKEN": "source-token-value",
            "INPUT_TOKEN": "source-token-value",
            "GH_TOKEN": "source-token-value",
            "GITHUB_TOKEN": "source-token-value",
            "KEEP": "kept",
        }
        with mock.patch.dict("os.environ", secrets):
            status, _out = self._run([run.Step("tokens", _py(show + "; print('KEEP=' + os.environ.get('KEEP', ''))"))])
        self.assertEqual(status, 0)
        logged = self.log.read_text()
        self.assertIn("TOKENS=[None, None, None, None, None]", logged)
        self.assertIn("KEEP=kept", logged)
        self.assertNotIn("source-token-value", logged)

    def test_steps_run_in_their_own_directory_of_the_product(self):
        (self.product / "desktop").mkdir()
        status, _out = self._run([run.Step("here", _py("open('marker', 'w').write('x')"), cwd="desktop")])
        self.assertEqual(status, 0)
        self.assertTrue((self.product / "desktop" / "marker").exists())

    def test_cargo_counts_aggregate_result_lines_and_withhold_test_names(self):
        code = ("print('running 16 tests');"
                "print('test python_json::tests::nonfinite_constants_are_json ... ok');"
                "print('test result: ok. 16 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.03s');"
                "print('running 37 tests');"
                "print('test result: ok. 37 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 2.47s');"
                "print('test result: FAILED. 2 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s')")
        status, out = self._run([run.Step("test suite", _py(code), counts="cargo")])
        self.assertEqual(status, 0)
        self.assertNotIn("python_json", out)
        self.assertNotIn("nonfinite", out)
        self.assertIn("[55 passed, 1 failed]", out)

    def test_no_cargo_summary_prints_no_counts(self):
        code = "import sys; print('error: could not compile blowhorn-host'); sys.exit(101)"
        status, out = self._run([run.Step("test suite", _py(code), counts="cargo")])
        self.assertEqual(status, 101)
        self.assertIn("test suite: failed (exit 101)", out)
        self.assertNotIn("blowhorn-host", out)
        self.assertNotIn("[", out)

    def test_a_failing_cargo_run_names_its_failing_tests_and_nothing_else(self):
        code = (
            "import sys\n"
            "print('     Running unittests src/lib.rs (target/debug/deps/blowhorn_host-0123456789abcdef)')\n"
            "print('running 3 tests')\n"
            "print('test python_json::tests::nonfinite_constants_are_json ... \\x1b[31mFAILED\\x1b[0m')\n"
            "print('test ok_one ... ok')\n"
            "print()\n"
            "print('failures:')\n"
            "print()\n"
            "print('---- python_json::tests::nonfinite_constants_are_json stdout ----')\n"
            "print(\"thread 'python_json::tests::nonfinite_constants_are_json' panicked at engine/rust/src/secret.rs:12:5:\")\n"
            "print(\"assertion failed: token == 'hunter2'\")\n"
            "print('test injected::should_not_appear ... FAILED')\n"
            "print()\n"
            "print('failures:')\n"
            "print('    python_json::tests::nonfinite_constants_are_json')\n"
            "print()\n"
            "print('test result: FAILED. 2 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s')\n"
            "print('     Running tests/contract.rs (target/debug/deps/contract_suite-aabbccddeeff0011)')\n"
            "print('test every_case_is_at_contract ... FAILED')\n"
            "print('failures:')\n"
            "print('    every_case_is_at_contract')\n"
            "print('test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s')\n"
            "print('error: test failed, to rerun pass `--test contract_suite`')\n"
            "sys.exit(101)\n"
        )
        status, out = self._run([run.Step("test suite", _py(code), counts="cargo")])
        self.assertEqual(status, 101)
        self.assertIn("  failed blowhorn_host::python_json::tests::nonfinite_constants_are_json\n", out)
        self.assertIn("  failed contract_suite::every_case_is_at_contract\n", out)
        self.assertEqual(out.count("failed blowhorn_host::python_json"), 1)
        self.assertNotIn("hunter2", out)
        self.assertNotIn("secret.rs", out)
        self.assertNotIn("src/lib.rs", out)
        self.assertNotIn("injected", out)
        self.assertNotIn("engine/rust", out)
        self.assertIn("withheld", out)
        self.assertIn("[2 passed, 2 failed]", out)

    def test_a_passing_cargo_run_names_no_tests(self):
        code = (
            "print('     Running unittests src/lib.rs (target/debug/deps/blowhorn_host-0123456789abcdef)')\n"
            "print('test python_json::tests::nonfinite_constants_are_json ... FAILED')\n"
            "print('test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s')"
        )
        _status, out = self._run([run.Step("test suite", _py(code), counts="cargo")])
        self.assertNotIn("python_json", out)
        self.assertNotIn("blowhorn_host", out)

    def test_failing_cargo_test_names_are_capped(self):
        header = "     Running unittests src/lib.rs (target/debug/deps/crate_a-0123456789abcdef)\n"
        lines = [f"test test_{i} ... FAILED" for i in range(run.MAX_FAILED_IDS + 5)]
        self.assertEqual(len(run.cargo_failed_ids(header + "\n".join(lines))), run.MAX_FAILED_IDS)

    def test_cargo_failed_ids_drop_source_paths_and_unsafe_names(self):
        text = (
            "     Running unittests src/lib.rs (target/debug/deps/okbin-0123456789abcdef)\n"
            "test src/lib.rs ... FAILED\n"
            "test ../etc/passwd ... FAILED\n"
            "test path/with/slash ... FAILED\n"
            "     Running `/tmp/hunter2/target/debug/deps/from_cmd-deadbeef --exact`\n"
            "test only_safe_name ... FAILED\n"
        )
        self.assertEqual(run.cargo_failed_ids(text), ["failed from_cmd::only_safe_name"])
        self.assertNotIn("hunter2", " ".join(run.cargo_failed_ids(text)))
        self.assertNotIn("passwd", " ".join(run.cargo_failed_ids(text)))

    def test_cargo_failed_ids_read_the_failures_list_when_progress_lines_are_absent(self):
        text = (
            "     Running tests/legacy_host.rs (target/aarch64-unknown-linux-gnu/debug/deps/legacy_host-abcdef0123456789)\n"
            "failures:\n"
            "    the_exact_path_is_listed_and_a_lookalike_is_not\n"
            "\n"
            "test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s\n"
        )
        self.assertEqual(
            run.cargo_failed_ids(text),
            ["failed legacy_host::the_exact_path_is_listed_and_a_lookalike_is_not"],
        )

    def test_rust_steps_run_make_cli_rust_tests(self):
        steps = run.rust_steps()
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0].argv, ("make", "cli-rust-tests"))
        self.assertEqual(steps[0].counts, "cargo")

    def test_python_steps_run_make_cli_tests(self):
        steps = run.python_steps("/opt/python/bin/python")
        self.assertEqual([step.label for step in steps], [
            "install dependencies", "playwright import boundary", "test suite",
        ])
        self.assertEqual(steps[2].argv[:8], (
            "timeout", "-s", "ABRT", "900", "make", "cli-tests",
            "PYTHON=/opt/python/bin/python -u",
            "PYTEST_ARGS=tests/ -q -rfE -o faulthandler_timeout=300",
        ))
        self.assertTrue(steps[2].argv[8].startswith("PYTEST_WORKERS="))
        self.assertGreaterEqual(int(steps[2].argv[8].split("=", 1)[1]), 2)
        self.assertEqual(steps[2].counts, "pytest")


def _fake_age(directory: Path, behaviour: str) -> Path:
    """An `age` on PATH that records its argv and its stdin, then behaves as asked.

    The plaintext arrives on stdin (encrypted_log.encrypt never names a file).
    encrypt: writes the age header and opaque bytes to --output (as real age does)
    copy:    writes the plaintext input to --output (a broken or hostile age)
    prefix:  writes the age header without its newline, then the plaintext
    fail:    exits 1 after writing a partial file
    """
    directory.mkdir(parents=True, exist_ok=True)
    script = directory / "age"
    script.write_text(f"""#!{sys.executable}
import json, sys
from pathlib import Path
args = sys.argv[1:]
Path({str(directory / "age-argv.json")!r}).write_text(json.dumps(args))
output = Path(args[args.index("--output") + 1])
plain = sys.stdin.buffer.read()
Path({str(directory / "age-stdin")!r}).write_bytes(plain)
behaviour = {behaviour!r}
if behaviour == "encrypt":
    output.write_bytes(b"age-encryption.org/v1\\n-> X25519 opaque\\n" + bytes(reversed(plain)))
elif behaviour == "copy":
    output.write_bytes(plain)
elif behaviour == "prefix":
    plain = plain.lstrip(b"\\n")
    output.write_bytes(b"age-encryption.org/v1" + plain)
else:
    output.write_bytes(b"age-encryption.org/v1\\n")
    sys.exit(1)
""")
    script.chmod(0o755)
    return script


def _every_file(directory: Path) -> list[Path]:
    return sorted(p for p in directory.rglob("*") if p.is_file()) if directory.exists() else []


class EncryptedLogTest(unittest.TestCase):
    """A failed suite's log leaves the runner only as age ciphertext, in its own directory."""

    FAIL = f"import sys; print({SECRET!r}); print('== 1 failed in 1.00s =='); sys.exit(1)"
    PASS = f"print({SECRET!r}); print('== 1 passed in 1.00s ==')"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.product = root / "product"
        self.product.mkdir()
        self.log = root / "product-ci" / "python.log"
        self.upload = root / "product-ci-encrypted"
        self.bin = root / "bin"
        self.bin.mkdir()
        self.env = mock.patch.dict(os.environ, {
            "PATH": os.pathsep.join([str(self.bin), "/usr/bin", "/bin"]),
            "GITHUB_RUN_ATTEMPT": "2",
            "GITHUB_RUN_ID": "1234",
        })
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def _run(self, code, upload=None):
        out = io.StringIO()
        status = run.run_steps([run.Step("test suite", _py(code), counts="pytest")], self.product, self.log,
                               out=out, suite="python", encrypted_dir=upload or self.upload)
        return status, out.getvalue()

    def _assert_no_plaintext_uploaded(self):
        for path in _every_file(self.upload):
            self.assertNotIn(b"hunter2", path.read_bytes(), path)

    def test_a_failed_suite_is_encrypted_to_the_recipient_and_only_the_ciphertext_is_written(self):
        _fake_age(self.bin, "encrypt")
        status, out = self._run(self.FAIL)
        self.assertEqual(status, 1)
        argv = json.loads((self.bin / "age-argv.json").read_text())
        self.assertEqual(argv[argv.index("--recipient") + 1],
                         "age14zuswrahtrqh7ksyjjv7u0vxqsrxzykhymfavt6x9yvuram67p9se6ngeq")
        self.assertEqual(argv[-2:], ["--output", str(self.upload.resolve() / ".python.log.age.partial")])
        self.assertEqual((self.bin / "age-stdin").read_bytes(), self.log.read_bytes())
        self.assertNotIn("--armor", argv)
        self.assertEqual([p.name for p in _every_file(self.upload)], ["python.log.age"])
        self.assertTrue((self.upload / "python.log.age").read_bytes().startswith(b"age-encryption.org/v1\n"))
        self._assert_no_plaintext_uploaded()
        self.assertIn("Encrypted log: available as artifact product-ci-python-log-attempt2, "
                      "readable only with the maintainers' key (make product-ci-log RUN=1234 SUITE=python).\n", out)
        self.assertNotIn("hunter2", out)
        self.assertIn("hunter2", self.log.read_text())

    def test_without_age_nothing_is_written_for_upload(self):
        status, out = self._run(self.FAIL)
        self.assertEqual(status, 1)
        self.assertEqual(_every_file(self.upload), [])
        self.assertIn("Encrypted log: none (age is not installed on this runner).\n", out)

    def test_an_age_failure_or_a_plaintext_output_writes_nothing_for_upload(self):
        for behaviour, reason in (("fail", "age failed with exit 1"),
                                  ("copy", "age wrote something that is not age ciphertext"),
                                  ("prefix", "age wrote something that is not age ciphertext")):
            with self.subTest(behaviour=behaviour):
                _fake_age(self.bin, behaviour)
                _status, out = self._run(self.FAIL)
                self.assertEqual(_every_file(self.upload), [])
                self.assertIn(f"Encrypted log: none ({reason}).\n", out)
                self.assertNotIn("artifact", out)

    def test_a_passing_suite_writes_nothing_and_never_starts_age(self):
        _fake_age(self.bin, "encrypt")
        status, out = self._run(self.PASS)
        self.assertEqual(status, 0)
        self.assertEqual(_every_file(self.upload), [])
        self.assertFalse((self.bin / "age-argv.json").exists())
        self.assertNotIn("Encrypted log", out)

    def test_the_upload_directory_may_not_hold_or_sit_beside_the_plaintext_log(self):
        _fake_age(self.bin, "encrypt")
        for upload in (self.log.parent, self.log.parent / "encrypted"):
            with self.subTest(upload=upload.name):
                _status, out = self._run(self.FAIL, upload=upload)
                self.assertEqual([p for p in _every_file(self.log.parent) if p != self.log], [])
                self.assertIn("Encrypted log: none (the upload directory must not hold or sit inside a "
                              "directory with the plaintext log or a secret).\n", out)
        self.assertFalse((self.bin / "age-argv.json").exists())


class ProductCiEncryptedLogWorkflowTest(unittest.TestCase):
    """Each job installs age and uploads only its suite's ciphertext, under run.py's name."""

    def test_each_job_uploads_only_the_ciphertext_its_run_py_names(self):
        for job_id, job in _product_ci_jobs().items():
            with self.subTest(job=job_id):
                steps = job["steps"]
                names = [step.get("name", "") for step in steps]
                suite = next(step for step in steps if "make product-ci SUITE=" in str(step.get("run", "")))
                self.assertIn(f"SUITE={job_id} ", suite["run"])
                self.assertIn('PRODUCT_CI_ENCRYPTED_DIR="$RUNNER_TEMP/product-ci-encrypted"', suite["run"])
                install = steps[names.index("Install age")]
                self.assertIn("apt-get install -y -qq --no-install-recommends age", install["run"])
                self.assertIn(">/dev/null", install["run"])
                self.assertIs(install.get("continue-on-error"), True)
                self.assertTrue(install.get("timeout-minutes"))
                self.assertLess(names.index("Install age"), steps.index(suite))
                uploads = [step for step in steps if "upload-artifact" in str(step.get("uses", ""))]
                self.assertEqual(len(uploads), 1)
                upload = uploads[0]
                self.assertEqual(steps.index(upload), len(steps) - 1)
                self.assertEqual(upload["uses"], "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9")
                self.assertEqual(upload["if"], "failure()")
                name = upload["with"]["name"]
                self.assertEqual(name, f"product-ci-{job_id}-log-attempt${{{{ github.run_attempt }}}}")
                self.assertEqual(upload["with"], {
                    "name": name,
                    "path": "${{ runner.temp }}/product-ci-encrypted/*.age",
                    "retention-days": 3,
                    "if-no-files-found": "ignore",
                    "compression-level": 0,
                })
                self.assertFalse(any("cache" in str(step.get("uses", "")) for step in steps))


class FetchLogTest(unittest.TestCase):
    """make product-ci-log decrypts into a temp directory outside the repo and prints only a path."""

    def setUp(self):
        spec = importlib.util.spec_from_file_location("encrypted_log_fetch_log", HERE / "encrypted-log" / "fetch_log.py")
        self.fetch_log = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.fetch_log)
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.bin = root / "bin"
        self.bin.mkdir()
        self.key = root / "key.txt"
        self.workdir = root / "work"
        self.workdir.mkdir()
        gh = self.bin / "gh"
        # A downloaded run with attempts 1 and 2: each artifact in its own directory, as gh does for -p.
        gh.write_text(f"""#!{sys.executable}
import sys
from pathlib import Path
args = sys.argv[1:]
Path({str(root / "gh-argv")!r}).write_text(" ".join(args))
dest = Path(args[args.index("-D") + 1])
for attempt in (1, 2):
    folder = dest / f"product-ci-python-log-attempt{{attempt}}"
    folder.mkdir(parents=True)
    (folder / "python.log.age").write_text(f"CIPHER attempt {{attempt}} hunter2")
""")
        gh.chmod(0o755)
        age = self.bin / "age"
        age.write_text(f"""#!{sys.executable}
import sys
from pathlib import Path
args = sys.argv[1:]
Path(args[args.index("--output") + 1]).write_text(Path(args[-1]).read_text().replace("CIPHER", "PLAIN"))
""")
        age.chmod(0o755)
        self.env = mock.patch.dict(os.environ, {"PATH": os.pathsep.join([str(self.bin), "/usr/bin", "/bin"])})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_a_missing_key_is_refused_before_anything_is_downloaded(self):
        err = io.StringIO()
        with mock.patch("sys.stderr", err):
            status = self.fetch_log.main(["--kind", "product-ci", "--name", "python", "--run", "42",
                                          "--key", str(self.key)])
        self.assertEqual(status, 2)
        self.assertIn("No private key at", err.getvalue())
        self.assertFalse((Path(self.tmp.name) / "gh-argv").exists())

    def test_the_latest_attempt_is_decrypted_outside_the_repo_and_only_its_path_printed(self):
        self.key.write_text("AGE-SECRET-KEY-FAKE")
        with mock.patch.object(self.fetch_log.tempfile, "tempdir", str(self.workdir)):
            out = io.StringIO()
            with mock.patch("sys.stdout", out):
                status = self.fetch_log.main(["--kind", "product-ci", "--name", "python", "--run", "42",
                                              "--key", str(self.key)])
        self.assertEqual(status, 0)
        self.assertIn("-p product-ci-python-log-attempt* ", (Path(self.tmp.name) / "gh-argv").read_text())
        files = _every_file(self.workdir)
        self.assertEqual(len(files), 1, files)
        self.assertEqual(files[0].name, "product-ci-python-run42-attempt2.log")
        self.assertEqual(files[0].read_text(), "PLAIN attempt 2 hunter2")
        self.assertFalse(files[0].resolve().is_relative_to(ROOT))
        self.assertIn(f"Decrypted log: {files[0].resolve()}\n", out.getvalue())
        self.assertNotIn("hunter2", out.getvalue())


class MakeTargetTest(unittest.TestCase):
    def test_make_product_ci_runs_the_suite_and_prints_only_its_summary(self):
        # Resolve `make` from the host PATH instead of assuming where it lives, and
        # fail with a clear message when it is not installed at all.
        host_path = os.environ.get("PATH", "")
        make_bin = shutil.which("make")
        if make_bin is None:
            self.fail(f"`make` was not found on PATH ({host_path!r}); "
                      "install make to run this test (`make test-scripts` needs it).")

        with tempfile.TemporaryDirectory() as tmp:
            product = Path(tmp) / "product"
            (product / "desktop").mkdir(parents=True)
            fake_bin = Path(tmp) / "bin"
            fake_bin.mkdir()
            pnpm = fake_bin / "pnpm"
            pnpm.write_text(f"#!/bin/sh\necho {SECRET!r}\n[ \"$1\" = test ] && echo '      Tests  5 passed (5)'\nexit 0\n")
            pnpm.chmod(0o755)
            log = Path(tmp) / "desktop.log"
            # fake pnpm first, then the host PATH (empty entries dropped: they mean "current dir").
            path = os.pathsep.join(p for p in (str(fake_bin), *host_path.split(os.pathsep)) if p)
            env = {"PATH": path, "HOME": tmp}
            done = subprocess.run([make_bin, "-s", "product-ci", "SUITE=desktop", f"PRODUCT_DIR={product}",
                                   f"PRODUCT_CI_LOG={log}"], cwd=ROOT, env=env, capture_output=True, text=True,
                                  timeout=60)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertNotIn("hunter2", done.stdout + done.stderr)
            for label in ("install", "typecheck", "lint", "test", "build"):
                self.assertIn(f"{label}: ok", done.stdout)
            self.assertIn("[tests: 5 passed]", done.stdout)
            self.assertIn("hunter2", log.read_text())


# These expressions must stay identical to product-ci.yml. github.event_name in
# a called workflow is the caller's event, never workflow_call, so detection
# uses the explicit `caller` input that build-dmg passes.
CONCURRENCY_GROUP = (
    "product-ci-${{ inputs.ref }}-"
    "${{ inputs.caller && format('{0}-{1}', inputs.caller, github.run_id) || 'manual' }}"
)
CONCURRENCY_CANCEL = "${{ !inputs.caller }}"


def product_ci_concurrency(ref: str, caller: str = "", run_id: str = "") -> tuple[str, bool]:
    """Group and cancel-in-progress for one Product CI run. Matches the YAML."""
    suffix = f"{caller}-{run_id}" if caller else "manual"
    return f"product-ci-{ref}-{suffix}", not bool(caller)


class ProductCiConcurrencyTest(unittest.TestCase):
    REF = "0123456789abcdef0123456789abcdef01234567"

    def test_yaml_uses_the_caller_input_not_event_name(self):
        text = (ROOT / ".github" / "workflows" / "product-ci.yml").read_text()
        self.assertIn(f"group: {CONCURRENCY_GROUP}", text)
        self.assertIn(f"cancel-in-progress: {CONCURRENCY_CANCEL}", text)
        self.assertNotIn("github.event_name == 'workflow_call'", text)
        self.assertNotIn("github.event_name != 'workflow_call'", text)
        self.assertIn("never workflow_call", text)
        self.assertIn("caller:", text)
        caller = (ROOT / ".github" / "workflows" / "build-dmg.yml").read_text()
        self.assertIn("caller: build-dmg", caller)

    def test_adhoc_and_signed_calls_of_the_same_ref_do_not_share_a_group(self):
        adhoc, cancel_a = product_ci_concurrency(self.REF, caller="build-dmg", run_id="11")
        signed, cancel_s = product_ci_concurrency(self.REF, caller="build-dmg", run_id="22")
        self.assertNotEqual(adhoc, signed)
        self.assertFalse(cancel_a)
        self.assertFalse(cancel_s)

    def test_manual_runs_of_the_same_ref_share_a_group_and_cancel(self):
        first, cancel_a = product_ci_concurrency(self.REF, run_id="11")
        second, cancel_b = product_ci_concurrency(self.REF, run_id="22")
        self.assertEqual(first, second)
        self.assertEqual(first, f"product-ci-{self.REF}-manual")
        self.assertTrue(cancel_a)
        self.assertTrue(cancel_b)

    def test_a_manual_run_does_not_share_a_group_with_a_build_dmg_call(self):
        manual, _ = product_ci_concurrency(self.REF)
        called, _ = product_ci_concurrency(self.REF, caller="build-dmg", run_id="11")
        self.assertNotEqual(manual, called)




class ProductCiRustToolchainTest(unittest.TestCase):
    """The rust job installs whatever product/engine/rust/rust-toolchain.toml pins.

    The version must not be copied into this public repo: when the product
    raises the pin, this workflow has to follow without a second edit.
    """

    def test_the_workflow_installs_the_toolchain_from_the_product_file(self):
        text = (ROOT / ".github" / "workflows" / "product-ci.yml").read_text()
        self.assertIn("cd product/engine/rust && timeout 600 rustup toolchain install", text)
        self.assertIn("product/engine/rust/rust-toolchain.toml", text)
        self.assertNotIn("1.85", text)
        self.assertNotIn("default-toolchain 1.85", text)
        self.assertNotRegex(text, r"default-toolchain [0-9]")
        self.assertNotRegex(text, r"name: rust \([0-9]")


def _product_ci_jobs():
    """The Product CI workflow, parsed as GitHub Actions YAML (jobs only)."""
    return yaml.safe_load((ROOT / ".github" / "workflows" / "product-ci.yml").read_text())["jobs"]


class ProductCiRustPythonEngineTest(unittest.TestCase):
    """The rust job can run the contract suite against the Python engine.

    make cli-rust-tests starts with BLOWHORN_CONTRACT_ENGINE=python, and
    Engine::from_env looks for checkout venv/bin/python unless
    BLOWHORN_CONTRACT_PYTHON is set. The product's own rust CI sets that
    to the setup-python interpreter after installing engine/requirements-dev.txt.
    Without the same setup here, every_case_is_at_contract fails immediately
    with "no virtualenv in the checkout" (0 passed, 1 failed).
    """

    def test_the_rust_job_gives_the_contract_suite_a_python_3_14_with_dev_deps(self):
        rust = _product_ci_jobs()["rust"]
        setup = [step for step in rust["steps"] if str(step.get("uses", "")).startswith("actions/setup-python@")]
        self.assertEqual(len(setup), 1, "the rust job should set up one Python")
        self.assertEqual(setup[0]["with"]["python-version"], "3.14")
        install = [step for step in rust["steps"] if "product/engine/requirements-dev.txt" in str(step.get("run", ""))]
        self.assertEqual(len(install), 1, "the rust job should install the product engine deps")
        suite = [step for step in rust["steps"] if step.get("name") == "Rust suite (output withheld)"]
        self.assertEqual(len(suite), 1)
        self.assertEqual((suite[0].get("env") or {}).get("BLOWHORN_CONTRACT_PYTHON"), "python")
        setup_index = rust["steps"].index(setup[0])
        install_index = rust["steps"].index(install[0])
        suite_index = rust["steps"].index(suite[0])
        self.assertLess(setup_index, install_index)
        self.assertLess(install_index, suite_index)


if __name__ == "__main__":
    unittest.main()
