---
title: "`blowhorn post` reference"
description: "The posting command in full: pending rows, every flag, and per-platform behavior."
weight: 216
---


Publishes the queue's pending rows and amplifies existing content.
This page describes the command in full; the [CLI reference](/docs/reference/cli/)
lists every command with its flags, and the steps live in the how-to
guides under Related.

## What "pending" means

A row is pending when "Approved?" says `yes` or `true`, "Date Promoted"
is empty, "Promote On" is due or blank, and the profile and platform
resolve. `--check-queue` lists the pending rows without publishing
anything, opening no browser and hitting no API. `--dry-run` walks the
whole run, printing what would go out, and marks nothing done.

Posting is one click per run. A clicked control with no confirmation
read back is recorded as clicked, outcome not read, counted for
nothing, and never retried by the run. See
[How Blowhorn avoids repeat posts](/docs/explanation/never-twice/).

## Flags

| Flag | Means |
|---|---|
| `--profile` | Name, comma-delimited names, or `all` (the default). A profile you name that is eligible for nothing in scope stops the run with the reason; `all` filters quietly |
| `--platform` | One of `bluesky`, `github`, `hn`, `linkedin`, `reddit`, `slack`, `x`, or `all` |
| `--exclude`, `--e` | Profiles left out of `--profile all`; naming a profile explicitly still runs it |
| `--target` | Ad-hoc target overriding the row for this run. Slack: `#channel`, `@user`, a channel link, or a message link for a thread reply. Other platforms: leave unset and use "Comment on" |
| `--message` | One ad-hoc Slack message instead of queue rows: no row read or marked done. Needs `--platform slack`, one named profile, and `--target`; refused with `--check-queue` or `--amplify` |
| `--amplify` | URL of existing content to amplify instead of publishing: LinkedIn repost, X retweet or quote, Reddit upvote, Bluesky repost, GitHub reactions. Overrides the row's "Amplify" column; ignored for Slack rows |
| `--check-queue` | List pending rows and stop; read-only |
| `--dry-run` | Simulate everything: no publishing, no following, no writing |
| `--pace` | `fast`, `normal`, `slow`, or a numeric multiplier on the pauses between actions |
| `--headless` | Unattended: a background window, never headless Chrome, and no waiting for a person at a sign-in or challenge |
| `--headed` | Keep the browser visible and in front; wins over `--headless` from a higher layer |
| `--chrome-launch` | How this run reaches Chrome, for one run |
| `--slack-auth` | Which Slack credential may send, for one run |
| `--config`, `--log-dir`, `--verbose` | Config file path, log directory, verbose output |

GitHub is amplify-only under `post`: `--platform github` needs an
`--amplify` issue or pull-request URL, or a GitHub row's "Amplify"
column, and refuses without one.

## Platform behavior

LinkedIn, X, Reddit, and Hacker News drive your Chrome through the
extension. Slack, Bluesky, and GitHub post through their APIs. Reddit
rows need their subreddit as `r/<name>` in "Destination" or "Amplify";
without one the row is skipped. A "Comment on" row addressed to a
LinkedIn or Reddit location becomes a comment under `post` as well as
under `comment`; X has no comment flow.

## Examples

```bash
blowhorn post --check-queue
blowhorn post --dry-run --platform hn
blowhorn post --profile all --platform x --pace slow
blowhorn post --platform github --amplify https://github.com/org/repo/issues/1
blowhorn post --platform slack --profile your-profile --target "#general" --message "Ship day is here."
```

## Related

- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the run in practice.
- [Content queue columns and row states](/docs/reference/content-queue/) - what the rows hold.
- [Platforms](/docs/reference/platforms/) - per-platform actions and limits.
- [CLI reference](/docs/reference/cli/) - every command and flag.
- [How Blowhorn avoids repeat posts](/docs/explanation/never-twice/) - one click per run.
- [You're in control](/docs/explanation/youre-in-control/) - dry run, pace and the built-in limits.
