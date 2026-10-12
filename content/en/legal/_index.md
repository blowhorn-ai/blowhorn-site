---
title: Trust Center
heading: Blowhorn Trust Center
description: How Blowhorn handles your data, sessions and accounts, in plain language, and every policy that covers the Blowhorn website, the Blowhorn app for macOS and the Blowhorn Chrome extension.
lead: Blowhorn runs as many public voices as you need from one coordinated queue, and every action happens on your own Mac. This page collects every policy that covers the Blowhorn website, the Blowhorn app for macOS and its Chrome extension, with a plain-language summary of each. The summaries are a guide; where one differs from a policy, the policy decides.
layout: trust-center
lastmod: 2026-10-09
sitemap:
  changefreq: monthly
  priority: 0.5
# The plain-language summaries. Each one restates what the linked policy
# already says; add a card only for a promise a policy or a public doc makes.
glance:
  - title: Every action happens on your own Mac
    text: Blowhorn never acts for you from a server. Every post, comment and reaction is made by the Blowhorn app on one of your Macs, and in Chrome the Blowhorn extension acts only when that app asks. Your browser cookies for LinkedIn, X, Reddit and Hacker News stay in Chrome on that Mac and never leave it.
    link: /legal/privacy/#on-your-mac
    linkText: What stays on your Mac
  - title: The extension reports to no server
    text: The extension talks only to the Blowhorn app on your Mac, over Chrome's native messaging. It acts only on the sites Blowhorn supports, only in the Chrome profiles you install it in, and it keeps nothing itself.
    link: /legal/privacy/#in-chrome-through-the-blowhorn-extension
    linkText: What the extension reads
  - title: No analytics, no crash reports, no cookies
    text: The app carries no analytics or crash-reporting library. This website sets no cookies, runs no analytics and loads nothing from third parties. While you browse, its one outside request is the release lookup on GitHub. The newsletter form sends your email address to Mailchimp only when you submit it, and the privacy page describes both.
    link: /legal/privacy/#this-website
    linkText: What this website does
  - title: One store for your queue, analytics and credentials
    text: Your account keeps your content queue, schedule, profiles, run history, analytics and platform credentials in sync. That is what lets you sign in on any number of Macs, yours or your teammates', and run them as one fleet. Every Mac works from the same queue, coordinated so the same post isn't sent from two of them, and your analytics show the complete picture. Layer5's privacy policy governs that data.
    link: /legal/privacy/#in-your-organizations-store-on-layer5-cloud
    linkText: What your account keeps
  - title: You approve what goes out
    text: Blowhorn publishes the rows you approve and the commands you run, from the accounts you configure. A dry run publishes nothing, and on Hacker News Blowhorn submits and comments only; it never votes.
    link: /legal/terms/#your-accounts
    linkText: Your accounts and your content
  - title: Releases you can check
    text: The official downloads are signed disk images published with a SHA256SUMS.txt file to check them against, and a release is never replaced in place. The Blowhorn software is licensed under the AGPL-3.0.
    link: /legal/terms/#downloads
    linkText: Official downloads
# The policies, as cards. `status` marks a policy the reader must know is not final.
policies:
  - title: Privacy
    summary: What the Blowhorn website, the app and the extension store, where they store it, and what the app sends.
    url: /legal/privacy/
  - title: Terms of service
    summary: The agreement between you and Layer5 for the website, the app and the extension, from early access and downloads to acceptable use.
    url: /legal/terms/
    status: Draft, pending legal review
  - title: Chrome extension permissions
    summary: Each permission the Blowhorn extension asks for, the sites it runs on, and why.
    url: /docs/reference/extension-permissions/
  - title: Where your data lives
    summary: What stays on your Mac, what your account keeps in sync, and what the extension reads.
    url: /docs/explanation/your-data/
  - title: Layer5 Trust Center
    summary: Layer5's own privacy policy, terms of service and other policies, which cover your account and every other Layer5 service.
    url: https://layer5.io/company/legal/
---

## Report a security issue

If you think you have found a security vulnerability in Blowhorn, send the details privately to [security@blowhorn.ai](mailto:security@blowhorn.ai) rather than opening a public issue. Layer5 acknowledges and analyzes each report within 10 working days and keeps the reporter updated while it is addressed. The [security policy](https://github.com/layer5io/blowhorn-site/blob/master/SECURITY.md) explains what to report and how fixes are disclosed.

## Questions

- About privacy: open an issue on the [site repository](https://github.com/layer5io/blowhorn-site/issues), or contact Layer5 through the channels on its [privacy policy](https://layer5.io/company/legal/privacy/).
- About the terms: email [legal@layer5.io](mailto:legal@layer5.io).

## Changes to these policies

Each policy shows the date it last changed at the top of its page, and every edit to these pages is recorded in the [site repository's history](https://github.com/layer5io/blowhorn-site/commits/master/content/en/legal).
