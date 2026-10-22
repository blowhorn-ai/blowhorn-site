---
title: "Content queue columns and activity states"
description: "Every content column, what each platform reads from an activity, and what each activity state means."
weight: 213
---


The queue is the set of content activities `blowhorn post` publishes. Each
activity is one message; each run publishes the activities that are still owed to
the profiles in scope. Columns may arrive in any order, and extra
columns beside them are preserved on write.

## Columns

| Column | Means | Read by |
|---|---|---|
| Platform | Where the activity goes: `linkedin`, `x`, `reddit`, `hn`, `slack`, `bluesky`, or `github` (`twitter` reads as `x`, `bsky` as `bluesky`; `Venue` is the old spelling) | Every run, as the platform gate |
| Profile | Which profile publishes it; blank or naming nothing resolvable is refused, never widened to everybody | The profile match |
| Destination | Where on the platform: a subreddit as `r/<name>` for Reddit; the channel, person, or thread for Slack's "Amplify" use | Reddit, Slack |
| Message Text | The message itself | Every platform that publishes |
| Title | The title where the platform needs one: Hacker News submissions | Hacker News |
| Encoded Post | The pre-encoded form, when the activity carries one | The post path |
| Approved? | `yes` or `true` selects the activity; anything else leaves it out | `get_posts_to_process` |
| Promote On | When the activity becomes due; unparseable is refused, never guessed | The due check |
| Date Promoted | When each profile published it; clear it to try the activity again | The done bookkeeping |
| Promotion Link | Where the published post landed, when a read-back showed it | Reporting |
| GDrive Link | Drive attachment source for activities that carry one | The post path |
| Image URL | Image attached to the post | Platforms that take images |
| Video URL | Video attached to the post | Platforms that take video |
| Amplify | Address of existing content to amplify instead of publishing: a post URL for repost, retweet, quote, or upvote; an issue or pull request for GitHub reactions; a Slack channel, person, or thread as the send target | The amplify path per platform |
| Comment on | Address to comment on instead of publishing: a LinkedIn, Reddit, or Bluesky post or comment address with a Message Text | `post` and `comment` |

An activity with "Comment on" set can only ever be a comment. An activity with an
"Amplify" GitHub target can only ever be reactions. Timestamps in
content values read `%Y-%m-%d %H:%M:%S`.

## Activity states

| State | Means |
|---|---|
| pending | Eligible by the activity's own fields; whether a profile picks it up is per-profile |
| scheduled | Due in the future under "Promote On" |
| partial | Landed for some profiles, still owed to others |
| done | Published and recorded, with "Date Promoted" stamped |
| unread | Clicked, outcome not read: the sending control was clicked and no confirmation was read back. Not pending again, and not done. "Date Promoted" carries `clicked, outcome not read` and no promotion link is written |
| draft | Not yet approved for publishing |
| invalid | Refused: an unresolvable profile, a blank profile, an unparseable date, an overlong HN title |
| unsupported | Names a platform no command in scope acts on |

Clearing an unread activity's "Date Promoted" tries the activity again. Neither a
retry nor a drop is a run's to decide: the run records, you decide.

## Related

- [Manage the content queue](/docs/how-to/publish/manage-the-content-worksheet/) - add, edit, and approve activities.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the run that reads the activities.
- [Post to Hacker News](/docs/how-to/publish/post-to-hacker-news/) - titles, caps, permanence.
- [Platforms](/docs/reference/platforms/) - what each platform does with an activity.
- [Messages and exit codes](/docs/reference/messages/) - what each refusal sentence means.
- [How Blowhorn avoids repeat posts](/docs/explanation/never-twice/) - why unread is not done.
