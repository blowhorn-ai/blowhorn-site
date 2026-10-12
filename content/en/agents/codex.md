{
  "tool": "Codex",
  "mark": "Cx",
  "weight": 40,
  "description": "Use Codex with Blowhorn: AGENTS.md rules, codex exec for unattended checks, and approval settings that keep publishing in your hands.",
  "lead": "Codex follows AGENTS.md and asks before it acts outside its lane. Point it at Blowhorn and keep your finger on approve.",
  "hook": "AGENTS.md, codex exec and approvals",
  "wire_title": "Rules in AGENTS.md, approvals in Codex",
  "wire_body": "Codex reads AGENTS.md from your repo. Blowhorn needs the network and your Chrome, so a sandboxed Codex session will ask before running it. That ask is a feature: approve reads, think twice before publishing.",
  "wire_file": "AGENTS.md",
  "wire_code": "## Social posting\n\nTool: blowhorn (on PATH). JSON output: add --json.\n1. Read: blowhorn schedule list --json, blowhorn content list --pending --json\n2. Propose changes as a payload and show me\n3. Write with --expected-fingerprint so you never overwrite a newer edit\n4. Stop switch: blowhorn schedule pause --all --reason \"<why>\"",
  "extra_file": "",
  "extra_code": "",
  "prompts": [
    "Read the last 30 days of operations grouped by host and tell me which Mac is doing the work.",
    "Schedule a daily report row at 08:00 for all profiles. Show the payload before you run it.",
    "Validate every schedule row and fix the ones that fail, one upsert per row."
  ],
  "commands": "blowhorn analytics operations --group-by host --since 30d --json\nblowhorn schedule upsert --payload '{\"Command\":\"report\",\"Profile\":\"all\",\"Run At\":\"2026-10-13 08:00:00\",\"Recurrence\":\"daily\"}' --json\nblowhorn schedule validate --json",
  "uses": [
    {
      "t": "Unattended checks",
      "b": "codex exec runs a task without the interactive UI, which suits a morning \"what is due, what failed\" pass."
    },
    {
      "t": "Safe edits",
      "b": "Every schedule and content write takes --expected-fingerprint, so a Codex edit is rejected if you changed the row first."
    },
    {
      "t": "Fleet health",
      "b": "analytics operations --group-by host shows which Mac ran what, so Codex can spot the one that went quiet."
    }
  ],
  "faq": [
    {
      "q": "Why does Codex ask before running blowhorn?",
      "a": "Blowhorn reaches the network and your Chrome. Approving it per command is the sensible default."
    },
    {
      "q": "Will two Macs post the same row?",
      "a": "Rows are claimed with a lease, coordinated so the same post isn't sent from two Macs."
    },
    {
      "q": "Does my agent see my social passwords?",
      "a": "No sign-in happens through the agent. Blowhorn posts through your own signed-in Chrome with the Blowhorn extension, so the agent runs commands and reads their output. Keep the same care you would with any tool that can act on your accounts: review what you allow it to run."
    }
  ],
  "major": "Codex asks permission before it fires. Good. The last recruit who did not is still explaining himself to LinkedIn.",
  "title": "Blowhorn for Codex",
  "linkTitle": "Codex",
  "layout": "agent",
  "lastmod": "2026-10-12",
  "sitemap": {
    "changefreq": "monthly",
    "priority": 0.5
  }
}
