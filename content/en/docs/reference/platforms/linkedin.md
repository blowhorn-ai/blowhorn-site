---
title: "LinkedIn"
linkTitle: "LinkedIn"
description: "What Blowhorn does on LinkedIn: actions, sign-in, and how much evidence stands behind each reading."
weight: 1
---

# LinkedIn

Browser, through the extension, in the Chrome profile you mapped. Posts
to the feed from a row; comments on a post when the row's "Comment on"
holds its address; amplifies by reposting. Sign-in is your LinkedIn
username and password in your Chrome, by hand; the credential Blowhorn
checks is `LI_USERNAME` with `LI_PASSWORD`.

## LinkedIn comments

A row with "Comment on" set to a `linkedin.com` post address and a
"Message Text" becomes a comment on that post instead of a new post.
The same row is also picked up by `blowhorn comment`. A row whose
"Comment on" names anything else stays a normal post.

## Captured versus unverified

How much evidence stands behind each reading Blowhorn takes on LinkedIn. [All platforms](/docs/reference/platforms/) explains what captured, probed, and unverified mean.

| State | Captured, probed or unverified |
|---|---|
| The Page composer's media and link-preview controls | Captured 2026-08-17 - a showcase Page |
| **A Page post landed: found in the Page's published list** | Probed 2026-08-18 - watched the check find a real post and refuse an absent one; nothing kept. The one landing Blowhorn confirms by going and looking |
| The Repost menu, the repost composer, the reaction control | Captured 2026-08-18 - a post page; a second wording on 2026-08-28 |
| The sign-in page's fields and submit control | Probed 2026-08-24 - a signed-out browser; nothing kept |
| The Accept control on received invitations | Captured 2026-08-25 - the received list |
| A row with no Accept control, and the toast after a real accept | Probed 2026-08-25 - the received list, watched live; nothing kept |
| A post's author, and whether you already reposted it | Captured 2026-08-28 - one post, six sessions, on both page designs |
| The withdraw confirmation | Probed 2026-08-10 - the sent list, during a manual run; nothing kept |
| **A feed post or a group post landed** | Unverified (model) - Blowhorn compares the newest item on your activity page or the group page before and after the click. A new item of yours marks the row done with its link; anything else holds the row as clicked, outcome not read |
| **A comment landed** | Unverified (model) - nothing is read after the click |
| **An instant repost landed** | Unverified (model) - the repost counts only when your activity feed shows it; otherwise the row is held as clicked, outcome not read, and Repost is not clicked again |
| **A repost with thoughts, or a like, landed** | Unverified (model) - nothing is read after the click; a repost with thoughts is held as clicked, outcome not read |
| **A Page post landed**: a toast, or the composer closing | Unverified (model) - a false "not sent" is caught by the published-list check above |
| **An acceptance or a withdrawal went through**: the row leaves the list | Unverified (model) - doubt halts the run; it never reports one that did not happen |
| The "Take care when connecting" warning | Unverified (model) - if missed, the flagged invitation stays on the list and is never accepted |
| Which page means signed in, signed out, or a challenge | Unverified (model) - a wrong reading falls back to signing in by hand |
| A new post's link | Unverified (model) - if wrong, the row records no link |
| Page analytics: date range, export, highlight labels | Unverified (model) - read-only; a wrong reading records a wrong number, or none |

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Content queue columns and row states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Field Manual: LinkedIn](/field-manual/linkedin/) - what the LinkedIn feed rewards and what it penalizes.
- [Platform action matrix](/field-manual/action-matrix/) - safe versus risky actions, per platform.
