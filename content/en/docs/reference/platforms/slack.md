---
title: "Slack"
linkTitle: "Slack"
description: "What Blowhorn can do on Slack, and how each action behaves there."
weight: 229
---

# Slack

Blowhorn works on Slack through Slack's API, never the browser, and sends as you. It uses a Slack token in your account (`SLACK_USER_TOKEN` or `SLACK_BOT_TOKEN`) or your Slack session, linked through the Blowhorn extension.

## Supported actions

{{< supported-actions "slack" >}}

Sends a message as you to a channel, a person, or a thread. One
profile sends. `blowhorn post --platform slack --message` sends one
ad-hoc message with no queue row.

## Slack messages

Send from a queue row or ad hoc. A row sends to its own target; `--message`
with `--target` sends one message you type, with no row read or marked
done, and `--target` redirects the run's queued Slack rows. The target
is a `#channel`, `@user`, channel id, channel link, or message link for
a thread reply; anything else is refused, never sent somewhere else.
One profile sends per run, named with `--profile`; the profile from
the defaults file does not count as named.

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Send a Slack message](/docs/how-to/publish/send-a-slack-message/) - Slack, worked.
- [Content queue columns and row states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Platform action matrix](https://blowhorn.ai/field-manual/action-matrix/) - safe versus risky actions, per platform.
