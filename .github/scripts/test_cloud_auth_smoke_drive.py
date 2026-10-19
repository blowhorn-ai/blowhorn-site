"""Unit tests for cloud-auth-smoke/drive.py's offline helpers (no network, no CLI)."""

import importlib.util
import pathlib
import sys
import unittest

SPEC = importlib.util.spec_from_file_location(
    "drive", pathlib.Path(__file__).parent / "cloud-auth-smoke" / "drive.py")
drive = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(drive)


class RedactTest(unittest.TestCase):
    def test_a_logged_url_keeps_host_and_path_and_drops_every_query_value(self):
        url = "http://127.0.0.1:5999/callback?bh_state=s&token=SECRET&ref=r"
        self.assertEqual(drive.redact(url), "http://127.0.0.1:5999/callback")
        self.assertNotIn("SECRET", drive.redact("https://cloud.blowhorn.ai/login?flow=f&login_challenge=SECRET"))


class TrailingJsonTest(unittest.TestCase):
    def test_the_cli_answer_after_its_authorize_line_is_the_one_read(self):
        out = '{"event": "authorize", "authorize_url": "https://x/login?source=s"}\n{\n  "ok": true,\n  "signed_in": true\n}\n'
        self.assertEqual(drive.trailing_json(out), {"ok": True, "signed_in": True})

    def test_no_json_is_none(self):
        self.assertIsNone(drive.trailing_json("ERROR: nothing\n"))


class FlowTest(unittest.TestCase):
    def test_a_page_without_a_flow_is_a_failure_that_names_the_page(self):
        with self.assertRaises(drive.Failure) as ctx:
            drive.flow_id("https://cloud.blowhorn.ai/registered?secret=1")
        self.assertIn("https://cloud.blowhorn.ai/registered", str(ctx.exception))
        self.assertNotIn("secret", str(ctx.exception))

    def test_messages_gather_the_flow_and_its_fields(self):
        flow = {"messages": [{"text": "Account not active yet. Did you forget to verify your email address?"}],
                "nodes": [{"attributes": {"name": "password"}, "messages": [{"text": "too short"}]}]}
        self.assertEqual(len(drive.messages(flow)), 2)


CONSENT_PAGE = """<!doctype html><html><body><h1>Allow blowhorn to sign in as a@example.com?</h1>
<form method="get" action="/search"><input type="hidden" name="q" value="decoy"></form>
<form method="post" action="/api/identity/native/authorize">
<input type="hidden" name="clientName" value="blowhorn">
<input type="hidden" name="port" value="53682">
<input type="hidden" name="codeChallenge" value="abc-_123">
<input type="hidden" name="codeChallengeMethod" value="S256">
<input type="hidden" name="state" value="s&amp;t">
<input type="text" name="ignored" value="x">
<button type="submit">Allow</button><a href="/">Cancel</a>
</form></body></html>"""


class ConsentFormTest(unittest.TestCase):
    def test_allow_submits_the_native_forms_hidden_fields_unchanged(self):
        action, fields = drive.consent_form(CONSENT_PAGE)
        self.assertEqual(action, "/api/identity/native/authorize")
        self.assertEqual(fields, {"clientName": "blowhorn", "port": "53682", "codeChallenge": "abc-_123",
                                  "codeChallengeMethod": "S256", "state": "s&t"})

    def test_a_page_without_the_native_form_is_a_failure(self):
        with self.assertRaises(drive.Failure):
            drive.consent_form("<form action=\"/search\"><input type=\"hidden\" name=\"q\" value=\"x\"></form>")


class LoginArgsTest(unittest.TestCase):
    def _engine(self, help_text):
        import tempfile, textwrap
        root = pathlib.Path(tempfile.mkdtemp())
        (root / "bin").mkdir()
        (root / "engine").mkdir()
        (root / "engine" / "blowhorn.py").write_text(f"print({help_text!r})\n")
        python = root / "bin" / "python"
        python.write_text(textwrap.dedent(f"""\
            #!/bin/sh
            exec {sys.executable} "$@"
            """))
        python.chmod(0o755)
        return root

    def test_a_release_with_redirect_answers_on_the_loopback_route(self):
        cli = drive.Cli(self._engine("Options: --redirect [loopback|app] --json"), None)
        self.assertEqual(cli.login_args(), ["--redirect", "loopback", "--json"])

    def test_a_pkce_release_needs_only_json(self):
        cli = drive.Cli(self._engine("Options: --sign-up --no-browser --json"), None)
        self.assertEqual(cli.login_args(), ["--json"])


if __name__ == "__main__":
    unittest.main()
