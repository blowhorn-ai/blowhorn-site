---
title: "Platforms"
description: "What Blowhorn does on each platform: actions, browser or API, sign-in, and limits."
weight: 212
no_list: true
anchor_redirects:
  linkedin: "/docs/reference/platforms/linkedin/"
  linkedin-comments: "/docs/reference/platforms/linkedin/"
  linkedin-1: "/docs/reference/platforms/linkedin/"
  x-twitter: "/docs/reference/platforms/x/"
  x-twitter-replies: "/docs/reference/platforms/x/"
  x: "/docs/reference/platforms/x/"
  reddit: "/docs/reference/platforms/reddit/"
  reddit-posts-and-comments: "/docs/reference/platforms/reddit/"
  reddit-1: "/docs/reference/platforms/reddit/"
  hacker-news: "/docs/reference/platforms/hacker-news/"
  hacker-news-submissions-and-comments: "/docs/reference/platforms/hacker-news/"
  hacker-news-1: "/docs/reference/platforms/hacker-news/"
  slack: "/docs/reference/platforms/slack/"
  slack-messages: "/docs/reference/platforms/slack/"
  slack-1: "/docs/reference/platforms/slack/"
  bluesky: "/docs/reference/platforms/bluesky/"
  bluesky-1: "/docs/reference/platforms/bluesky/"
  github: "/docs/reference/platforms/github/"
  github-1: "/docs/reference/platforms/github/"
  youtube: "/docs/reference/platforms/youtube/"
  instagram: "/docs/reference/platforms/instagram/"
  tiktok: "/docs/reference/platforms/tiktok/"
  facebook: "/docs/reference/platforms/facebook/"
---

# Platforms

What Blowhorn can do on each platform, how it reaches
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

Each platform has its own page:

<div class="grid grid-2 platform-cards">
  <a class="card docs-card platform-card" href="/docs/reference/platforms/linkedin/">
    <span class="h3">LinkedIn</span>
    <span>Browser, through the extension</span>
  </a>
  <a class="card docs-card platform-card" href="/docs/reference/platforms/x/">
    <span class="h3">X (Twitter)</span>
    <span>Browser, through the extension</span>
  </a>
  <a class="card docs-card platform-card" href="/docs/reference/platforms/reddit/">
    <span class="h3">Reddit</span>
    <span>Browser, through the extension</span>
  </a>
  <a class="card docs-card platform-card" href="/docs/reference/platforms/hacker-news/">
    <span class="h3">Hacker News</span>
    <span>Browser, through the extension</span>
  </a>
  <a class="card docs-card platform-card" href="/docs/reference/platforms/slack/">
    <span class="h3">Slack</span>
    <span>API, never the browser</span>
  </a>
  <a class="card docs-card platform-card" href="/docs/reference/platforms/bluesky/">
    <span class="h3">Bluesky</span>
    <span>API, never the browser</span>
  </a>
  <a class="card docs-card platform-card" href="/docs/reference/platforms/github/">
    <span class="h3">GitHub</span>
    <span>API, never the browser</span>
  </a>
  <a class="card docs-card platform-card" href="/docs/reference/platforms/youtube/">
    <span class="h3">YouTube</span>
    <span>Coming soon - not generally available yet</span>
  </a>
  <a class="card docs-card platform-card" href="/docs/reference/platforms/instagram/">
    <span class="h3">Instagram</span>
    <span>Coming soon - not generally available yet</span>
  </a>
  <a class="card docs-card platform-card" href="/docs/reference/platforms/tiktok/">
    <span class="h3">TikTok</span>
    <span>Coming soon - not generally available yet</span>
  </a>
  <a class="card docs-card platform-card" href="/docs/reference/platforms/facebook/">
    <span class="h3">Facebook</span>
    <span>Coming soon - not generally available yet</span>
  </a>
</div>

YouTube, Instagram, TikTok, and Facebook are coming soon. Early work
exists in the app, but none of them is generally available yet, and
`blowhorn post --platform` does not list them. Each page says what
exists today.

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

Each platform page carries its own table.

## Related


- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Post to Hacker News](/docs/how-to/publish/post-to-hacker-news/) - the strictest platform, worked.
- [Content queue columns and row states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Send a Slack message](/docs/how-to/publish/send-a-slack-message/) - Slack, worked.
- [Platform action matrix](/field-manual/action-matrix/) - which actions are safe and which risk a penalty, per platform.
