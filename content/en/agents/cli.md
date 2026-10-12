{
  "tool": "CLI",
  "mark": ">_",
  "weight": 70,
  "description": "The Blowhorn CLI does everything the Mac app does: schedule, queue, post, amplify and pause, with JSON output any script or agent can drive.",
  "lead": "Everything the Mac app does, the CLI does too. That is why any agent can run Blowhorn.",
  "hook": "Every app feature, as a command",
  "wire_title": "Built to be driven",
  "wire_body": "Reads take --json. Writes take --expected-fingerprint so an agent never stomps a newer edit. Anything that publishes takes --dry-run. And one switch stops every Mac at once, with a recorded reason every machine reports.",
  "wire_file": "terminal",
  "wire_code": "blowhorn schedule status --json\nblowhorn schedule pause --all --reason \"launch moved to Thursday\"\nblowhorn schedule resume --all",
  "extra_file": "",
  "extra_code": "",
  "prompts": [],
  "commands": "blowhorn post --check-queue\nblowhorn post --profile all --dry-run\nblowhorn schedule list --due-only --profile all\nblowhorn schedule trigger-now 7\nblowhorn schedule pause --row 7\nblowhorn analytics --platform x --profile all\nblowhorn report --dry-run",
  "uses": [
    {
      "t": "Scripts and cron",
      "b": "Plain commands with exit codes, so a shell script can run a launch the same way an agent does."
    },
    {
      "t": "A fleet of Macs",
      "b": "Every Mac signed in to your account works the same schedule, coordinated so the same post isn't sent from two Macs."
    },
    {
      "t": "Pause control",
      "b": "schedule pause --all stops every Mac; --row N parks one job everywhere; resume picks up where you left off."
    }
  ],
  "faq": [
    {
      "q": "Where do I find every command?",
      "a": "Run blowhorn -h for the full list with examples, or read the CLI reference in the docs."
    },
    {
      "q": "Can I see what a command will do first?",
      "a": "Yes. Commands that act take --dry-run, and post --check-queue lists pending posts without publishing."
    },
    {
      "q": "What happens when a post fails?",
      "a": "Within a run, Blowhorn doesn't retry a failed post; if a post goes out but can't be recorded, it stops that profile's queue; scheduled retries are off by default."
    }
  ],
  "major": "A button is a suggestion. A command is an order.",
  "title": "The Blowhorn CLI",
  "linkTitle": "CLI",
  "layout": "agent",
  "lastmod": "2026-10-12",
  "sitemap": {
    "changefreq": "monthly",
    "priority": 0.5
  }
}
