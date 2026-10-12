---
title: "The Blowhorn app, screen by screen"
description: "The menu-bar popover, the console screens, Setup, Settings, and what each one does."
weight: 211
---

# The Blowhorn app, screen by screen

What each part of the Blowhorn desktop app shows and does. This page
describes; the steps live in the how-to guides linked under Related.

## The menu bar and the popover

Blowhorn lives in the menu bar. Opening it shows the popover, which has
two boards. The running board shows the scheduler, what is due now, what
is running, what needs you, and the content queue with a countdown to
the next tick. The paused board shows PAUSED with each tick-level pause
scope stated once, and the rows that would post now wait instead of
posting. A store outage puts its line above the board.

The popover footer holds the pause controls and, when an update is
ready, the update card. The update installs and relaunches the app when
this machine can reach the release; otherwise it opens the release
page in your browser.

## The console

The console is the full window, reached from the popover. Its rail, in
order: "jobs", "content", "runs", "profiles", "analytics", "service",
"settings". Each screen reads live state on open. Nothing here edits on
a timer.

| Screen | Shows | Acts |
|---|---|---|
| jobs | Every schedule row, whether it is due, paused, or held; a job drawer with the row behind it; a bootstrap preview for a starter set | Create, edit, pause or resume one row; run one row now; apply the bootstrap set |
| content | The queue: pending rows, rows still owed to some profile, clicked-but-unread rows | Edit a row; clearing a clicked row's "Date Promoted" re-queues it |
| runs | Past runs with their ledger lines; per-job logs under the log directory | Re-run a failure from its row |
| profiles | Every profile, its Chrome mapping, its per-platform sessions | Add a profile; map or unmap its Chrome profile |
| analytics | Followers, growth, and operations per profile; collection freshness in the header | Collect now; open the HTML report |
| service | Who registered the background service, whether it runs, the last tick heartbeat | Install, start, stop, restart, update, or uninstall the service |
| settings | Engine defaults rendered from the CLI's own option list, the extension card, your account card | Change defaults, check the extension, test your account connection |

The analytics screen states how fresh its numbers are in the header and
has no refresh control of its own. The runs screen reaches per-job logs
through the log directory listing, which includes each capture file and
its rollover. The service screen is the visible face of
`blowhorn service`; every button there runs the matching command.

## Setup

Setup is the first-run checklist, five rows read from this machine:
"blowhorn checkout", "python environment", "store", "chrome profiles",
and "background service". Each row reports ok, warn, or off with the
one fix that clears it. The "map chrome profiles" panel and the
"background service" row act directly: mapping a profile and
registering the service happen here, not in a terminal.

## Settings

Settings edits the same `.blowhorn.yaml` defaults the CLI reads: pace,
excluded profiles, dry run, notifications, logs, and the Chrome launch
mode. The engine-defaults card renders from `blowhorn config show`,
so the app can never offer an option the engine does not know. The
extension card reports whether the extension is installed, which
version answers, and whether it says connected. Quitting the app leaves
posting to the background service and the keep-running setting; see
[What runs when the app is closed](/docs/explanation/distribution/).

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - the Setup panel behind the mapping.
- [Change your defaults](/docs/how-to/settings/defaults/) - pace, exclusions, logs.
- [Settings and configuration](/docs/reference/configuration/) - every option the app edits.
- [How Blowhorn works](/docs/explanation/how-it-works/) - app, engine, extension, and store.
- [You're in control](/docs/explanation/youre-in-control/) - the controls behind pause and Settings.
- [Install the app](/docs/how-to/set-up/install-the-app/) - get the app onto a Mac.
