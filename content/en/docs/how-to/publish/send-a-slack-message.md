---
title: "Send a Slack message"
description: "Queue Slack rows or send one message typed on the command line."
weight: 116
---


Send a Slack message as yourself, from a queued row or typed on the
command line. Both send under your captured session, with no app attached.

## Before the first run

Capture your signed-in Slack session into the profile
([Sign a profile in to each platform](/docs/how-to/set-up/platform-accounts/)):

```bash
blowhorn profile auth --platform slack --profile kate
```

## Send one message, no row

Name one profile, the destination, and the text, and preview it first:

```bash
blowhorn post --platform slack --profile kate --target "#announcements" --message "Maintenance is complete" --dry-run
blowhorn post --platform slack --profile kate --target "#announcements" --message "Maintenance is complete"
```

`--target` takes `#channel`, `@user`, a Slack channel link, or a Slack
message link (a thread reply). For a one-off message anything else is
refused, never sent somewhere you did not name. Give a link when the profile's credentials
are per workspace, so Blowhorn knows which workspace to send with.
`--target` without `--message` is not a one-off message: it redirects the
queued Slack rows for that run.

Nothing is written back, so running the command twice sends the message
twice.

## Send as an agent, exactly once

`blowhorn slack send` is the same one-off send built for an agent: a dry run
unless `--confirm`, `--json` output, and each message sent at most once. Name
several profiles to send the same reply as each of them, one after another:

```bash
blowhorn slack send --profile rian,alex --target "https://acme.slack.com/archives/C0123/p1776000000000100" --file reply.md --slack-auth session --json
```

Each profile gets its own idempotency key, ledger entry and result, and a
refusal for one never stops the others. A confirmed send waits a random
interval (scaled by `--pace`) after the one before it. If the store becomes
unavailable partway through, the command stops there, still reports what was
already sent, and lists the remaining profiles as `store_unavailable`. The
command exits 0 only when every profile succeeded. See the [CLI reference](/docs/reference/cli/).

## Edit, delete or react

Fix or take back a message you sent with `blowhorn slack send`, or react to
any message. Each is a dry run until `--confirm`:

```bash
blowhorn slack edit --profile rian --target "https://acme.slack.com/archives/C0123/p1776000000000400" --file fixed.md --confirm
blowhorn slack delete --profile rian --target "https://acme.slack.com/archives/C0123/p1776000000000400" --confirm
blowhorn slack react --profile rian --target "https://acme.slack.com/archives/C0123/p1776000000000100" --emoji white_check_mark --confirm
```

Edit and delete work only on a message that profile sent through
`blowhorn slack send`; anything else is refused as `not_sent_by_profile`,
even when your session could delete it in Slack.

## Send the queued rows

Queue rows with `Platform` set to Slack. Put where each message goes in
`Amplify` (`#channel`, `@user`, or a Slack channel or message link), or a
Slack message link in `Comment on` for a thread reply. `Destination` only
picks the workspace whose credentials send. Then run:

```bash
blowhorn post --platform slack --profile kate
```

A row with no target in `Amplify` or `Comment on` goes to `#general`, and
so does one whose target Blowhorn cannot read, such as `announcements`
without the `#`. Preview with `--dry-run` first.

`--target` on that run sends the queued rows to that destination instead
of their own. Unlike a one-off message, it is not checked: a value it
cannot read sends every queued row to `#general`.

## Pick which credential sends

`--slack-auth` names which Slack credential may send for one run:
`session` (your captured signed-in session), `user-token`, or
`bot-token`, or a comma-delimited list of them.

## Related

- [Sign a profile in to each platform](/docs/how-to/set-up/platform-accounts/) -
  capturing the session each message sends with.
- [Post content](/docs/how-to/publish/post-content/) - running `blowhorn post` in general.
- [Manage the content queue](/docs/how-to/publish/manage-the-content-worksheet/) - queueing
  the rows a run reads.
