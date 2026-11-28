{{- /* Markdown output of MCP configuration generator, matching tabs.md conventions */ -}}
### Claude Code

```bash
claude mcp add --transport http blowhorn https://mcp.blowhorn.ai/mcp
```

### Cursor

```json
{
  "mcpServers": {
    "blowhorn": {
      "url": "https://mcp.blowhorn.ai/mcp"
    }
  }
}
```

### VS Code with GitHub Copilot

```json
{
  "servers": {
    "blowhorn": {
      "type": "http",
      "url": "https://mcp.blowhorn.ai/mcp"
    }
  }
}
```

### Claude Desktop

```json
{
  "mcpServers": {
    "blowhorn": {
      "type": "http",
      "url": "https://mcp.blowhorn.ai/mcp"
    }
  }
}
```

### Windsurf

```json
{
  "mcpServers": {
    "blowhorn": {
      "type": "http",
      "url": "https://mcp.blowhorn.ai/mcp"
    }
  }
}
```

### Zed

```json
{
  "context_servers": {
    "blowhorn": {
      "type": "http",
      "url": "https://mcp.blowhorn.ai/mcp"
    }
  }
}
```

### Gemini CLI

```bash
gemini mcp add --transport http blowhorn https://mcp.blowhorn.ai/mcp
```
