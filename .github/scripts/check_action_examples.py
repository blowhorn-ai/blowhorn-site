#!/usr/bin/env python3
"""Fail if action examples, vocabulary, or YAML actions drift apart.

Every supported action on every supported platform must have an
data/action_examples.json entry (placeholders allowed). CLI commands marked
available must use flags that appear on the named CLI reference page.

Usage: check_action_examples.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLAG_RE = re.compile(r"--[a-z][a-z0-9-]*")
EM_DASH = "\u2014"


def yaml_action_ids(platform_id: str) -> list[str]:
    path = ROOT / "data" / "platforms" / f"{platform_id}.yaml"
    return [
        line.split("id:", 1)[1].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("  - id:")
    ]


def supported_pairs() -> list[tuple[str, str]]:
    data = json.loads((ROOT / "data/integrations.json").read_text(encoding="utf-8"))
    pairs = []
    for item in data["platforms"]:
        if item["status"] != "supported":
            continue
        for action in yaml_action_ids(item["id"]):
            pairs.append((item["id"], action))
    return pairs


def cli_page(cli_ref: str) -> Path:
    slug = cli_ref.strip("/").rsplit("/", 1)[-1]
    return ROOT / "content" / "en" / "docs" / "reference" / "cli" / f"{slug}.md"


def main() -> int:
    problems: list[str] = []
    vocab = json.loads((ROOT / "data/actions.json").read_text(encoding="utf-8"))
    examples = json.loads((ROOT / "data/action_examples.json").read_text(encoding="utf-8"))
    vocab_ids = [a["id"] for a in vocab["actions"]]
    vocab_set = set(vocab_ids)
    if len(vocab_ids) != len(vocab_set):
        problems.append("data/actions.json repeats an action id")

    order = examples.get("surfaces") or []
    if order != ["app", "cli", "rest", "mcp", "skill"]:
        problems.append(
            f"action_examples.surfaces is {order!r}, want ['app', 'cli', 'rest', 'mcp', 'skill']"
        )

    pairs = supported_pairs()
    pair_set = set(pairs)
    seen = set()
    for ex in examples["examples"]:
        key = (ex["platform"], ex["action"])
        if key in seen:
            problems.append(f"duplicate example for {key[0]} {key[1]}")
        seen.add(key)
        if ex["action"] not in vocab_set:
            problems.append(
                f"example {key[0]} {key[1]} uses an action id not in data/actions.json"
            )
        if key not in pair_set:
            problems.append(
                f"example {key[0]} {key[1]} is not a supported platform action"
            )
        blob = json.dumps(ex, ensure_ascii=False)
        if EM_DASH in blob:
            problems.append(f"example {key[0]} {key[1]} contains an em dash")
        cli = ex["surfaces"]["cli"]
        if cli["status"] == "available":
            command = cli.get("command") or ""
            ref = cli.get("cliRef") or ""
            if not command.startswith("blowhorn "):
                problems.append(f"{key[0]} {key[1]} CLI command does not start with blowhorn")
            page = cli_page(ref)
            if not page.is_file():
                problems.append(f"{key[0]} {key[1]} cliRef {ref} has no {page.relative_to(ROOT)}")
            else:
                text = page.read_text(encoding="utf-8")
                for flag in FLAG_RE.findall(command):
                    if flag not in text:
                        problems.append(
                            f"{key[0]} {key[1]} uses {flag} which is not on {page.relative_to(ROOT)}"
                        )
        shot = ex["surfaces"]["app"].get("screenshot") or ""
        expected = f"assets/docs/actions/{ex['platform']}/{ex['action']}.png"
        if shot != expected:
            problems.append(
                f"{key[0]} {key[1]} screenshot is {shot!r}, want {expected}"
            )

    for platform, action in pairs:
        if action not in vocab_set:
            problems.append(
                f"data/platforms/{platform}.yaml action {action} is not in data/actions.json"
            )
        if (platform, action) not in seen:
            problems.append(
                f"missing action_examples entry for {platform} {action}"
            )

    for item in problems:
        print(f"actions: {item}", file=sys.stderr)
    print(f"checked {len(pairs)} supported action(s), {len(problems)} broken")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
