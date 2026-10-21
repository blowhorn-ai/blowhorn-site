#!/usr/bin/env python3
"""The action matrix and the docs all-actions table must match the data.

Run with `make test-scripts` (CI runs it too). Each test builds a small
fixture site from a copy of data/ and checks that check_action_matrix.py
passes it, then breaks one thing and checks that the check names it.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import check_action_matrix as check

ROOT = Path(__file__).resolve().parents[2]
DOCS_PAGE = """---
title: All actions
---

One row per action and platform.

{{< all-actions >}}
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


DOT = '<svg class="mx-mark mx-dot"><circle/></svg>'
CLOCK = '<svg class="mx-mark mx-soon"><circle/></svg>'


def render_matrix(want: dict, supported_mark: str = DOT, soon_mark: str = CLOCK) -> str:
    """Markup with the attributes layouts/action-matrix.html writes."""
    heads = []
    for p in want["platforms"]:
        name = want["names"][p]
        if p in want["soon"]:
            label = want["labels"]["coming-soon"]
            heads.append(
                f'<th data-matrix-platform="{p}" data-status="coming-soon"><a href="/x/" title="{name}: {label}">{soon_mark}</a></th>'
            )
        else:
            heads.append(f'<th data-matrix-platform="{p}"><a href="/x/" title="{name}">logo</a></th>')
    body = []
    actions_by_group: dict[str, list[str]] = {}
    data = json.loads((ROOT / "data/actions.json").read_text(encoding="utf-8"))
    group_of = {a["id"]: a["group"] for a in data["actions"]}
    for aid in want["actions"]:
        actions_by_group.setdefault(group_of[aid], []).append(aid)
    for gid in want["groups"]:
        rows = []
        for aid in actions_by_group.get(gid, []):
            cells = []
            for pid in want["platforms"]:
                status, href = want["cells"][f"{aid}:{pid}"]
                if status == "supported":
                    inner = f'<a href="{href}">{supported_mark}<span>{aid} on {pid}</span></a>'
                else:
                    inner = f'<span>{want["labels"][status]}</span>'
                cells.append(f'<td data-matrix-cell="{aid}:{pid}" data-status="{status}">{inner}</td>')
            rows.append(f'<tr data-matrix-action="{aid}"><th>{aid}</th>{"".join(cells)}</tr>')
        body.append(f'<tbody data-matrix-group="{gid}">{"".join(rows)}</tbody>')
    return f'<div data-action-matrix><table><thead><tr><td></td>{"".join(heads)}</tr></thead>{"".join(body)}</table></div>'


def render_table(want: dict, docs: dict, extra: str = "") -> str:
    """Markup with the attributes layouts/_partials/action-table.html writes."""
    rows = []
    for key in want["supported_keys"]:
        status, href = want["cells"][key]
        pid = key.split(":", 1)[1]
        name = want["names"][pid]
        rows.append(
            f'<tr data-row="{key}" data-status="{status}"><th><a href="{href}">a</a></th>'
            f'<td data-label="Platform"><a href="{docs[pid]}" title="{name}"><img src="l.svg" alt="{name}"></a></td>'
            f'<td data-label="What it does">{extra}does</td></tr>'
        )
    return f'<section data-action-table><table><tbody>{"".join(rows)}</tbody></table></section>'


class ActionMatrixCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "repo"
        self.build = self.tmp / "public"
        shutil.copytree(ROOT / "data", self.root / "data")
        self.integrations = json.loads((self.root / "data/integrations.json").read_text(encoding="utf-8"))
        self.matrix = self.integrations["matrix"]
        write(self.root / "content/en" / self.matrix["docsPath"].strip("/") / "_index.md", DOCS_PAGE)
        self.render()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def render(self, want=None, matrix_kw=None, table_extra=""):
        want = want or check.expected(self.root)
        docs = {p["id"]: p["docs"] for p in self.integrations["platforms"]}
        # Platform docs pages carry an #action-<id> section per listed action.
        for p in self.integrations["platforms"]:
            ids = check.yaml_action_ids(self.root, p["id"]) or []
            sections = "".join(f'<section id="action-{a}"></section>' for a in ids)
            write(check.built_file(self.build, p["docs"]), f"<main>{sections}</main>")
        write(check.built_file(self.build, self.matrix["path"]), render_matrix(want, **(matrix_kw or {})))
        write(check.built_file(self.build, self.matrix["docsPath"]), render_table(want, docs, table_extra))
        link = f'<a href="{self.matrix["path"]}" data-matrix-link>all</a>'
        write(check.built_file(self.build, "/"), link)
        write(check.built_file(self.build, "/integrations/"), link)
        return want

    def problems(self):
        check._page_ids.clear()
        return check.run(self.root, self.build)

    def edit_json(self, rel, change):
        path = self.root / rel
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def assert_flags(self, needle):
        found = self.problems()
        self.assertTrue(any(needle in p for p in found), f"{needle!r} not in {found}")

    # ---------- passing ----------

    def test_checked_in_data_passes(self):
        self.assertEqual(check.check_source(ROOT), [])

    def test_fixture_passes(self):
        self.assertEqual(self.problems(), [])

    def test_every_action_and_platform_is_a_cell(self):
        want = check.expected(self.root)
        actions = json.loads((ROOT / "data/actions.json").read_text(encoding="utf-8"))["actions"]
        self.assertEqual(len(want["keys"]), len(actions) * len(self.integrations["platforms"]))

    # ---------- data drift ----------

    def test_unknown_group_fails(self):
        self.edit_json("data/actions.json", lambda d: d["actions"][0].update(group="nowhere"))
        self.assert_flags("not a groups[].id")

    def test_empty_group_fails(self):
        self.edit_json("data/actions.json", lambda d: d["groups"].append({"id": "spare", "name": "Spare", "summary": "Empty."}))
        self.assert_flags("group spare holds no action")

    def test_exception_order_fails(self):
        self.edit_json("data/integrations.json", lambda d: d["matrix"]["exceptions"].reverse())
        self.assert_flags("matrix exceptions")

    def test_supported_after_coming_soon_fails(self):
        self.edit_json("data/integrations.json", lambda d: d["platforms"].reverse())
        self.assert_flags("follows a coming-soon one")

    def test_unknown_yaml_action_fails(self):
        path = self.root / "data/platforms/x.yaml"
        path.write_text(path.read_text(encoding="utf-8") + "  - id: teleport\n", encoding="utf-8")
        self.assert_flags("unknown action 'teleport'")

    # ---------- built drift ----------

    def test_stale_page_after_yaml_change_fails(self):
        path = self.root / "data/platforms/github.yaml"
        path.write_text(path.read_text(encoding="utf-8") + "  - id: post\n", encoding="utf-8")
        found = self.problems()
        self.assertTrue(any("post:github is 'none', data says 'supported'" in p for p in found), found)

    def test_missing_cell_fails(self):
        want = check.expected(self.root)
        key = want["keys"][0]
        want["keys"] = want["keys"][1:]
        want["supported_keys"] = [k for k in want["supported_keys"] if k != key]
        self.render(want)
        self.assert_flags(f"missing 1 cell(s): {key}")

    def test_out_of_order_fails(self):
        want = check.expected(self.root)
        want["keys"] = list(reversed(want["keys"]))
        want["supported_keys"] = list(reversed(want["supported_keys"]))
        self.render(want)
        self.assert_flags("out of order")

    def test_docs_table_lists_supported_pairs_only(self):
        want = check.expected(self.root)
        self.assertTrue(want["supported_keys"])
        self.assertTrue(all(want["cells"][k][0] == "supported" for k in want["supported_keys"]))
        self.assertLess(len(want["supported_keys"]), len(want["keys"]))

    def test_supported_word_fails(self):
        self.render(table_extra="Supported. ")
        self.assert_flags("renders the word 'supported'")

    def test_check_mark_fails(self):
        self.render(matrix_kw={"supported_mark": '<svg class="mx-mark mx-yes"><path/></svg>'})
        found = self.problems()
        self.assertTrue(any("renders a check mark" in p for p in found), found)
        self.assertTrue(any("want only the neutral dot" in p for p in found), found)

    def test_soon_column_without_clock_fails(self):
        self.render(matrix_kw={"soon_mark": ""})
        self.assert_flags("lacks its one clock mark")

    def test_exception_label_drift_fails(self):
        self.edit_json("data/integrations.json", lambda d: d["matrix"]["exceptions"][1].update(label="Absent"))
        self.assert_flags("want the none label 'Absent'")

    def test_status_mark_in_docs_table_fails(self):
        self.render(table_extra=CLOCK)
        self.assert_flags("shows a status mark")

    def test_docs_logo_without_name_fails(self):
        page = check.built_file(self.build, self.matrix["docsPath"])
        page.write_text(page.read_text(encoding="utf-8").replace('alt="LinkedIn"', 'alt=""', 1), encoding="utf-8")
        self.assert_flags("platform logo must carry alt and title 'LinkedIn'")

    def test_wrong_status_fails(self):
        want = check.expected(self.root)
        want["cells"] = dict(want["cells"])
        want["cells"]["post:linkedin"] = ("none", None)
        self.render(want)
        self.assert_flags("post:linkedin is 'none', data says 'supported'")

    def test_link_on_exception_cell_fails(self):
        want = check.expected(self.root)
        want["cells"] = dict(want["cells"])
        want["cells"]["post:youtube"] = ("supported", "/docs/reference/platforms/youtube/")
        self.render(want)
        self.assert_flags("post:youtube is 'supported', data says 'coming-soon'")

    def test_dead_anchor_fails(self):
        target = check.built_file(self.build, "/docs/reference/platforms/linkedin/")
        target.write_text("<main></main>", encoding="utf-8")
        self.assert_flags("has no id='action-post'")

    def test_missing_platform_page_fails(self):
        check.built_file(self.build, "/docs/reference/platforms/x/").unlink()
        self.assert_flags("/docs/reference/platforms/x/#action-post, which has no built page")

    def test_home_without_matrix_link_fails(self):
        check.built_file(self.build, "/").write_text("<main></main>", encoding="utf-8")
        self.assert_flags("/ does not link to the action matrix")

    def test_integrations_without_matrix_link_fails(self):
        check.built_file(self.build, "/integrations/").write_text("<main></main>", encoding="utf-8")
        self.assert_flags("/integrations/ does not link to the action matrix")

    def test_hand_written_docs_table_fails(self):
        page = self.root / "content/en" / self.matrix["docsPath"].strip("/") / "_index.md"
        page.write_text(DOCS_PAGE + "\n| Action | Platform |\n| --- | --- |\n| Post | X |\n", encoding="utf-8")
        self.assert_flags("hand-written action table")

    def test_docs_page_without_shortcode_fails(self):
        page = self.root / "content/en" / self.matrix["docsPath"].strip("/") / "_index.md"
        page.write_text("---\ntitle: All actions\n---\n", encoding="utf-8")
        self.assert_flags("must call")

    def test_em_dash_fails(self):
        page = check.built_file(self.build, self.matrix["path"])
        page.write_text(page.read_text(encoding="utf-8") + "\u2014", encoding="utf-8")
        self.assert_flags("contains an em dash")

    def test_missing_matrix_page_fails(self):
        check.built_file(self.build, self.matrix["path"]).unlink()
        self.assert_flags("was not built")


if __name__ == "__main__":
    unittest.main()
