---
title: "TikTok"
linkTitle: "TikTok"
description: "TikTok in Blowhorn: coming soon. What exists today, and what is not ready yet."
weight: 12
---

# TikTok

**Coming soon.** TikTok is not generally available yet. TikTok is not a supported platform. This page describes work in progress.

Early work for TikTok exists in the app, and it is not ready for your
posts. It works in your own signed-in Chrome, never from a server. What
exists today:

- **You sign in by hand.** Sign in to TikTok yourself in your own Chrome
  profile. Blowhorn never fills a sign-in form, never retries a failed
  sign-in and never runs without a visible browser. A sign-in wall,
  challenge or captcha stops TikTok for that profile and asks you to sign
  in.
- **A dry run comes first.** A dry run checks a post and shows the steps a
  live post would take, without touching the browser.
- **Limits apply.** Posts a video with a caption. A caption is at most 4,000 characters, and a video is at most 10 minutes long and 2 GB. Posting through TikTok's own API is a later phase.
- **The credential** Blowhorn checks is `TIKTOK_USERNAME`. It names your account; it
  is never a password.

Nothing has been confirmed against the real TikTok yet. Every reading
Blowhorn takes there is unverified until a first hand-supervised live post
confirms it, so don't rely on TikTok for real posts until this page says
otherwise.

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
