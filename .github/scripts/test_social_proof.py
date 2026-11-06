"""Test local company-logo data and every social-proof attribution slot."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class CompanyLogoDataTests(unittest.TestCase):
    def test_each_company_has_a_local_logo_or_an_explicit_hold(self):
        items = json.loads((ROOT / "data/testimonials.json").read_text())["items"]
        ticker = json.loads((ROOT / "data/user_logos.json").read_text())["items"]
        ticker_paths = {item["logo"] for item in ticker}
        for item in items:
            with self.subTest(company=item["company"]):
                logo = item.get("companyLogo")
                if not logo:
                    self.assertTrue(item.get("companyLogoNote"), "Missing logo or documented hold")
                    continue
                self.assertTrue(logo.startswith("/assets/orgs/"))
                self.assertTrue((ROOT / "static" / logo.lstrip("/")).is_file())
                self.assertIn(logo, ticker_paths)
                self.assertIn(Path(logo).name, (ROOT / "static/assets/brand/LICENSES.md").read_text())


@unittest.skipUnless(shutil.which("hugo"), "Hugo is required for template integration tests")
class SocialProofRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        for path in ("layouts/_partials", "content", "data"):
            (root / path).mkdir(parents=True)
        shutil.copy(ROOT / "layouts/_partials/social-proof.html", root / "layouts/_partials")
        # The fixture isolates attribution markup, not the independent card dealer.
        (root / "layouts/_partials/card-variant.html").write_text("card-paper")
        (root / "hugo.toml").write_text('baseURL = "https://example.test/"\n')
        (root / "content/_index.md").write_text("---\ntitle: Proof fixture\n---\n")
        slots = ("grid", "rotating", "interlude", "closing", "ticker")
        (root / "layouts/home.html").write_text("".join(
            f'<div data-slot="{slot}">{{{{ partial "social-proof.html" (dict "slot" "{slot}") }}}}</div>'
            for slot in slots
        ))
        items = [
            {"name": "A Person", "role": "Engineer", "company": "One Company",
             "quote": "An existing quote.", "picture": "/avatar.jpg",
             "companyLogo": "/assets/orgs/one.svg", "placements": list(slots)},
            {"name": "B Person", "role": "Engineer", "company": "Held Company",
             "quote": "Another existing quote.", "placements": list(slots)},
            {"name": "Draft Person", "company": "Draft Company", "quote": "Draft quote.",
             "placeholder": True, "companyLogo": "/assets/orgs/draft.svg", "placements": list(slots)},
        ]
        (root / "data/testimonials.json").write_text(json.dumps({"items": items}))
        (root / "data/user_logos.json").write_text(json.dumps({"items": [
            {"name": "Ticker Only", "logo": "/assets/orgs/ticker.svg"}
        ]}))
        subprocess.run(["hugo", "--source", str(root), "--environment", "production",
                        "--cleanDestinationDir"], check=True, capture_output=True, text=True)
        html = (root / "public/index.html").read_text()
        cls.slots = dict(re.findall(r'<div data-slot="([^"]+)">(.*?)(?=<div data-slot=|$)', html, re.S))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_attribution_slots_render_a_decorative_local_company_logo(self):
        for slot in ("grid", "rotating", "interlude", "closing"):
            with self.subTest(slot=slot):
                logos = re.findall(r'<img\b[^>]*class="proof-company-logo"[^>]*>', self.slots[slot])
                self.assertEqual(len(logos), 1)
                self.assertIn('src="/assets/orgs/one.svg"', logos[0])
                self.assertIn('alt=""', logos[0])
                self.assertIn('loading="lazy"', logos[0])
                self.assertNotIn("draft.svg", self.slots[slot])

    def test_missing_logo_keeps_the_person_and_company_attribution(self):
        for slot in ("grid", "rotating", "closing"):
            with self.subTest(slot=slot):
                self.assertIn("B Person", self.slots[slot])
                self.assertIn("Held Company", self.slots[slot])
                self.assertNotIn('src=""', self.slots[slot])

    def test_ticker_remains_independent_of_testimonials(self):
        self.assertEqual(self.slots["ticker"].count('src="/assets/orgs/ticker.svg"'), 2)
        self.assertNotIn("one.svg", self.slots["ticker"])


if __name__ == "__main__":
    unittest.main()
