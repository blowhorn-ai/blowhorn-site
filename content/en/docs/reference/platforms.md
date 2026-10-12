---
title: "Platforms"
description: "What Blowhorn does on each platform: actions, browser or API, sign-in, and limits."
weight: 212
---

# Platforms

What Blowhorn can do on each of the seven platforms, how it reaches
each one, and the limits it honors. This page describes; the steps live
in the how-to guides linked under Related.

{{< major >}}Two hundred seventy-four characters before X wants a thread. I don't make the rules. I thread them.{{< /major >}}

Four platforms drive your own signed-in Chrome through the extension:
LinkedIn, X, Reddit, and Hacker News. Three post through their APIs
above the browser: Slack, Bluesky, and GitHub. A platform is usable the
moment its credential exists; see [Who can post as whom](/docs/explanation/eligibility/).

`blowhorn post --platform` accepts one of: `linkedin`, `x`, `reddit`,
`hn`, `slack`, `bluesky`, `github`, or `all`. `twitter` reads as `x`
and `bsky` as `bluesky`. GitHub is amplify-only under `post`: it needs
an issue or pull-request URL and refuses without one.

## LinkedIn

Browser, through the extension, in the Chrome profile you mapped. Posts
to the feed from a row; comments on a post when the row's "Comment on"
holds its address; amplifies by reposting. Sign-in is your LinkedIn
username and password in your Chrome, by hand; the credential Blowhorn
checks is `LI_USERNAME` with `LI_PASSWORD`.

### LinkedIn comments

A row with "Comment on" set to a `linkedin.com` post address and a
"Message Text" becomes a comment on that post instead of a new post.
The same row is also picked up by `blowhorn comment`. A row whose
"Comment on" names anything else stays a normal post.

## X (Twitter)

Browser, through the extension. Posts from a row; a message past 274
characters goes out as a thread. Replies go through a post row that
targets the conversation. Amplifies by retweet or quote. Follows
accounts with `blowhorn follow`. Analytics appends a
follower and following trend row per run. Sign-in is your X username in
your Chrome, by hand; the credential Blowhorn checks is `X_USERNAME`.

Follows: at most 400 per profile a day and 15 in any 15 minutes,
counted from that profile's follow log on this Mac.

### X (Twitter) replies

Replying is a post row addressed at the conversation, not a separate
command. There is no comment flow for X under `blowhorn comment`.

## Reddit

Browser, through the extension. Posts to the subreddit the row's
"Destination" names as `r/<name>`; with no subreddit the row is
skipped, never guessed. Comments when "Comment on" holds a Reddit post
or comment address. Amplifies with an upvote. Sign-in is your Reddit
username in your Chrome, by hand; the credential Blowhorn checks is
`RDDT_USERNAME`.

### Reddit posts and comments

Posting needs the subreddit in "Destination" or, for an upvote, in
"Amplify". Commenting needs a Reddit address in "Comment on" plus a
"Message Text". Both `post` and `comment` act on comment rows; a row
already marked done is never acted on twice.

## Hacker News

Browser, through the extension, signed in with the username and
password in your account (`HN_USERNAME` with `HN_PASSWORD`). Submits link
and text posts and comments from rows. Titles hold 80 characters;
a longer title fails the row rather than truncating, because a
submission cannot be edited after it lands. At most 2 link submissions
per profile per UTC day count; only link submissions are recorded, so
only they count toward the cap. Blowhorn never votes: there is nothing
to configure and no way to turn it on.

### Hacker News submissions and comments

A link row needs the URL; a text post needs the title and text. A row
with "Comment on" set becomes a comment on that item. Every submission
is permanent and every comment lands under your name, so preview each
new row with `--dry-run` first. Submissions HN rate-limits fail the
row; see [Messages and exit codes](/docs/reference/messages/).

## Slack

API, never the browser. Sends a message as you to a channel, a person,
or a thread: the target is `#channel`, `@user`, a channel id, a channel
link, or a message link for a thread reply. One profile sends; the
credential is a Slack token in your account (`SLACK_USER_TOKEN`,
`SLACK_BOT_TOKEN`, or a workspace session captured through the
extension). `blowhorn post --platform slack --message` sends one ad-hoc
message with no queue row.

### Slack messages

Send from a queue row or ad hoc. A row sends to its own target; `--message`
with `--target` sends one message you type, with no row read or marked
done, and `--target` redirects the run's queued Slack rows. The target
is a `#channel`, `@user`, channel id, channel link, or message link for
a thread reply; anything else is refused, never sent somewhere else.
One profile sends per run, named with `--profile`; the profile from
the defaults file does not count as named.

## Bluesky

API, never the browser. Posts up to 300 characters per post; longer
messages split into threads. Reposts for amplify rows. Follows with
`blowhorn follow`, unfollows one account with `blowhorn unfollow`,
searches posts with `blowhorn find`. Analytics appends a follower and
following trend row per run. The credential is `BLUESKY_HANDLE` with
`BLUESKY_APP_PASSWORD`: an app password, not your main password.

## GitHub

API, never the browser. Follows accounts with `blowhorn follow` and
lists an audience with `blowhorn source --platform github --repo`.
Under `post`, GitHub amplifies only: it adds all five uplifting
reactions (+1, laugh, hooray, heart, rocket) to the issue or pull
request the `--amplify` flag or the row's "Amplify" column names, from
every selected profile under its own token. Re-running adds none of
them twice. The credential is `GH_TOKEN` in your account.

## Captured versus unverified, by platform

Blowhorn works on each platform by reading signals off it: a selector,
a button's wording, the page a submit lands on, the shape of an API
answer. Each table below says how much evidence stands behind each of
those readings, so you know how far to trust a line in your run's
output. There are three kinds, strongest first:

- **Captured** - a saved page, a dump, or quoted markup from the real
  service stands behind it, on a known date.
- **Probed** - someone watched the real service do it on a known date
  and kept nothing of the page.
- **Unverified** - never observed against the real service; written
  from a model of the site or from its documentation.

Unverified is a statement about Blowhorn's evidence, not a claim that a
platform is broken or that your post will fail. What it changes is
what your run tells you: where a success rests on an unverified
reading, the run says what it did or read - `Clicked Like; nothing was
read to confirm LinkedIn accepted it.` - rather than stating the
outcome as a fact. Where nothing could be read after a click, the row
is recorded as *clicked, outcome not read*: it is not counted, not
repeated, and waits for you to check it.

Only one landing after a submit has been captured on any platform: a
Hacker News reply, on 2026-09-18. A run that worked and a green test
suite never upgrade a reading; only a dated capture of the page a
submit lands on does.

### LinkedIn

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

### X

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

### Reddit

| State | Captured, probed or unverified |
|---|---|
| **A new post landed**: the browser reaches the post's comments page | Unverified (model) - Blowhorn then looks for your title on that page. A match marks the row done; anything else holds it as clicked, outcome not read, and it is not posted again |
| **A comment, reply, or upvote landed** | Unverified (model) - nothing is read after the click; the row is held as clicked, outcome not read |
| A new comment's link | Unverified (model) - printed when read, not recorded |
| The upvote control and its already-upvoted state | Unverified (model) - if that is not the real signal, a second run could undo the upvote |
| The switch to Markdown | Unverified (model) - if missed, Markdown publishes as literal characters |
| The submit form, comment box, session markers, sign-in, and challenges | Unverified (model) - a miss sends nothing, or falls back to signing in by hand |

### Hacker News

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

### Bluesky

| State | Captured, probed or unverified |
|---|---|
| **A post, repost, reply, follow, or unfollow was accepted** | Unverified (docs) - the SDK's documented answers, never recorded from a real response |
| A post's link, built from your handle and the answer | Unverified (docs) - built, not read |
| The sign-in errors that separate a refused app password from an outage | Unverified (docs) - misread, you could be told to replace an app password that works |
| The 300-character limit, link shapes, and thread and profile reads | Unverified (docs) |
| Where to create an app password, as the refusal tells you | Unverified (model) |

### Slack

| State | Captured, probed or unverified |
|---|---|
| **A message was posted**: Slack answers `ok` | Unverified (docs) - never recorded from a real response |
| A message's link, built from the answer | Unverified (docs) |
| How a captured workspace session is used | Unverified (model) - Slack's web client convention, undocumented by Slack |
| Capturing a workspace session from your browser | Unverified (model) - a miss captures nothing and posts nothing |
| Sign-in errors, OAuth answers, and link shapes | Unverified (docs) |
| A resend is not duplicated | Unverified (docs) - Blowhorn's own send record keeps each send to once |
| The marks of an app-attributed message | Unverified (docs) - a miss reports an attributed message as clean |
| A rate limit's wait, and an unreadable answer | Unverified (docs, model) - such a send is marked outcome unknown and never resent |

### GitHub

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

- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Post to Hacker News](/docs/how-to/publish/post-to-hacker-news/) - the strictest platform, worked.
- [Content queue columns and row states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Send a Slack message](/docs/how-to/publish/send-a-slack-message/) - Slack, worked.
