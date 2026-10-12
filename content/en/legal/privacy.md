---
title: Privacy
heading: What Blowhorn stores, and where
description: What the Blowhorn website and the Blowhorn app store, where they store it, and what the app sends.
lead: Last updated 9 October 2026. This page covers this website, the Layer5 Blowhorn app and its Chrome extension. Layer5's own [privacy policy](https://layer5.io/company/legal/privacy/) covers Layer5 Cloud and every other Layer5 service.
layout: legal
weight: 10
aliases:
  - /privacy.html
lastmod: 2026-10-09
sitemap:
  changefreq: yearly
  priority: 0.3
---

## This website

blowhorn.ai is a static site served by GitHub Pages. It sets no cookies, runs no analytics and loads no fonts, images, styles or scripts from third parties: they are all served from this site. While you browse, its one request to another host is the download page's release lookup, described below. The newsletter form in the footer sends nothing unless you submit it.

- GitHub serves the pages and keeps its own server logs. Those are covered by the [GitHub privacy statement](https://docs.github.com/site-policy/privacy-policies/github-privacy-statement).
- The download page asks GitHub's public API for the newest release from your browser. That request reaches GitHub like any other request your browser makes, with your IP address and the usual request headers. With JavaScript off, no request is made and the page links to the releases page instead.

### Newsletter signup

The footer has the site's one form, a signup for the Layer5 newsletter. It is the same list as the signup on layer5.io. It is a plain HTML form with no script, and nothing leaves your browser until you press Subscribe.

- What is sent: the email address you type. The form has no other fields, visible or hidden. Like any site your browser contacts, Mailchimp also receives your IP address and the usual request headers.
- Who receives it: Layer5, which keeps the list on Mailchimp, an Intuit company, as its email provider. [Layer5's privacy policy](https://layer5.io/company/legal/privacy/) covers the list and names Mailchimp among its email providers. Mailchimp's own handling is covered by the [Intuit privacy statement](https://www.intuit.com/privacy/statement/).
- What it is for: the Layer5 newsletter. Signing up does not create a Blowhorn account and adds nothing to your organization's store.
- Where you go: submitting takes you from blowhorn.ai to a Mailchimp page on list-manage.com. That page is Mailchimp's, not this site's, and Mailchimp sets its own cookies there, including for bot protection. blowhorn.ai sets none.
- Leaving the list: every newsletter email has an unsubscribe link.

## The Blowhorn app

### On your Mac

- Browser sessions for LinkedIn, X, Reddit and Hacker News, meaning the cookies Chrome keeps for those sites, live in Chrome profiles on your machine. They never leave it.
- Every action Blowhorn takes runs on one of your Macs. Blowhorn never signs in or acts for you from a server.
- Configuration lives in `.blowhorn.yaml` inside the installation. The store connection, including its password, lives in `~/.config/blowhorn/store.yaml`, readable only by your user account.
- For LinkedIn, X, Reddit and Bluesky, the password a run signs in with is read from `profiles/<name>/config.yaml` inside the installation, and `blowhorn profile set` writes it there.
- The app keeps its cached copy of your organization's plan features in your macOS Keychain.
- Run logs are written to the `logs/` directory of the installation. The menu-bar app keeps its preferences and state under `~/Library/Application Support/Blowhorn/`.

### In Chrome, through the Blowhorn extension

The extension works only for the Blowhorn app on your Mac, over Chrome's native messaging. It acts only on the sites Blowhorn supports, only in the Chrome profiles you install it in, and only when the app asks. Everything it reads goes to that app and nowhere else: it reports to no server of its own, and it keeps nothing itself.

- Sign-in information: a session cookie or token on a supported site, read when the app needs to reuse a sign-in you already have. Today that is your Slack workspace session, which the app keeps in your organization's store (below).
- Your communications: the posts, comments and messages the app asks it to enter and send as you.
- Page content: what a page shows, read to tell when an action has finished; a screenshot when an action needs a person to check it; and an export you asked a site for, such as an analytics or connections export, which it catches and hands to the app.

### In your organization's store on Layer5 Cloud

Keeping this in one store is what lets you install Blowhorn on any number of Macs, your own or your teammates', and run them as one. Every Mac works from the same queue, and the Macs coordinate through it, so the same post isn't sent from two of them. Your analytics cover every Mac. Your content still goes out as long as one of those Macs is awake. The store holds:

- The content queue, schedule, profiles, run history and analytics. Every row is scoped to your organization's id.
- Platform credentials, in the credentials table of your Layer5 Cloud organization: GitHub tokens, Hacker News passwords, and Slack tokens and workspace sessions. For profiles set up before October 2026, it also holds the LinkedIn, X, Reddit and Bluesky passwords copied in when those profiles moved to the store. Blowhorn reads these credentials when it checks which profile may act on which platform. GitHub, Hacker News and Slack runs sign in with the stored value; for Slack that is the workspace session captured from your Chrome, or a Slack app token you enter. LinkedIn, X, Reddit and Bluesky runs sign in with the copy in the local `config.yaml` above.
- Which Chrome profile each Blowhorn profile uses on each Mac: the Mac's name, the Chrome profile's folder and display name, and the Google account signed in to that Chrome profile.
- Layer5 Cloud's handling of that data is governed by the [Layer5 privacy policy](https://layer5.io/company/legal/privacy/).

### What the app sends

- Posts, comments, reactions and invitations to the platforms a profile is configured for, when an approved row is due or when you run a command. Nothing is published from a dry run.
- A version check that lists the releases on Layer5's Blowhorn release channel, hosted on GitHub. The check needs GitHub credentials: when a GitHub token is already on your Mac (`GH_TOKEN`, `GITHUB_TOKEN` or `gh auth token`), the app sends it with that request, and updating downloads the disk image published with the newest release, installs the Blowhorn app from it into `/Applications` and relaunches. Without a token, the update button opens that release page in your browser and the app downloads nothing itself.
- A request to Layer5 Cloud for your organization's plan features, sent with your Layer5 Cloud token and your organization's id. The app caches the answer in your Keychain.
- No usage analytics and no crash reports. The app carries no analytics or crash-reporting library.

## Questions

Open an issue on the [site repository](https://github.com/layer5io/blowhorn-site/issues) for anything about this page, or contact Layer5 through the channels on its [privacy policy](https://layer5.io/company/legal/privacy/).
