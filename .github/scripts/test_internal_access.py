"""Tests for internal_access.py: the Access application must stay default-deny."""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(__file__))
import internal_access as ia  # noqa: E402

CFG = {
    "hostname": "internal.blowhorn.ai",
    "app_name": "app",
    "policy_name": "pol",
    "session_duration": "24h",
    "allowed_emails": ["lee.calcote@layer5.io"],
}


def fake_call(app, policy):
    def call(method, path, permission, body=None):
        if "/access/apps/" in path:
            return {"result": app}
        if "/access/policies/" in path:
            return {"result": policy}
        raise AssertionError(path)
    return call


GOOD_APP = {"domain": "internal.blowhorn.ai", "type": "self_hosted", "policies": [{"id": "p1"}], "aud": "x"}
GOOD_POLICY = {"decision": "allow", "include": [{"email": {"email": "lee.calcote@layer5.io"}}], "exclude": [], "require": []}


class VerifyApp(unittest.TestCase):
    def setUp(self):
        os.environ["CLOUDFLARE_ACCOUNT_ID"] = "acct"

    def run_verify(self, app, policy):
        with mock.patch.object(ia, "call", fake_call(app, policy)):
            ia.verify_app(CFG, "a1", "p1")

    def test_good(self):
        self.run_verify(GOOD_APP, GOOD_POLICY)

    def test_everyone_rule_rejected(self):
        bad = dict(GOOD_POLICY, include=GOOD_POLICY["include"] + [{"everyone": {}}])
        with self.assertRaises(SystemExit):
            self.run_verify(GOOD_APP, bad)

    def test_domain_rule_rejected(self):
        bad = dict(GOOD_POLICY, include=[{"email_domain": {"domain": "layer5.io"}}])
        with self.assertRaises(SystemExit):
            self.run_verify(GOOD_APP, bad)

    def test_bypass_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verify(GOOD_APP, dict(GOOD_POLICY, decision="bypass"))

    def test_extra_policy_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verify(dict(GOOD_APP, policies=[{"id": "p1"}, {"id": "p2"}]), GOOD_POLICY)

    def test_email_drift_rejected(self):
        bad = dict(GOOD_POLICY, include=[{"email": {"email": "someone@example.com"}}])
        with self.assertRaises(SystemExit):
            self.run_verify(GOOD_APP, bad)


class MatchingApps(unittest.TestCase):
    def test_matches_host_paths_and_subdomains(self):
        apps = [
            {"id": 1, "domain": "internal.blowhorn.ai"},
            {"id": 2, "domain": "internal.blowhorn.ai/internal/finance"},
            {"id": 3, "domain": "x.internal.blowhorn.ai"},
            {"id": 4, "domain": "tells.blowhorn.ai"},
            {"id": 5, "domain": "other.example", "self_hosted_domains": ["internal.blowhorn.ai/a"]},
        ]
        self.assertEqual([a["id"] for a in ia.matching_apps(apps, "internal.blowhorn.ai")], [1, 2, 3, 5])


class Config(unittest.TestCase):
    def test_repository_allow_list_is_named_emails(self):
        cfg = ia.load_config(ia.DEFAULT_CONFIG)
        self.assertTrue(cfg["allowed_emails"])
        for e in cfg["allowed_emails"]:
            self.assertRegex(e, r"^[^@*\s]+@[^@*\s]+\.[a-z]+$")


if __name__ == "__main__":
    unittest.main()
