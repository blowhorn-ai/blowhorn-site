"""Regression tests for the production Google Analytics template."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AnalyticsTemplateTests(unittest.TestCase):
    def test_analytics_loads_without_a_cookie_choice(self):
        template = (ROOT / "layouts/_partials/analytics.html").read_text()

        self.assertIn(
            '<script async src="https://www.googletagmanager.com/gtag/js?id={{ . | urlquery }}"></script>',
            template,
        )
        self.assertIn("analytics_storage: 'granted'", template)
        self.assertIn("ad_storage: 'denied'", template)
        self.assertNotIn("consent.js", template)

    def test_cookie_choices_cannot_control_analytics(self):
        self.assertFalse((ROOT / "assets/js/consent.js").exists())
        self.assertFalse((ROOT / "layouts/_partials/consent.html").exists())
        footer = (ROOT / "layouts/_partials/footer.html").read_text()

        self.assertNotIn("data-consent", footer)
        self.assertNotIn('partial "consent.html"', footer)


if __name__ == "__main__":
    unittest.main()
