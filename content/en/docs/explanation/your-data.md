---
title: "Where your data lives"
description: "What stays on your machine, what your account keeps in sync, and what the extension reads."
weight: 281
---


Three places hold Blowhorn's data, and each holds a different kind.
Nothing here is a step; for the sharing behind it see
[How Blowhorn works](/docs/explanation/how-it-works/).

On your machine: the app with the engine it carries, the engine's folder
(`~/Library/Application Support/Blowhorn/home`, or a contributor's checkout),
and your Chrome sessions.
Browser sessions, meaning the cookies Chrome keeps for LinkedIn, X,
Reddit and Hacker News, live in your Chrome profiles, where you made
them; Blowhorn reads them there and copies none of them elsewhere, with
one exception: a Slack workspace session you capture is kept in your account, below. LinkedIn, X, Reddit and Bluesky runs sign
in with the password in the profile's local `config.yaml`. Every action
Blowhorn takes runs on one of your machines; Blowhorn never signs in or
acts for you from a server. The daily
logs, the run ledger copy, and the scheduler heartbeat live under the
log directory. The account connection file lives outside the engine's folder at
mode 0600. A plan attestation, once fetched, is kept in your keychain
for the offline grace.

In your account: the content rows, the schedule, the
profiles, the ledgers, the run history, and the analytics. Keeping them
in one account is what lets you install Blowhorn on any number of machines,
your own or your teammates', and run them as one: every machine works from
the same queue, and the machines coordinate through it, so the same post
isn't sent from two of them, and your analytics cover every machine. Your account holds platform credentials too: GitHub tokens, Hacker News
passwords, and Slack tokens and captured sessions. For profiles set up
before October 2026, it also holds the LinkedIn, X, Reddit and Bluesky
passwords copied in when those profiles moved to your account. It records
which Chrome profile each Blowhorn profile uses on each machine: the machine's
name, the Chrome profile's folder and display name, and the Google
account signed in to that Chrome profile. A machine that isn't signed in to your account runs nothing.

On the platforms: whatever Blowhorn published, amplified, or followed
as you, under your name, subject to each destination's own retention.
A published post is the platform's copy; Blowhorn keeps the link and
the outcome, not the content's master.

The extension queries tabs only on the supported sites and reads
cookies there only when the app asks, handing both to the Blowhorn app
on your machine. Every action Blowhorn takes is executed on one of your machines,
through your Chrome profile or a platform's API; your account keeps the
queue and results in sync and does not act for you from a server. The
one browser session the app keeps in your account is your Slack workspace
session, saved as that profile's Slack credential.
Platform credentials such as tokens and passwords are a different
matter: they live in your account, as the
[privacy page](https://blowhorn.ai/legal/privacy/) describes. What a run records, such as a new post's link and its
outcome, goes to your account as described above. The extension makes no
requests of its own to any server, sells nothing, and injects no ads.
The [privacy page at blowhorn.ai](https://blowhorn.ai/legal/privacy/) states the same promises; this page
follows it, and the privacy page wins on any difference.

What never belongs in a report, an issue, or a chat message:
credentials, session files, the private connection file, and anything
from your Chrome profile directories. A refusal sentence and an exit
code are enough to diagnose with.

## Related

- [Get help](/docs/reference/support/) - report a problem without secrets.
- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) - the log directory listing.
- [Profile reference](/docs/reference/profiles/) - which secrets live where.
- [Chrome extension permissions](/docs/reference/extension-permissions/) - what the extension may read.
