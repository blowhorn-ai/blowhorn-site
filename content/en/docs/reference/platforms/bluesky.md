---
title: "Bluesky"
linkTitle: "Bluesky"
description: "What Blowhorn does on Bluesky: actions, sign-in, and how much evidence stands behind each reading."
weight: 6
---

# Bluesky

API, never the browser. Posts up to 300 characters per post; longer
messages split into threads. Reposts for amplify rows. Follows with
`blowhorn follow`, unfollows one account with `blowhorn unfollow`,
searches posts with `blowhorn find`. Analytics appends a follower and
following trend row per run. The credential is `BLUESKY_HANDLE` with
`BLUESKY_APP_PASSWORD`: an app password, not your main password.

## Captured versus unverified

How much evidence stands behind each reading Blowhorn takes on Bluesky. [All platforms](/docs/reference/platforms/) explains what captured, probed, and unverified mean.

| State | Captured, probed or unverified |
|---|---|
| **A post, repost, reply, follow, or unfollow was accepted** | Unverified (docs) - the SDK's documented answers, never recorded from a real response |
| A post's link, built from your handle and the answer | Unverified (docs) - built, not read |
| The sign-in errors that separate a refused app password from an outage | Unverified (docs) - misread, you could be told to replace an app password that works |
| The 300-character limit, link shapes, and thread and profile reads | Unverified (docs) |
| Where to create an app password, as the refusal tells you | Unverified (model) |

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Content queue columns and row states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Field Manual: Bluesky](/field-manual/bluesky/) - what the Bluesky feed rewards and what it penalizes.
- [Platform action matrix](/field-manual/action-matrix/) - safe versus risky actions, per platform.
