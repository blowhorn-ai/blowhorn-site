---
title: "Chrome extension permissions"
description: "Each permission the Blowhorn extension asks for, the sites it runs on, and why."
weight: 220
---

# Chrome extension permissions

What the Blowhorn extension may do, and why each capability exists.
The extension acts only on requests from the Blowhorn app on your Mac;
it makes no requests of its own to any server, sells no data, and
injects no ads. Its single purpose is carrying out the posting,
amplifying, and session-check actions you queue, inside the Chrome
profile you already use. It adds no toolbar button by design: it is a
companion, not a tool you click.

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
| `nativeMessaging` | Talks to the Blowhorn app on this Mac. Every action is a request from that app |
| `alarms` | A one-minute alarm re-opens the connection to the app after Chrome suspends the worker, so a scheduled run finds the extension ready |
| `tabs` | Finds the tab already open on a supported site, or opens one, so the action runs where you are signed in. Only the sites above are queried |
| `cookies` | Reads cookies on the supported sites only when the app asks, to reuse a sign-in you already have. A cookie goes to the local app; the one the app keeps beyond your Mac is your Slack workspace session, kept in your account as that profile's Slack credential |
| `debugger` | Delivers your queued clicks and keystrokes as real input, watches the page's own requests to tell when an action finished, and takes a screenshot when an action needs a person to check it. Attached only to a tab the app is driving, released when the action ends |
| `downloads` | Catches the one export you asked for (an analytics or connections export) for the app, then cancels and clears it. A finished file stays where it is; the extension never starts a download on its own |

## Related

- [Chrome reference](/docs/reference/chrome/) - install, status, and connection checks.
- [Platforms](/docs/reference/platforms/) - the sites above, per platform.
- [Where your data lives](/docs/explanation/your-data/) - what the extension reads and where it goes.
- [Install the Chrome extension](/docs/how-to/set-up/install-the-chrome-extension/) - install it.
