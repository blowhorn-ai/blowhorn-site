"""Static contract tests for the API reference viewer's templates, script and
stylesheet. They do not render Hugo (a faithful render needs the whole site);
the render is checked by building a temporary page against the synthetic
fixture (docs/api-reference.md, "Verifying a change"), and the built page by
check_api_reference.py once a spec is configured.
"""

import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARTIALS = ROOT / "layouts" / "_partials" / "rest-apis"
LAYOUT = ROOT / "layouts" / "docs" / "rest-apis.html"
CSS = ROOT / "assets" / "css" / "api-reference.css"
JS = ROOT / "assets" / "js" / "api-reference.js"


def read(path):
    return path.read_text(encoding="utf-8")


def templates():
    return [LAYOUT, *sorted(PARTIALS.glob("*.html"))]


class TestConfigurableInput(unittest.TestCase):
    def spec_param(self):
        return tomllib.loads(read(ROOT / "hugo.toml"))["params"]["apiReference"]["spec"]

    def test_spec_path_is_a_site_param_inside_the_project(self):
        spec = self.spec_param()
        self.assertIsInstance(spec, str)
        self.assertFalse(spec.startswith("/") or ".." in spec, spec)

    def test_spec_partial_reads_the_param_not_a_fixed_file(self):
        text = read(PARTIALS / "spec.html")
        self.assertIn("site.Params.apiReference", text)
        self.assertNotRegex(text, r'openapi\.ya?ml|data/openapi')
        # A missing or unusable spec must fail the build, not render nothing.
        self.assertGreaterEqual(text.count("errorf"), 4)

    def test_a_page_uses_the_layout_only_when_a_spec_is_configured(self):
        users = [p for p in (ROOT / "content").rglob("*.md")
                 if re.search(r"^layout:\s*rest-apis\s*$", read(p), re.MULTILINE)]
        spec = self.spec_param()
        if not spec:
            self.assertEqual(users, [], "a page uses layout rest-apis but params.apiReference.spec "
                                        "is empty (docs/api-reference.md)")
        else:
            self.assertTrue((ROOT / spec).is_file(), f"params.apiReference.spec {spec} is missing")
        for page in users:  # sync-docs.py deletes any other docs page it does not know
            if "content/en/docs/" in page.as_posix():
                self.assertEqual(page.name, "_index.md", page)


class TestPublicOnly(unittest.TestCase):
    def test_audience_is_public_and_never_cloud(self):
        text = read(PARTIALS / "is-public.html")
        self.assertIn('"public"', text)
        self.assertNotIn("cloud", text.replace("opt-in", "").split("*/")[1])

    def test_viewer_filters_with_the_audience_partial(self):
        self.assertIn("rest-apis/is-public.html", read(PARTIALS / "viewer.html"))

    def test_viewer_never_reads_servers_or_external_docs(self):
        for path in templates():
            body = read(path)
            body = re.sub(r"\{\{-?\s*/\*.*?\*/\s*-?\}\}", "", body, flags=re.DOTALL)  # comments
            self.assertNotRegex(body, r'"servers"|externalDocs|Try this', path.name)

    def test_the_not_an_http_api_notice_is_in_the_viewer(self):
        text = read(PARTIALS / "viewer.html")
        self.assertIn("Not an HTTP API", text)
        self.assertIn("does not run an HTTP REST listener", text)


class TestSiteRules(unittest.TestCase):
    def test_no_outside_host_and_no_private_repository(self):
        for path in [*templates(), CSS, JS]:
            body = read(path)
            self.assertNotRegex(body, r"https?://(?!www\.apache\.org)", path.name)
            self.assertNotRegex(body, r"blowhorn-ai/blowhorn(?![\w-])", path.name)

    def test_stylesheet_uses_tokens_only(self):
        css = re.sub(r"/\*.*?\*/", "", read(CSS), flags=re.DOTALL)
        self.assertNotRegex(css, r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")
        self.assertNotRegex(css, r"border-(left|right|inline-start|inline-end)")
        self.assertNotRegex(css, r"(margin|padding)[a-z-]*:\s*[1-9][0-9]*px")

    def test_no_inline_style_or_script(self):
        for path in templates():
            body = read(path)
            self.assertNotIn("style=", body, path.name)
            self.assertNotRegex(body, r"<script(?![^>]*\bsrc=)", path.name)

    def test_native_disclosure_and_no_em_dash(self):
        viewer = read(PARTIALS / "viewer.html")
        self.assertIn("<details", viewer)
        self.assertIn("<summary>", viewer)
        for path in [*templates(), CSS, JS]:
            self.assertNotIn("—", read(path), path.name)


if __name__ == "__main__":
    unittest.main()
