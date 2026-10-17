---
title: "Amplify an existing post"
description: "Repost, retweet, quote, upvote, or react to a post from every profile."
weight: 90
aliases: [/docs/how-to/amplify-a-post/]
---


Repost, retweet, quote, upvote, or react to something already published,
from a content row. Put the URL in the row's `Amplify` column and set
`Message Text` only when you add your own words:

| Platform | `Amplify` | `Message Text` | Result |
| --- | --- | --- | --- |
| LinkedIn | post URL | empty | repost |
| LinkedIn | post URL | your words | repost with thoughts |
| X | post URL | empty | retweet |
| X | post URL | your words | quote |
| Reddit | thread URL | empty, and `Comment on` empty | upvote |
| Bluesky | post URL | empty | repost |
| GitHub | issue or PR URL | ignored | all five reactions |

{{< major >}}Your launch deserves more than nine likes. Fall in, profiles.{{< /major >}}

```bash
blowhorn post --platform linkedin --profile marcus --dry-run
blowhorn post --platform linkedin --profile marcus
```

On X and Reddit, `--amplify` with a URL overrides the row's `Amplify`
column for the whole run. You still need the rows: the flag retargets
them, it does not replace them. On GitHub the flag needs no row at all
([Amplify an issue or pull request on GitHub](/docs/how-to/publish/amplify-on-github/)).

## What Blowhorn refuses to amplify twice

On LinkedIn and X, a profile never amplifies its own post: when the
`Amplify` URL names the acting profile's own author, that profile is left
out of the run. The guard reads the author against the profile's handle,
so a LinkedIn or X amplify row whose profile has no handle stays pending
with a warning naming the missing handle, instead of running blind.

Both halves of a LinkedIn amplify are guarded before anything is clicked:
a post that already carries the reaction is left alone, and a post the
profile already reposted is recorded as done with the amplify URL as its
link. Re-running a row that already went out is safe. A Bluesky repost
carries no such guard: once the row is done, leave it done.

## When your account cannot be updated

The `Date Promoted` write happens after the amplify went out, so losing
it does not undo anything: it hides it. The row stays pending and the
next run acts again, which the LinkedIn guards above make a no-op rather
than a duplicate. The write is retried on transient failures; when it
still fails, one loud `!!!` line names the row, the profile, and exactly
what went out publicly, the row counts as failed, and the rest of that
profile's queue is not attempted. Re-run once your account is reachable.

## Comments are a different column

Replying uses `Comment on`, never `Amplify`
([Reply to a post](/docs/how-to/publish/reply-to-a-post/)). A Reddit row whose `Comment on`
is a Reddit post or comment URL and whose `Message Text` is set comments,
even when it also carries a thread URL in `Destination` or `Amplify`.
With a malformed `Comment on` or no `Message Text`, the row upvotes or
posts instead.

## Related

- [Amplify an issue or pull request on GitHub](/docs/how-to/publish/amplify-on-github/) - the
  GitHub reaction set, scopes, and previews.
- [Reply to a post](/docs/how-to/publish/reply-to-a-post/) - the `Comment on` column.
- [Post content](/docs/how-to/publish/post-content/) - running `blowhorn post` in general.
- [Why a public action is never repeated](/docs/explanation/reliability-and-anti-bot-design/) -
  the rule behind the guards.
- [You're in control](/docs/explanation/youre-in-control/) - the limits on every amplify
