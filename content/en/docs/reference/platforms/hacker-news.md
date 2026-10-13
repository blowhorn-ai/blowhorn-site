---
title: "Hacker News"
linkTitle: "Hacker News"
description: "What Blowhorn does on Hacker News: actions, sign-in, and how much evidence stands behind each reading."
weight: 4
---

# Hacker News

Browser, through the extension, signed in with the username and
password in your account (`HN_USERNAME` with `HN_PASSWORD`). Submits link
and text posts and comments from rows. Titles hold 80 characters;
a longer title fails the row rather than truncating, because a
submission cannot be edited after it lands. At most 2 link submissions
per profile per UTC day count; only link submissions are recorded, so
only they count toward the cap. Blowhorn never votes: there is nothing
to configure and no way to turn it on.

## Hacker News submissions and comments

A link row needs the URL; a text post needs the title and text. A row
with "Comment on" set becomes a comment on that item. Every submission
is permanent and every comment lands under your name, so preview each
new row with `--dry-run` first. Submissions HN rate-limits fail the
row; see [Messages and exit codes](/docs/reference/messages/).

## Captured versus unverified

How much evidence stands behind each reading Blowhorn takes on Hacker News. [All platforms](/docs/reference/platforms/) explains what captured, probed, and unverified mean.

| State | Captured, probed or unverified |
|---|---|
| The sign-in page's two forms, and `/submit` signed out | Captured 2026-08-18 - signed out, read-only |
| Story and comment rows, permalinks, and the comment form | Captured 2026-08-18 - an item page, signed out |
| The expired-link page | Captured 2026-08-18 - signed out |
| The signed-out top bar and bylines | Captured 2026-08-18 - listing and item pages |
| The read-only API's answers | Captured 2026-08-18 - user and item lookups, unauthenticated |
| The signed-in submit form | Captured 2026-09-18 - saved by hand, session tokens removed |
| Form pages show no logout link even signed in | Captured 2026-09-18 - `/submit` and `/reply` |
| The signed-in top bar, reply links, and vote arrows | Captured 2026-09-18 - item and listing pages. Blowhorn never clicks an arrow |
| **A reply landed**: the story page, with the new comment carrying edit and delete links | Captured 2026-09-18 - after a reply posted by hand. The one landing captured on any platform |
| **A story landed** | Unverified (model) - if neither the page nor the API confirms it, the story is reported unconfirmed |
| HN sends a repeat URL to the existing story | Unverified (docs) |
| The API lists a new story within seconds | Unverified (model) |
| The rate-limit pages and the reCAPTCHA signal | Unverified (model) - a limiter worded otherwise is missed for one more attempt |
| A comment's own page shows the reply form | Unverified (model) - if not, the row fails with "No comment form" and nothing is posted |
| **A top-level comment landed** | Unverified (model) - if wrong, the comment is reported unfound; the row is still done with the thread's link |

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Post to Hacker News](/docs/how-to/publish/post-to-hacker-news/) - the strictest platform, worked.
- [Content queue columns and row states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Field Manual: Hacker News](/field-manual/hacker-news/) - what the Hacker News feed rewards and what it penalizes.
- [Platform action matrix](/field-manual/action-matrix/) - safe versus risky actions, per platform.
