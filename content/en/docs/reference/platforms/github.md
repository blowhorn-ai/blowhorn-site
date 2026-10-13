---
title: "GitHub"
linkTitle: "GitHub"
description: "What Blowhorn does on GitHub: actions, sign-in, and how much evidence stands behind each reading."
weight: 7
---

# GitHub

API, never the browser. Follows accounts with `blowhorn follow` and
lists an audience with `blowhorn source --platform github --repo`.
Under `post`, GitHub amplifies only: it adds all five uplifting
reactions (+1, laugh, hooray, heart, rocket) to the issue or pull
request the `--amplify` flag or the row's "Amplify" column names, from
every selected profile under its own token. Re-running adds none of
them twice. The credential is `GH_TOKEN` in your account.

## Captured versus unverified

How much evidence stands behind each reading Blowhorn takes on GitHub. [All platforms](/docs/reference/platforms/) explains what captured, probed, and unverified mean.

| State | Captured, probed or unverified |
|---|---|
| A missing token scope answers 404, not 403 | Probed 2026-08-25 - reproduced live; nothing kept |
| Pull-request reactions use the issues endpoint | Probed 2026-08-26 - answered live; nothing kept |
| The reactions endpoint asks for the `repo` scope | Captured 2026-08-26 - a request against a repository that does not exist, so nothing was created |
| **A reaction was added, or was already there** | Unverified (docs) - re-running never duplicates a reaction |
| **A follow went through**, and the follow-state read | Unverified (docs) |
| Rate-limit signals, pagination, and listings | Unverified (docs) |
| A repository audience's usernames, public emails, and earliest commits | Unverified (docs) |

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Content queue columns and row states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Platform action matrix](/field-manual/action-matrix/) - safe versus risky actions, per platform.
