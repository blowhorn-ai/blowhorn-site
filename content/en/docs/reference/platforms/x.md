---
title: "X (Twitter)"
linkTitle: "X (Twitter)"
description: "What Blowhorn does on X (Twitter): actions, sign-in, and how much evidence stands behind each reading."
weight: 2
---

# X (Twitter)

Browser, through the extension. Posts from a row; a message past 274
characters goes out as a thread. Replies go through a post row that
targets the conversation. Amplifies by retweet or quote. Follows
accounts with `blowhorn follow`. Analytics appends a
follower and following trend row per run. Sign-in is your X username in
your Chrome, by hand; the credential Blowhorn checks is `X_USERNAME`.

Follows: at most 400 per profile a day and 15 in any 15 minutes,
counted from that profile's follow log on this Mac.

## X (Twitter) replies

Replying is a post row addressed at the conversation, not a separate
command. There is no comment flow for X under `blowhorn comment`.

## Captured versus unverified

How much evidence stands behind each reading Blowhorn takes on X (Twitter). [All platforms](/docs/reference/platforms/) explains what captured, probed, and unverified mean.

| State | Captured, probed or unverified |
|---|---|
| The signed-in markers on a profile page | Captured 2026-08-07 - a signed-in profile page |
| The sign-in username step: two forms, the dialog field, Continue | Captured 2026-09-17 - a signed-out page, nothing submitted |
| **A post or thread landed** | Unverified (model) - after the dialog closes, Blowhorn reads the post back under your own handle. A match marks the row done; anything else holds it as clicked, outcome not read. Post is clicked once per run |
| **A repost, reply, like, or follow landed** | Unverified (model) - nothing is read after the click; a repost or reply is held as clicked, outcome not read, and a follow is skipped next time but not counted as followed |
| A new post's link | Unverified (model) - if wrong, the row records no link |
| The compose page, editor, Post button, and media button | Unverified (model) - a miss sends nothing; a failed upload posts the text without its image |
| The password step, signed-out markers, and challenge wording | Unverified (model) - a wrong reading falls back to signing in by hand |
| The follower and following counts | Unverified (model) - read-only |
| The 274-character limit | Unverified (model) - if wrong, a post splits into a thread early |

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Content queue columns and row states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Field Manual: X](/field-manual/x/) - what the X feed rewards and what it penalizes.
- [Platform action matrix](/field-manual/action-matrix/) - safe versus risky actions, per platform.
