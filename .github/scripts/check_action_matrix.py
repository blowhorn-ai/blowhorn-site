#!/usr/bin/env python3
"""Fail if the action matrix or the docs all-actions table drifts from the data.

Both views render from layouts/_partials/action-matrix.html:

- the site matrix at data/integrations.json matrix.path (/integrations/actions/),
- the docs table at matrix.docsPath (/docs/reference/platforms/actions/),
  through the {{< all-actions >}} shortcode.

Expected cells come straight from the data: every action in data/actions.json
(rows, in groups[] order, then vocabulary order) by every platform in
data/integrations.json (columns, catalog order). A cell is supported when the
platform's data/platforms/<id>.yaml lists the action, coming-soon when the
platform is coming soon, and none otherwise.

Status is shown by exception. A supported matrix cell is a link to
<docs>#action-<id> holding only the neutral dot (mx-dot); coming-soon and none
cells hold no link and no mark, only their matrix.exceptions label as
screen-reader text; a coming-soon platform's column head carries the one
clock (mx-soon). The docs table lists supported pairs only, with no status
column, and a logo-only platform cell named by alt. Neither view may render
the word "supported" or a check mark.

--source checks the data alone (run by make check-schemas): every action's
group is a groups[].id, every group holds an action, platform YAML uses only
vocabulary ids, matrix exceptions are coming-soon then none, and supported
platforms come before coming-soon ones.

With a build directory it also checks the built pages: the matrix and the
table hold exactly the expected cells and rows with the expected status and
link, in order; every link resolves to a built page and, with a #fragment,
to an element with that id there; /integrations/ and the home page link to
the matrix; the docs page calls the shortcode and carries no hand-written
table; neither page carries an em dash.

Usage: check_action_matrix.py --source
       check_action_matrix.py [BUILD_DIR]
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
EM_DASH = "\u2014"
EXCEPTIONS = ("coming-soon", "none")
SUPPORTED_WORD_RE = re.compile(r"\bsupported\b", re.I)
REGIONS = ("data-action-matrix", "data-action-table")
SHORTCODE_RE = re.compile(r"\{\{<\s*all-actions\s*>\}\}")
MD_TABLE_RE = re.compile(r"^\|\s*Action\s*\|", re.M)


# ---------- data ----------

def load_json(root: Path, rel: str) -> dict:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def yaml_action_ids(root: Path, platform_id: str) -> list[str] | None:
    path = root / "data" / "platforms" / f"{platform_id}.yaml"
    if not path.is_file():
        return None
    return [
        line.split("id:", 1)[1].strip().strip("\"'")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("  - id:")
    ]


def check_source(root: Path) -> list[str]:
    problems: list[str] = []
    actions = load_json(root, "data/actions.json")
    integrations = load_json(root, "data/integrations.json")
    group_ids = [g["id"] for g in actions.get("groups", [])]
    if not group_ids:
        problems.append("data/actions.json has no groups")
    if len(set(group_ids)) != len(group_ids):
        problems.append("data/actions.json groups repeat an id")
    vocab = [a["id"] for a in actions["actions"]]
    if len(set(vocab)) != len(vocab):
        problems.append("data/actions.json actions repeat an id")
    used = set()
    for a in actions["actions"]:
        group = a.get("group")
        if group not in group_ids:
            problems.append(f"action {a['id']} has group {group!r}, not a groups[].id")
        else:
            used.add(group)
    for gid in group_ids:
        if gid not in used:
            problems.append(f"group {gid} holds no action")

    matrix = integrations.get("matrix")
    if not matrix:
        problems.append("data/integrations.json has no matrix block")
    else:
        ids = tuple(s.get("id") for s in matrix.get("exceptions", []))
        if ids != EXCEPTIONS:
            problems.append(f"matrix exceptions are {ids}, want {EXCEPTIONS}")

    seen_soon = False
    for item in integrations["platforms"]:
        if item["status"] == "coming-soon":
            seen_soon = True
        elif seen_soon:
            problems.append(
                f"supported platform {item['id']} follows a coming-soon one; list supported platforms first"
            )
        ids = yaml_action_ids(root, item["id"])
        if item["status"] == "supported" and ids is None:
            problems.append(f"supported platform {item['id']} has no data/platforms/{item['id']}.yaml")
        for aid in ids or []:
            if aid not in vocab:
                problems.append(f"data/platforms/{item['id']}.yaml lists unknown action {aid!r}")
    return problems


def platform_name(root: Path, item: dict) -> str:
    path = root / "data" / "platforms" / f"{item['id']}.yaml"
    if item["status"] == "supported" and path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("name:"):
                return line.split(":", 1)[1].strip().strip("\"'")
    return item.get("name", item["id"])


def expected(root: Path) -> dict:
    """Rows, columns and cells both views must show, from the data alone."""
    actions = load_json(root, "data/actions.json")
    integrations = load_json(root, "data/integrations.json")
    platforms = integrations["platforms"]
    order: list[str] = []
    groups: list[str] = []
    for g in actions["groups"]:
        members = [a["id"] for a in actions["actions"] if a.get("group") == g["id"]]
        if members:
            groups.append(g["id"])
        order.extend(members)
    cells: dict[str, tuple[str, str | None]] = {}
    keys: list[str] = []
    for aid in order:
        for item in platforms:
            pid = item["id"]
            docs = item["docs"]
            listed = yaml_action_ids(root, pid) or []
            if item["status"] == "coming-soon":
                cell = ("coming-soon", None)
            elif aid in listed:
                cell = ("supported", f"{docs}#action-{aid}")
            else:
                cell = ("none", None)
            key = f"{aid}:{pid}"
            keys.append(key)
            cells[key] = cell
    labels = {e["id"]: e["label"] for e in integrations.get("matrix", {}).get("exceptions", [])}
    return {
        "labels": labels,
        "soon": [p["id"] for p in platforms if p["status"] == "coming-soon"],
        "names": {p["id"]: platform_name(root, p) for p in platforms},
        "supported_keys": [k for k in keys if cells[k][0] == "supported"],
        "groups": groups,
        "actions": order,
        "platforms": [p["id"] for p in platforms],
        "keys": keys,
        "cells": cells,
        "matrix": integrations.get("matrix", {}),
    }


# ---------- built HTML ----------

class Collector(HTMLParser):
    """Collect matrix heads and cells, table rows, ids, links and the text
    (plus title, alt and aria-label values) inside the two view regions."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.platforms: list[str] = []
        self.heads: dict[str, dict] = {}
        self.groups: list[str] = []
        self.actions: list[str] = []
        self.cells: list[dict] = []
        self.rows: list[dict] = []
        self.hrefs: list[str] = []
        self.markers: dict[str, int] = {}
        self.region_text: list[str] = []
        self.region_classes: list[str] = []
        self._stack: list[str] = []
        self._region_depth: int | None = None
        self._head: dict | None = None
        self._cell: dict | None = None
        self._row: dict | None = None
        self._in_th = False
        self._in_platform_td = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        void = tag in ("img", "input", "col", "br", "meta", "link", "path", "circle")
        if not void:
            self._stack.append(tag)
        if a.get("id"):
            self.ids.add(a["id"])
        for marker in REGIONS + ("data-matrix-link",):
            if marker in a:
                self.markers[marker] = self.markers.get(marker, 0) + 1
                if marker in REGIONS and self._region_depth is None:
                    self._region_depth = len(self._stack)
        if self._region_depth is not None:
            for key in ("title", "alt", "aria-label"):
                if a.get(key):
                    self.region_text.append(a[key])
            if a.get("class"):
                self.region_classes.extend(a["class"].split())
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
        classes = (a.get("class") or "").split()
        if "data-matrix-platform" in a:
            pid = a["data-matrix-platform"]
            self.platforms.append(pid)
            self._head = {"status": a.get("data-status", ""), "marks": [], "title": None, "depth": len(self._stack)}
            self.heads[pid] = self._head
        if "data-matrix-group" in a:
            self.groups.append(a["data-matrix-group"])
        if "data-matrix-action" in a:
            self.actions.append(a["data-matrix-action"])
        if tag == "td" and "data-matrix-cell" in a:
            self._cell = {"key": a["data-matrix-cell"], "status": a.get("data-status", ""), "href": None, "marks": [], "text": ""}
        if tag == "tr" and "data-row" in a:
            self._row = {"key": a["data-row"], "href": None, "alt": None, "title": None, "marks": [], "cells": 0}
        if tag == "svg" and "mx-mark" in classes:
            mark = [c for c in classes if c != "mx-mark"]
            for target in (self._head, self._cell, self._row):
                if target is not None:
                    target["marks"].extend(mark)
        if tag == "a":
            if self._head is not None and self._head["title"] is None:
                self._head["title"] = a.get("title")
            if self._cell is not None and self._cell["href"] is None:
                self._cell["href"] = a.get("href")
            if self._row is not None and self._in_th and self._row["href"] is None:
                self._row["href"] = a.get("href")
            if self._row is not None and self._in_platform_td:
                self._row["title"] = a.get("title")
        if self._row is not None:
            if tag == "th":
                self._in_th = True
            elif tag == "td":
                self._row["cells"] += 1
                self._in_platform_td = a.get("data-label") == "Platform"
            elif tag == "img" and self._in_platform_td:
                self._row["alt"] = a.get("alt")

    def handle_data(self, data):
        if self._region_depth is not None:
            self.region_text.append(data)
        if self._cell is not None:
            self._cell["text"] += data

    def handle_endtag(self, tag):
        if tag == "td" and self._cell is not None:
            self._cell["text"] = " ".join(self._cell["text"].split())
            self.cells.append(self._cell)
            self._cell = None
        if self._row is not None:
            if tag == "th":
                self._in_th = False
            if tag == "td":
                self._in_platform_td = False
            if tag == "tr":
                self.rows.append(self._row)
                self._row = None
        if self._stack and self._stack[-1] == tag:
            if self._head is not None and tag == "th" and len(self._stack) == self._head["depth"]:
                self._head = None
            if self._region_depth is not None and len(self._stack) == self._region_depth:
                self._region_depth = None
            self._stack.pop()


def built_file(build_dir: Path, path: str) -> Path:
    path = path.strip("/")
    if not path:
        return build_dir / "index.html"
    if path.endswith(".html"):
        return build_dir / path
    return build_dir / path / "index.html"


def parse(path: Path) -> Collector:
    c = Collector()
    c.feed(path.read_text(encoding="utf-8"))
    return c


_page_ids: dict[Path, set[str]] = {}


def check_link(build_dir: Path, label: str, href: str) -> list[str]:
    parts = urlsplit(href)
    if parts.scheme or parts.netloc:
        return [f"{label} links off-site to {href}"]
    target = built_file(build_dir, parts.path)
    if not target.is_file():
        return [f"{label} links to {href}, which has no built page"]
    if parts.fragment:
        ids = _page_ids.get(target)
        if ids is None:
            ids = parse(target).ids
            _page_ids[target] = ids
        if parts.fragment not in ids:
            return [f"{label} links to {href}, but that page has no id={parts.fragment!r}"]
    return []


def compare_keys(label: str, want_keys: list[str], keys: list[str]) -> list[str]:
    problems: list[str] = []
    missing = [k for k in want_keys if k not in keys]
    extra = [k for k in keys if k not in want_keys]
    if missing:
        problems.append(f"{label} is missing {len(missing)} cell(s): {', '.join(missing[:6])}")
    if extra:
        problems.append(f"{label} has {len(extra)} cell(s) the data doesn't: {', '.join(extra[:6])}")
    if len(keys) != len(set(keys)):
        problems.append(f"{label} repeats a cell")
    if not missing and not extra and keys != want_keys:
        problems.append(f"{label} cells are out of order (groups, then actions, then platforms)")
    return problems


def check_regions(label: str, c: Collector) -> list[str]:
    problems: list[str] = []
    text = " ".join(c.region_text)
    if SUPPORTED_WORD_RE.search(text):
        problems.append(f"{label} renders the word 'supported'; status is shown by exception")
    if "mx-yes" in c.region_classes or "mx-check" in c.region_classes:
        problems.append(f"{label} renders a check mark; supported cells take the neutral dot")
    return problems


def check_built(build_dir: Path, root: Path) -> list[str]:
    problems: list[str] = []
    want = expected(root)
    m = want["matrix"]
    if not m:
        return ["data/integrations.json has no matrix block"]
    labels = want["labels"]

    page = built_file(build_dir, m["path"])
    if not page.is_file():
        problems.append(f"action matrix page {m['path']} was not built")
    else:
        c = parse(page)
        label = f"matrix {m['path']}"
        if c.markers.get("data-action-matrix") != 1:
            problems.append(f"{label} must render the shared matrix exactly once")
        if c.platforms != want["platforms"]:
            problems.append(f"{label} columns are {c.platforms}, data says {want['platforms']}")
        if c.groups != want["groups"]:
            problems.append(f"{label} groups are {c.groups}, data says {want['groups']}")
        if c.actions != want["actions"]:
            problems.append(f"{label} rows are {c.actions}, data says {want['actions']}")
        for pid, head in c.heads.items():
            soon = pid in want["soon"]
            if soon and (head["status"] != "coming-soon" or head["marks"] != ["mx-soon"]):
                problems.append(f"{label} column {pid} is coming soon but lacks its one clock mark")
            if not soon and (head["status"] or head["marks"]):
                problems.append(f"{label} column {pid} carries a status mark, but it is supported")
            if soon and labels.get("coming-soon") not in (head["title"] or ""):
                problems.append(f"{label} column {pid} title does not name {labels.get('coming-soon')!r}")
        problems.extend(compare_keys(label, want["keys"], [x["key"] for x in c.cells]))
        for cell in c.cells:
            key = cell["key"]
            if key not in want["cells"]:
                continue
            want_status, want_href = want["cells"][key]
            if cell["status"] != want_status:
                problems.append(f"{label} {key} is {cell['status']!r}, data says {want_status!r}")
                continue
            if want_status == "supported":
                if cell["href"] != want_href:
                    problems.append(f"{label} {key} links to {cell['href']!r}, want {want_href!r}")
                if cell["marks"] != ["mx-dot"]:
                    problems.append(f"{label} {key} marks are {cell['marks']}, want only the neutral dot")
            else:
                if cell["href"] is not None:
                    problems.append(f"{label} {key} links to {cell['href']}, want no link")
                if cell["marks"]:
                    problems.append(f"{label} {key} shows a mark {cell['marks']}; exceptions in cells stay empty")
                if cell["text"] != labels.get(want_status):
                    problems.append(
                        f"{label} {key} says {cell['text']!r}, want the {want_status} label {labels.get(want_status)!r}"
                    )
            if cell["href"]:
                problems.extend(check_link(build_dir, label, cell["href"]))
        problems.extend(check_regions(label, c))
        if EM_DASH in page.read_text(encoding="utf-8"):
            problems.append(f"{label} contains an em dash")

    docs = built_file(build_dir, m["docsPath"])
    if not docs.is_file():
        problems.append(f"docs all-actions page {m['docsPath']} was not built")
    else:
        c = parse(docs)
        label = f"docs table {m['docsPath']}"
        if c.markers.get("data-action-table") != 1:
            problems.append(f"{label} must render the shared table exactly once")
        problems.extend(compare_keys(label, want["supported_keys"], [r["key"] for r in c.rows]))
        for row in c.rows:
            key = row["key"]
            if key not in want["cells"]:
                continue
            pid = key.split(":", 1)[1]
            want_href = want["cells"][key][1]
            if row["href"] != want_href:
                problems.append(f"{label} {key} links to {row['href']!r}, want {want_href!r}")
            elif row["href"]:
                problems.extend(check_link(build_dir, label, row["href"]))
            name = want["names"].get(pid)
            if row["alt"] != name or row["title"] != name:
                problems.append(f"{label} {key} platform logo must carry alt and title {name!r}")
            if row["marks"]:
                problems.append(f"{label} {key} shows a status mark; listed actions are supported by definition")
            if row["cells"] != 2:
                problems.append(f"{label} {key} has {row['cells']} data cells, want Platform and What it does")
        problems.extend(check_regions(label, c))
        if EM_DASH in docs.read_text(encoding="utf-8"):
            problems.append(f"{label} contains an em dash")

    source = root / "content" / "en" / (m["docsPath"].strip("/") + "/_index.md")
    if not source.is_file():
        problems.append(f"no docs source page at {source.relative_to(root)}")
    else:
        text = source.read_text(encoding="utf-8")
        if len(SHORTCODE_RE.findall(text)) != 1:
            problems.append(f"{source.relative_to(root)} must call {{{{< all-actions >}}}} once")
        if MD_TABLE_RE.search(text):
            problems.append(f"{source.relative_to(root)} carries a hand-written action table")

    for path in ("/", "/integrations/"):
        target = built_file(build_dir, path)
        if not target.is_file():
            problems.append(f"{path} was not built")
            continue
        c = parse(target)
        if m["path"] not in c.hrefs:
            problems.append(f"{path} does not link to the action matrix at {m['path']}")
    return problems


def run(root: Path, build_dir: Path | None) -> list[str]:
    problems = check_source(root)
    if build_dir is not None:
        problems.extend(check_built(build_dir, root))
    return problems


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--source"]:
        problems = check_source(ROOT)
        what = "action matrix data"
    else:
        build_dir = Path(argv[0]) if argv else ROOT / "public"
        if build_dir.is_dir():
            problems = run(ROOT, build_dir)
        else:
            problems = check_source(ROOT) + [
                f"build dir {build_dir} is missing; run make site-build first"
            ]
        what = "action matrix and docs table"
    for item in problems:
        print(f"action-matrix: {item}", file=sys.stderr)
    print(f"checked {what}, {len(problems)} broken")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
