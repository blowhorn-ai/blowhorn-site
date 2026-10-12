{
  "tool": "Pi",
  "mark": "Pi",
  "weight": 30,
  "description": "Use the Pi coding agent with Blowhorn: a minimal agent, a bash tool and an AGENTS.md block that turn it into your marketing operator.",
  "lead": "Pi keeps its toolbox small: read, write, edit and bash. Bash is all Blowhorn needs.",
  "hook": "A minimal agent with a bash tool",
  "wire_title": "Small agent, small setup",
  "wire_body": "Pi has no plugin to install for this. It reads AGENTS.md for project context and runs commands through bash, so the whole integration is a short block of instructions and a CLI that answers in JSON.",
  "wire_file": "AGENTS.md",
  "wire_lang": "markdown",
  "wire_code": "## Blowhorn\n\nUse the blowhorn CLI for social posting. Always read before writing:\n  blowhorn content list --pending --json\nWrites carry the fingerprint you read:\n  blowhorn content upsert --row N --expected-fingerprint <fp> --payload '<json>' --json\nNever publish without a --dry-run first and my go-ahead.",
  "extra_file": "",
  "extra_lang": "",
  "extra_code": "",
  "prompts": [
    "What does the content queue owe each profile right now?",
    "Turn this README section into a Hacker News row with a title under the limit. Leave it unapproved.",
    "Show me schedule status for every Mac in one table."
  ],
  "commands": "blowhorn content list --pending --json\nblowhorn content get 18 --json\nblowhorn schedule status --json\nblowhorn post --check-queue --profile all",
  "commands_lang": "bash",
  "uses": [
    {
      "t": "Low ceremony",
      "b": "No server, no extension for the agent, no second config format. If Pi can run it in bash, Pi can run your launch."
    },
    {
      "t": "Context you can read",
      "b": "Everything Pi does is a visible blowhorn command with JSON output, so the transcript doubles as an audit trail."
    },
    {
      "t": "Check before you post",
      "b": "post --check-queue shows pending posts without publishing anything. A good first command for a new agent."
    }
  ],
  "faq": [
    {
      "q": "Do I need a Pi package for Blowhorn?",
      "a": "No. Pi only needs blowhorn on its PATH."
    },
    {
      "q": "What if a post fails mid-run?",
      "a": "Within a run, Blowhorn doesn't retry a failed post; if a post goes out but can't be recorded, it stops that profile's queue; scheduled retries are off by default. Pi will see that in the output and can tell you."
    },
    {
      "q": "Does my agent see my social passwords?",
      "a": "No sign-in happens through the agent. Blowhorn posts through your own signed-in Chrome with the Blowhorn extension, so the agent runs commands and reads their output. Keep the same care you would with any tool that can act on your accounts: review what you allow it to run."
    }
  ],
  "major": "Four tools and a bash prompt. That is a lean, mean posting machine, soldier.",
  "title": "Blowhorn for Pi",
  "linkTitle": "Pi",
  "layout": "agent",
  "lastmod": "2026-10-12",
  "sitemap": {
    "changefreq": "monthly",
    "priority": 0.5
  }
}
