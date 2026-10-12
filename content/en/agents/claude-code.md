{
  "tool": "Claude Code",
  "mark": "CC",
  "weight": 10,
  "description": "Use Claude Code to run your marketing with Blowhorn: a project skill, an allowlist for the blowhorn CLI, and prompts that schedule, queue and amplify across every Mac.",
  "lead": "Claude Code already lives in your terminal. Give it the Blowhorn CLI and a skill, and it runs your launch while you review the diff.",
  "hook": "Skills, CLAUDE.md and a Bash allowlist",
  "wire_title": "Teach it once with a skill",
  "wire_body": "Claude Code loads project skills from .claude/skills/. Drop one in that tells it which blowhorn commands exist, that every read takes --json, and that writes pass the row fingerprint back. Then allow the read-only commands in .claude/settings.json so it stops asking, and leave publishing on ask.",
  "wire_file": ".claude/skills/blowhorn/SKILL.md",
  "wire_lang": "markdown",
  "wire_code": "---\nname: blowhorn\ndescription: Schedule, queue and amplify social posts with the blowhorn CLI\n---\n\nRead before you write:\n- blowhorn schedule list --json\n- blowhorn content list --pending --json\n- blowhorn schedule status --json\n\nWrite with the fingerprint you just read:\n- blowhorn content upsert --payload '<json>' --row N --expected-fingerprint <fp> --json\n\nPreview anything that publishes with --dry-run first.\nIf anything looks wrong: blowhorn schedule pause --all --reason \"<why>\"",
  "extra_file": ".claude/settings.json",
  "extra_lang": "json",
  "extra_code": "{\n  \"permissions\": {\n    \"allow\": [\n      \"Bash(blowhorn schedule list:*)\",\n      \"Bash(blowhorn schedule status:*)\",\n      \"Bash(blowhorn content list:*)\",\n      \"Bash(blowhorn analytics:*)\"\n    ]\n  }\n}",
  "prompts": [
    "Read my pending content queue and tell me which rows are owed to which profiles before Tuesday.",
    "Add a LinkedIn row for profile lee: announce the v2.4 release, approved, promote on 2026-11-10 09:00:00. Show me the payload first.",
    "Our post just went live at this URL. Dry-run an amplify from every profile on this Mac, then wait for my go.",
    "Something is off with LinkedIn. Pause the whole fleet and tell me the reason you recorded."
  ],
  "commands": "blowhorn content list --pending --json\nblowhorn content upsert --payload '{\"Platform\":\"linkedin\",\"Profile\":\"lee\",\"Message Text\":\"v2.4 is out\",\"Approved?\":\"yes\",\"Promote On\":\"2026-11-10 09:00:00\"}' --json\nblowhorn post --platform linkedin --profile all --amplify \"<post-url>\" --dry-run\nblowhorn schedule pause --all --reason \"LinkedIn challenge\"",
  "commands_lang": "bash",
  "uses": [
    {
      "t": "Release day from the PR",
      "b": "Ask Claude Code to read the changelog it just wrote and turn it into one queue row per platform, in your voice, ready for approval."
    },
    {
      "t": "Headless runs",
      "b": "claude -p runs a prompt without the interactive session, so a morning check of what is due can run from a script and land in your terminal."
    },
    {
      "t": "The weekly read-out",
      "b": "Let it pull blowhorn analytics history --json and write the summary you would otherwise build by hand on Friday."
    }
  ],
  "faq": [
    {
      "q": "Does Blowhorn ship an MCP server for Claude Code?",
      "a": "Not today. Claude Code drives the CLI through its Bash tool, and every command that an agent needs speaks --json, so a skill and an allowlist are all the setup there is."
    },
    {
      "q": "Can it publish without asking me?",
      "a": "Only if you allow it. Keep blowhorn post and schedule trigger-now off the allowlist and Claude Code asks every time."
    },
    {
      "q": "Does my agent see my social passwords?",
      "a": "No sign-in happens through the agent. Blowhorn posts through your own signed-in Chrome with the Blowhorn extension, so the agent runs commands and reads their output. Keep the same care you would with any tool that can act on your accounts: review what you allow it to run."
    }
  ],
  "major": "Your agent wrote 4,000 lines before lunch and the launch post is still a sticky note. Unacceptable. Hand it the horn.",
  "title": "Blowhorn for Claude Code",
  "linkTitle": "Claude Code",
  "layout": "agent",
  "lastmod": "2026-10-12",
  "sitemap": {
    "changefreq": "monthly",
    "priority": 0.5
  }
}
