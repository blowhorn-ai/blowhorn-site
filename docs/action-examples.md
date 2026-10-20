# Adding a platform action example

Every supported action on every supported platform has a tabbed example on its
docs page (`/docs/reference/platforms/<id>/#action-<id>`). The tabs are App,
CLI, REST API, MCP, then Skill. Content lives in data, not in the Markdown
page. Hyphens, never em dashes.

## Where the data lives

| File | What it is |
|---|---|
| [`data/actions.json`](../data/actions.json) | Action vocabulary: `id`, display `name`, default description. Templates never hand-list action names. |
| [`data/platforms/<id>.yaml`](../data/platforms/) | Which of those ids this platform supports. Optional `behavior` overrides the default description where the platform differs. Optional `limits`. |
| [`data/action_examples.json`](../data/action_examples.json) | One entry per supported platform+action. Each surface is `available` or `placeholder`. |
| [`schemas/actions.schema.json`](../schemas/actions.schema.json) and [`schemas/action_examples.schema.json`](../schemas/action_examples.schema.json) | `make check-schemas` validates both, then [`.github/scripts/check_action_examples.py`](../.github/scripts/check_action_examples.py) fails if coverage dropped. |

The docs page already calls `{{< supported-actions "linkedin" >}}`. That
shortcode renders the actions table and the example tabs from this data. You
do not edit the page to add an example.

## Add or fill an example

1. If the action is new to Blowhorn, append it to `data/actions.json` (id, name,
   description). Use a hyphenated lowercase id (`post`, `find`).
2. List that id under `actions:` in `data/platforms/<platform>.yaml`. Set
   `behavior` only when this platform's "what it does" is not the vocabulary
   default. Set `limits` when there is a cap or a read-only note.
3. Add a matching object to `data/action_examples.json`:

   ```json
   {
     "platform": "linkedin",
     "action": "comment",
     "surfaces": {
       "app": {
         "status": "placeholder",
         "screenshot": "assets/docs/actions/linkedin/comment.png"
       },
       "cli": {
         "status": "available",
         "command": "blowhorn comment --platform linkedin --target \"https://www.linkedin.com/feed/update/urn:li:activity:123/\" --message \"Great post!\"",
         "cliRef": "/docs/reference/cli/comment/"
       },
       "rest": { "status": "placeholder", "notes": "The Blowhorn REST API for this action is not published yet." },
       "mcp": {
         "status": "placeholder",
         "prompt": "Comment on this LinkedIn post as me: https://www.linkedin.com/feed/update/urn:li:activity:123/ with the message Great post!",
         "notes": "Coming soon. This is the shape of the prompt to give an AI agent connected to the Blowhorn MCP server."
       },
       "skill": { "status": "placeholder", "notes": "A Blowhorn skill for this action is not available yet." }
     }
   }
   ```

4. CLI: copy a command from [`content/en/docs/reference/cli/`](../content/en/docs/reference/cli/).
   Do not invent flags. If the action has no CLI command, set `cli.status` to
   `placeholder` and say so in `notes`. The check script requires every
   `--flag` in an available command to appear on the `cliRef` page.
5. App screenshot: keep `status` as `placeholder` until the PNG exists. Put
   the file at `static/assets/docs/actions/<platform>/<action>.png` (the path
   in `screenshot` without the `static/` prefix). The pane fills itself when
   that file is present; you do not have to change the JSON.
6. Run `make check-schemas`, then `make check`.

## Tabs shortcode

For a one-off tabset in Markdown, not an action example:

```
{{< tabs id="unique" group="surface" label="Examples" >}}
{{< tab id="cli" name="CLI" >}}
command here
{{< /tab >}}
{{< /tabs >}}
```

`group="surface"` shares the chosen tab across the page (localStorage), so
switching to CLI switches every grouped set. Without JavaScript every pane
stays visible, stacked. Action examples use this through
`{{< action-examples platform="linkedin" action="comment" >}}`.
