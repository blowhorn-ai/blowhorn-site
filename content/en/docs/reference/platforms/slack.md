---
title: "Slack"
linkTitle: "Slack"
description: "What Blowhorn does on Slack: actions, sign-in, and how much evidence stands behind each reading."
weight: 5
---

# Slack

API, never the browser. Sends a message as you to a channel, a person,
or a thread: the target is `#channel`, `@user`, a channel id, a channel
link, or a message link for a thread reply. One profile sends; the
credential is a Slack token in your account (`SLACK_USER_TOKEN`,
`SLACK_BOT_TOKEN`, or a workspace session captured through the
extension). `blowhorn post --platform slack --message` sends one ad-hoc
message with no queue row.

## Slack messages

Send from a queue row or ad hoc. A row sends to its own target; `--message`
with `--target` sends one message you type, with no row read or marked
done, and `--target` redirects the run's queued Slack rows. The target
is a `#channel`, `@user`, channel id, channel link, or message link for
a thread reply; anything else is refused, never sent somewhere else.
One profile sends per run, named with `--profile`; the profile from
the defaults file does not count as named.

## Captured versus unverified

How much evidence stands behind each reading Blowhorn takes on Slack. [All platforms](/docs/reference/platforms/) explains what captured, probed, and unverified mean.

| State | Captured, probed or unverified |
|---|---|
| **A message was posted**: Slack answers `ok` | Unverified (docs) - never recorded from a real response |
| A message's link, built from the answer | Unverified (docs) |
| How a captured workspace session is used | Unverified (model) - Slack's web client convention, undocumented by Slack |
| Capturing a workspace session from your browser | Unverified (model) - a miss captures nothing and posts nothing |
| Sign-in errors, OAuth answers, and link shapes | Unverified (docs) |
| A resend is not duplicated | Unverified (docs) - Blowhorn's own send record keeps each send to once |
| The marks of an app-attributed message | Unverified (docs) - a miss reports an attributed message as clean |
| A rate limit's wait, and an unreadable answer | Unverified (docs, model) - such a send is marked outcome unknown and never resent |

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Send a Slack message](/docs/how-to/publish/send-a-slack-message/) - Slack, worked.
- [Content queue columns and row states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Platform action matrix](/field-manual/action-matrix/) - safe versus risky actions, per platform.
