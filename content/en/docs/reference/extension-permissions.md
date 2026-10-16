---
title: "Chrome extension permissions"
description: "Each permission the Blowhorn extension asks for, the sites it runs on, and why."
weight: 220
---

# Chrome extension permissions

What the Blowhorn extension may do, and why each capability exists.
The extension acts only on requests from the Blowhorn app on your machine;
it makes no requests of its own to any server, sells no data, and
injects no ads. Its single purpose is carrying out the posting,
engagement, outreach, export and session-check actions you queue or
start in Blowhorn, inside the Chrome profile you already use. Its
toolbar button shows status only; every change happens in the Blowhorn
app.

## Sites

The extension runs content only on the sites Blowhorn acts on, and
reads a workspace session only from its sign-in pages:

- `x.com`, `twitter.com`
- `linkedin.com`, `www.linkedin.com`
- `reddit.com`, `www.reddit.com`
- `news.ycombinator.com`
- `mentorship.lfx.linuxfoundation.org`, `sso.linuxfoundation.org`
- `*.slack.com`

No other site is touched. You remain responsible for each destination's
terms and acceptable-use rules; Blowhorn gives you the controls, not
permission to ignore them.

## Permissions

| Permission | Why |
|---|---|
| `nativeMessaging` | Talks to the Blowhorn app on this machine. Every action is a request from that app |
| `alarms` | A one-minute alarm re-opens the connection to the app after Chrome suspends the worker, so a scheduled run finds the extension ready |
| `tabs` | Opens one background tab on a supported site, or reuses the one it opened earlier, so the action runs where you are signed in. It looks only among tabs on the sites above, only to find its own, and never navigates, drives or closes any other tab |
| `tabGroups` | Puts the tab it opened in a tab group named Blowhorn, right after the tab you were on, so you can see which tab the app is driving and get back to yours. The group is a label: it never moves, selects or closes your other tabs, and a Chrome that cannot group still gets the tab |
| `cookies` | Reads cookies on the supported sites only when the app asks, to reuse a sign-in you already have. A cookie goes to the local app; the one the app keeps beyond your machine is your Slack workspace session, kept in your account as that profile's Slack credential |
| `debugger` | Delivers some of your queued clicks and key presses as real input (the rest, and all typing, go through the extension's own script on the page), watches the page's own requests to tell when an action finished, and takes a screenshot when the app asks for one. Attached only to the tab the extension opened, released when the action ends or after a short idle period |
| `downloads` | Catches the one export you asked for (an analytics or connections export) for the app, then cancels and clears it. A finished file stays where it is; the extension never starts a download on its own |

## Related

- [Chrome reference](/docs/reference/chrome/) - install, status, and connection checks.
- [Platforms](/docs/reference/platforms/) - the sites above, per platform.
- [Where your data lives](/docs/explanation/your-data/) - what the extension reads and where it goes.
- [Install the Chrome extension](/docs/how-to/set-up/install-the-chrome-extension/) - install it.
