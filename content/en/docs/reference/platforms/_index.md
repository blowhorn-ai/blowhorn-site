---
title: "Platforms"
description: "What Blowhorn does on each platform: supported actions, browser or API, sign-in, and limits."
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

Each platform has its own page, listing its supported actions and how each one behaves there:

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
</div>

## Related


- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Post to Hacker News](/docs/how-to/publish/post-to-hacker-news/) - the strictest platform, worked.
- [Content queue columns and row states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Send a Slack message](/docs/how-to/publish/send-a-slack-message/) - Slack, worked.
- [Platform action matrix](https://blowhorn.ai/field-manual/action-matrix/) - which actions are safe and which risk a penalty, per platform.
