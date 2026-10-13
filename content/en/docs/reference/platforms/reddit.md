---
title: "Reddit"
linkTitle: "Reddit"
description: "What Blowhorn does on Reddit: actions, sign-in, and how much evidence stands behind each reading."
weight: 3
---

# Reddit

Browser, through the extension. Posts to the subreddit the row's
"Destination" names as `r/<name>`; with no subreddit the row is
skipped, never guessed. Comments when "Comment on" holds a Reddit post
or comment address. Amplifies with an upvote. Sign-in is your Reddit
username in your Chrome, by hand; the credential Blowhorn checks is
`RDDT_USERNAME`.

## Reddit posts and comments

Posting needs the subreddit in "Destination" or, for an upvote, in
"Amplify". Commenting needs a Reddit address in "Comment on" plus a
"Message Text". Both `post` and `comment` act on comment rows; a row
already marked done is never acted on twice.

## Captured versus unverified

How much evidence stands behind each reading Blowhorn takes on Reddit. [All platforms](/docs/reference/platforms/) explains what captured, probed, and unverified mean.

| State | Captured, probed or unverified |
|---|---|
| **A new post landed**: the browser reaches the post's comments page | Unverified (model) - Blowhorn then looks for your title on that page. A match marks the row done; anything else holds it as clicked, outcome not read, and it is not posted again |
| **A comment, reply, or upvote landed** | Unverified (model) - nothing is read after the click; the row is held as clicked, outcome not read |
| A new comment's link | Unverified (model) - printed when read, not recorded |
| The upvote control and its already-upvoted state | Unverified (model) - if that is not the real signal, a second run could undo the upvote |
| The switch to Markdown | Unverified (model) - if missed, Markdown publishes as literal characters |
| The submit form, comment box, session markers, sign-in, and challenges | Unverified (model) - a miss sends nothing, or falls back to signing in by hand |

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Content queue columns and row states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Field Manual: Reddit](/field-manual/reddit/) - what the Reddit feed rewards and what it penalizes.
- [Platform action matrix](/field-manual/action-matrix/) - safe versus risky actions, per platform.
