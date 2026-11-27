{
  "title": "Blowhorn MCP server",
  "linkTitle": "MCP server",
  "seo_title": "The Blowhorn MCP server - Blowhorn for any AI assistant",
  "description": "The Blowhorn MCP server lets your AI assistant inspect your posts, schedule, queue, and connections over Streamable HTTP. Seven read-only tools, standard OAuth 2.1, zero setup on your computer.",
  "tool": "MCP",
  "who": "your assistant",
  "mark": "MCP",
  "weight": 20,
  "lead": "Connect any AI assistant to your Blowhorn workspace. The hosted Blowhorn MCP server serves seven read-only tools over Streamable HTTP, backed by OAuth 2.1 or Bearer authentication.",
  "hook": "One endpoint, seven read-only tools",
  "crumb_label": "AI native",
  "crumb_url": "/ai/",
  "steps": [
    {
      "t": "Get your endpoint",
      "b": "Blowhorn's hosted MCP server runs at https://mcp.blowhorn.ai/mcp over Streamable HTTP."
    },
    {
      "t": "Connect your assistant",
      "b": "One command or a JSON config block points your MCP client at the server. Sign in with OAuth 2.1 or a Bearer token."
    },
    {
      "t": "Say what you want",
      "b": "Your assistant inspects your scheduled posts, queue, events, and platform sessions without changing any live data."
    }
  ],
  "wire_title": "Plug it into your assistant",
  "mcp_generator": true,
  "wire_body": "Point your MCP client at Blowhorn's hosted server at https://mcp.blowhorn.ai/mcp. Streamable HTTP with OAuth 2.1 or Bearer token fallback. For Claude Code, one command connects it. Cursor, VS Code, and Claude Desktop configure in JSON.",
  "wire_file": "terminal",
  "wire_lang": "bash",
  "wire_code": "claude mcp add --transport http blowhorn https://mcp.blowhorn.ai/mcp",
  "extra_file": ".cursor/mcp.json",
  "extra_lang": "json",
  "extra_code": "{\n  \"mcpServers\": {\n    \"blowhorn\": {\n      \"url\": \"https://mcp.blowhorn.ai/mcp\"\n    }\n  }\n}",
  "wire_note": "New to this? [Connect an AI assistant over MCP](/docs/how-to/set-up/connect-mcp-client/) has the steps for every client, including [Claude Code](/docs/how-to/set-up/connect-mcp-client/#claude-code), [Cursor](/docs/how-to/set-up/connect-mcp-client/#cursor), [VS Code](/docs/how-to/set-up/connect-mcp-client/#vs-code-with-github-copilot), [Claude Desktop](/docs/how-to/set-up/connect-mcp-client/#claude-desktop), [Windsurf](/docs/how-to/set-up/connect-mcp-client/#windsurf-devin-desktop), [Zed](/docs/how-to/set-up/connect-mcp-client/#zed), [Gemini CLI](/docs/how-to/set-up/connect-mcp-client/#gemini-cli), [Grok](/docs/how-to/set-up/connect-mcp-client/#grok) and [Grok Bot](/docs/how-to/set-up/connect-mcp-client/#grok-bot). Grok Bot also has a [product page](/agents/grok-bot/). [Source and listings](https://github.com/blowhorn-ai/blowhorn-mcp): the launcher, plugin manifests and listing files live in the public blowhorn-mcp repo.",
  "prompts": [
    "What posts are currently scheduled across all my connected social accounts for this week?",
    "Show me recent publish events and delivery status for yesterday's release announcement.",
    "List all active platform connections and verify which accounts are currently authenticated.",
    "Read the upcoming queued items across my channels and check if anything needs attention."
  ],
  "commands_title": "What your assistant sees",
  "commands_file": "assistant",
  "commands_lang": "text",
  "commands_prompt": false,
  "commands": "# claude mcp list\nblowhorn: https://mcp.blowhorn.ai/mcp (HTTP) - Connected\n\n# the seven read-only tools served by the hosted MCP server\nlistContentItems       read only, inspects queued and draft content\ngetContentItem         read only, retrieves item details and assets\ngetEvents              read only, views recent publish events and delivery logs\ngetConnections         read only, lists active platform channels and credentials\nlistSchedules          read only, retrieves posting schedules\ngetScheduleById        read only, inspects timing and recurrence rules\ngetPlatformSessions    read only, checks active session status across platforms",
  "uses": [
    {
      "t": "Release day",
      "b": "Have your assistant inspect what is scheduled, what is queued and what needs your attention across channels without opening the app."
    },
    {
      "t": "The first hour",
      "b": "Ask what published, check event logs, and verify delivery status. Reads run as asked, so the answer comes straight back."
    },
    {
      "t": "The weekly read-out",
      "b": "Let it review scheduled queues and connection health for Friday's summary. Nothing is changed or written."
    }
  ],
  "faq": [
    {
      "q": "Does it run in the cloud?",
      "a": "Yes. The hosted server runs at https://mcp.blowhorn.ai/mcp over Streamable HTTP with OAuth 2.1. See [Connect an AI assistant over MCP](/docs/how-to/set-up/connect-mcp-client/)."
    },
    {
      "q": "Can I npx it?",
      "a": "Coming soon. Today, connect directly to the hosted server URL at https://mcp.blowhorn.ai/mcp."
    },
    {
      "q": "Can the agent approve or publish on its own?",
      "a": "No. The hosted server is read-only and serves seven inspection tools. It does not post, schedule, or change anything. [How the MCP server keeps you in control](/docs/explanation/mcp-and-safety/) has the whole picture."
    },
    {
      "q": "Where is the MCP server source?",
      "a": "The public [blowhorn-mcp repo](https://github.com/blowhorn-ai/blowhorn-mcp) on GitHub holds the launcher, the Claude Code and Cursor plugin manifests, the Gemini CLI extension, the agent skill and the listing files."
    },
    {
      "q": "Is it listed in MCP catalogs?",
      "a": "Coming soon."
    },
    {
      "q": "Does my assistant see my passwords?",
      "a": "No. Tool results never carry secrets. See [how the MCP server keeps you in control](/docs/explanation/mcp-and-safety/)."
    },
    {
      "q": "Which assistants can use it?",
      "a": "Any MCP client that supports Streamable HTTP: Claude Code, Cursor, VS Code, Claude Desktop, Windsurf, Zed, Gemini CLI, Grok, and Grok Bot. [Connect an AI assistant over MCP](/docs/how-to/set-up/connect-mcp-client/) has the steps for each."
    }
  ],
  "cta_title": "Inspect your marketing with any assistant",
  "more_title": "Other ways to bring your assistant",
  "major": "Any assistant can report for duty. Connect to the hosted server in seconds.",
  "status": "Available now",
  "label": "AI native",
  "layout": "agent",
  "lastmod": "2026-11-27",
  "sitemap": {
    "changefreq": "monthly",
    "priority": 0.5
  }
}
