---
title: "Post content"
description: "Preview and publish queued posts across profiles and platforms."
weight: 70
aliases: [/docs/how-to/post-content/]
---


Publish the rows waiting in the content queue.

## Check what a run would pick up

Nothing is published, nothing is written back:

```bash
blowhorn post --check-queue
blowhorn post --check-queue --profile marcus --platform linkedin
```

`--check-queue` is read-only: it opens no browser and reaches no platform.

## Publish the queue

```bash
blowhorn post --profile marcus                       # every platform with pending rows
blowhorn post --platform linkedin --profile marcus --headless   # unattended: a background window, never headless
blowhorn post --profile all --exclude marcus,kanvas  # fan out, holding profiles back
```

`--profile all` leaves out the excluded profiles (`--exclude`, else
`BLOWHORN_EXCLUDE`, else `defaults.exclude`) and prints `Excluding
profiles: …` when it does. To post as one of them, name it:
`--profile marcus`.

Rehearse first whenever the result matters. A dry run goes end to end
without publishing and without marking the row done:

```bash
blowhorn post --profile marcus --dry-run
```

A dry run still signs in where a real run would: on Hacker News it opens
the browser and signs in exactly as a real run does, then stops short of
the submit.

## Amplify or reply from the command line

On X and Reddit, `--amplify` with the post URL amplifies it for this run
(retweet, quote, or upvote), overriding the row's `Amplify` column.
Replies ride on the row's `Comment on` column with `Message Text`. The full
forms are [Amplify an existing post](/docs/how-to/publish/amplify-a-post/) and
[Reply to a post](/docs/how-to/publish/reply-to-a-post/). GitHub amplify and the one-off
Slack message need no row at all; each has its own page.

## Slow a long unattended run down

```bash
blowhorn post --profile all --pace slow
```

`--pace` takes `fast`, `normal`, `slow`, or a numeric multiplier such as
`2.0`.

## Attaching an image to a LinkedIn post

A row that fills `Image URL`, `GDrive Link`, or `Video URL` attaches that
file to the post. Two things are worth knowing when such a post fails:

- A row whose text holds a URL and an image keeps the image: Blowhorn
  removes the link preview LinkedIn generates first, because the preview
  takes the slot the image needs. A row with a URL and no image keeps its
  preview.
- A post never goes out without the image it asked for. If the file cannot
  be attached, the row fails and stays pending for a later run. Re-run once
  the cause is understood rather than filling in `Date Promoted` to silence
  it.

## Related

- [Manage the content queue](/docs/how-to/publish/manage-the-content-worksheet/) - adding and
  editing the rows a run reads.
- [Amplify an existing post](/docs/how-to/publish/amplify-a-post/) - reposts, retweets,
  upvotes, GitHub reactions.
- [Reply to a post](/docs/how-to/publish/reply-to-a-post/) - comments and replies.
- [Send a Slack message](/docs/how-to/publish/send-a-slack-message/) - the one-off message
  that needs no row.
- [`blowhorn post` reference](/docs/reference/post/) - every flag, what
  "pending" means, and what a run writes back.
- [You're in control](/docs/explanation/youre-in-control/) - what stops a run going wrong
