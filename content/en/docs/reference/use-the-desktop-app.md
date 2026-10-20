---
title: "The Blowhorn app, screen by screen"
description: "The menu-bar popover, the console screens, Setup, Settings, and what each one does."
weight: 211
---


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
ready, the update card. The update downloads the new version, checks it
against the release's checksums, confirms it is signed by the same Apple
Developer ID team as the running app and accepted by Gatekeeper, installs it
and relaunches the app; when it cannot, it opens the release page in your
browser. An installed Blowhorn that finds such a release when it opens also
asks in the console window, before the download, with **Download**, **Later**
and a **?** help icon;
what each does is under [Update](/docs/how-to/set-up/install-the-app/#update).

## The console

The console is the full window, reached from the popover. Its rail, in
order: "home", "activity", "history", "profiles", "performance", "this
computer", "settings". "activity" is one page with two views, switched at the
top of the screen: "queue" (what you want to say) and "schedule" (when and
where things go out). Under the items, "pause this computer" is one toggle:
press it to pause, press it again to turn the pause off. Each screen reads live state on open. Nothing here edits on
a timer. Until you're signed in and the extension is ready, every rail item
but "home" is locked; see
[Set up Blowhorn the first time](/docs/how-to/set-up/first-run-setup/).

| Screen | Shows | Acts |
|---|---|---|
| home | Whether Blowhorn is working, what runs next, and whether it needs you; a pause names which pause holds - this computer, all computers, or both | Turn off the pause it names (one button per pause while both hold); reconnect an account; finish setting up |
| activity › queue | Your posts with their status - "ready", "scheduled", "partly sent", "sent", "draft", "needs you" - and clicked-but-unread ones | Add or edit a post; clearing a clicked post's "Date Promoted" queues it again |
| activity › schedule | The schedule as a day, week or month calendar, or as a list: each item's next time, its last time, and the times that would follow, dashed because they are estimates; a "now" row for items going out or waiting for the next check; a drawer for one item; a preview of a sample schedule | Add an item, from "schedule something" or by clicking a free time; move an item's next time by dragging it; edit, pause or resume one item; "do it now"; add the sample schedule |
| history | Everything Blowhorn did, newest first, with each one's detailed log under the log directory's `scheduler/` folder | "try again" on a failure |
| profiles | Every profile, its Chrome mapping, its per-platform sessions | Add a profile; map or unmap its Chrome profile |
| performance | Followers, growth, and operations per profile; collection freshness in the header | Collect now; open the HTML report |
| this computer | Who registered the background service, whether it is on watch, the last check, the pause for all computers | "check now" (with "preview only" to see what would go out); the "pause all computers" toggle; open System Settings when the service is turned off there |
| settings | Engine defaults rendered from the CLI's own option list, the extension card, your account card | Change defaults, check the extension, choose its mode, test your account connection |

The schedule list layout keeps every value on one line. When the list is narrow -
the drawer is wide, or the window is small - the browser and recurrence
columns leave first (the drawer still shows both) and a long profile list
is shortened with an ellipsis; the status is never cut.

The schedule view opens on the week calendar and remembers the layout you
pick; opening a day from the month makes the day view the remembered one.
The tabs ("coming up", "due now", "going out", "failed", "all") and the
filter box choose which items it shows, in every layout. An item's next time
is a fact; the times after it are drawn dashed, because Blowhorn schedules
each one from when the last one finished, so they drift. An item that repeats
more often than every hour shows its next time only (the month shows daily
and slower). Moving one asks your account first and refuses if someone else
changed that item since you loaded it. A finished item (it happened once, or
gave up after its retries) shows its last time and no next one; giving it a
new "when" in its editor schedules it again, with its full set of retries.

The performance screen states how fresh its numbers are in the header and
has no refresh control of its own. Its operations heatmap has one row per
profile; attempts recorded for several profiles at once (`all`, or a comma
list) name no one profile, so they are counted beside it rather than shown
as a row. The history screen reaches each item's detailed log through the
log directory listing, which includes each capture file and its rollover.
The this computer screen is the visible face of `blowhorn service`: it reports the
service the app registered and never installs, updates or uninstalls one.

Profiles made before profile names were lowercase keep their capitalised
folder (`data/profiles/Lee`). The app lists them as they are spelled and
reads and saves them as the lowercase name every command resolves them to.

## Setup

Setup is the engine checklist the app opens on while its engine is not
ready (otherwise the first run is the guided setup; see
[Set up Blowhorn the first time](/docs/how-to/set-up/first-run-setup/)),
five rows read from this machine:
"Blowhorn folder", "helper tools", "organization connection", "chrome profiles",
and "this computer on watch". The first two check the engine bundled in the
app, the only engine the installed app runs
([Install the app](/docs/how-to/set-up/install-the-app/#first-run)); it
never needs a clone or an install, so those rows offer neither. An app run from its disk image says to move it to Applications
instead. Each row reports ok, warn, or off with the
one fix that clears it. The "map chrome profiles" panel and the
"this computer on watch" row act directly: mapping a profile and
registering the service happen here, not in a terminal.

## Settings

Settings edits the same `.blowhorn.yaml` defaults the CLI reads: pace,
excluded profiles, dry run, notifications, logs, and the Chrome launch
mode. The engine-defaults card renders from `blowhorn config show`,
so the app can never offer an option the engine does not know. The
extension card reports whether the extension is installed, which
version answers, and whether it says connected, and sets its
[extension mode](/docs/reference/chrome/#extension-mode-classic-or-background), classic or
background, on your Blowhorn account. **guided setup** at the
bottom reopens the first-run setup, and **run setup again** opens Setup.
Quitting the app leaves
posting to the background service and the keep-running setting; see
[What runs when the app is closed](/docs/explanation/distribution/).

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - the Setup panel behind the mapping.
- [Change your defaults](/docs/how-to/settings/defaults/) - pace, exclusions, logs.
- [Settings and configuration](/docs/reference/configuration/) - every option the app edits.
- [How Blowhorn works](/docs/explanation/how-it-works/) - app, engine, extension, and store.
- [You're in control](/docs/explanation/youre-in-control/) - the controls behind pause and Settings.
- [Install the app](/docs/how-to/set-up/install-the-app/) - get the app onto a Mac.
