---
title: "Chrome reference"
description: "The mapping commands, the two launch modes, the extension default, and Linux differences."
weight: 224
---


How Blowhorn finds and reaches your Google Chrome. Every browser run
reads the profile mapping first and refuses a profile without one,
before anything opens. This page describes; the steps live in the
how-to guides under Related.

## What it reads, and what it never reads

`blowhorn chrome` reads two files under Chrome's data directory,
`Local State` and `DevToolsActivePort`, and nothing else: never
cookies, saved passwords, storage, or the keychain. It writes nothing
there and opens no browser, DevTools, or network connection. Whether
Chrome is running is one bounded process lookup. There are two
exceptions. `blowhorn chrome extension-status` also reads each Chrome
profile's `Secure Preferences` and `Preferences` for the extension's
entry alone (see [its section](#blowhorn-chrome-extension-status)).
`blowhorn chrome map` also asks Chrome to open a window on the
extension's pairing page in the mapped Chrome profile, and creates this
machine's pairing key outside Chrome's directory (see [Pairing](#pairing)).

The extension's native host reads one more thing, only to answer the
toolbar popup: it looks for the extension's own random identifier in
the extension's own IndexedDB files,
`<profile>/IndexedDB/chrome-extension_<extension id>_0.indexeddb.leveldb/`
under the data directory of the Chrome that started it (its
`--user-data-dir`, else Chrome's default), to learn which Chrome profile
is asking. It
reads no other extension's files and nothing else in the profile, and
writes nothing there.

## The mapping

Each Blowhorn profile maps to one real Chrome profile on this machine,
kept in your account and keyed by hostname. The mapping does not follow
you to another machine.

`blowhorn chrome profiles` lists every profile Chrome knows, with the
directory name and the display identity. Chrome does not have to be
running. `blowhorn chrome suggest` prints a proposed mapping for every
Blowhorn profile your account knows. `blowhorn chrome map <profile>
<directory>` writes one mapping; it checks the directory exists in
Chrome and refuses a name Chrome no longer has. `blowhorn chrome unmap
<profile>` removes one mapping. A mapping is identity, never
permission: it says where the run acts, not what it may do, and there
is never a fallback to another profile.

### Pairing

The Chrome extension drives whichever Chrome profile it is installed in, so a
mapping alone cannot stop a run from acting in the wrong one. `blowhorn chrome
map` therefore also pairs the profile: it opens the extension's pairing page in
the mapped Chrome profile, and the page keeps a token tied to this machine, the
Blowhorn profile and the Chrome directory. The token is derived from a random
key Blowhorn keeps on this machine (`chrome_pairing.key`, readable only by you);
it carries no account data. The extension keeps it in its own storage (the
`storage` permission, which shows no install warning) and reports it when a run
connects.

Before any action, a run checks the token. It refuses with one sentence when
the Chrome profile is not paired, is paired to another Blowhorn profile (the
sentence names both and the Chrome directory to switch to), or is paired to a
mapping this machine no longer has. To pair, or to pair again after the
extension was reinstalled, map the profile to the directory it already has:

```bash
blowhorn chrome map ada 'Profile 2'
```

On the desktop app, the Chrome card on a profile has a pair again button that
does the same. An extension older than pairing cannot report a token; the run
says so once on stderr and goes ahead. The check starts once Chrome updates the
extension to a version that pairs and you re-run `blowhorn chrome map` for each
profile.

## Launch modes

How the run reaches Chrome once the mapping holds:

- The extension default: the run drives your signed-in Chrome through
  the Blowhorn extension. No second browser, no Allow dialog in the
  happy path.
- Attach (`cdp`): the run attaches to the Chrome you have open over the
  debugging protocol. Needs a window open and the Allow dialog
  approved; a scheduled pass gets a short Allow window.
- Launch (`persistent`): the run launches Blowhorn's own Chrome from
  the automation directory, minimized in the background.

Chrome is never launched headless and never replaced with bundled
Chromium: a headless run would announce itself to every site.

### The extension default

The extension driver starts no Chrome and launches no Playwright. One
mapped profile holds the bridge per run; a second run that wants it
while it is held stops with `another blowhorn run holds the Chrome
extension bridge` and does nothing. A hello that omits the run's
version, or an installed extension older than the run needs, stops as
`extension_outdated` naming both versions. Anything the extension
cannot do is refused by name.

Under the extension default, `blowhorn profile auth` is a sign-in by
hand: it opens the platform's sign-in page once in your mapped Chrome
profile, types nothing, and waits a bounded time for you to finish
signing in, then confirms the session once.

## `blowhorn chrome status`

Whether Google Chrome is installed, whether it is running, and whether
its debugging switch is on. On macOS the installed path is
`/Applications/Google Chrome.app`; on Linux the `PATH` names and
`/opt/google/chrome/chrome`. A missing Chrome stops the run with
`ChromeNotInstalled` before any driver starts.

## Flags

`--profile` and `--chrome-profile` pin one Chrome profile for one run.
`--chrome-launch` pins the launch mode for one run. `--pace`,
`--headless`, and `--dry-run` behave as they do everywhere.

## Linux

The `extension` and `persistent` drivers run on Linux as on macOS; the
`cdp` attach driver is macOS only. Chrome is found by its `PATH` names
and `/opt/google/chrome/chrome`. Everything else on this page reads
the same.

## A dedicated attach Chrome (no Allow dialog)

`blowhorn chrome attach-chrome` starts a second Chrome on a tree of
its own (`~/.blowhorn/attach-chrome`), open to remote debugging, so
`--chrome-launch cdp` can attach unattended with no Allow dialog.
Chrome 136 and later ignore the debugging switch on the default data
directory, which is why this is never your daily Chrome.

The port is bound to `127.0.0.1` and has no password: any program
running as you on this Mac can drive that Chrome and read its
cookies. Sign it in only to the accounts Blowhorn posts from.

A debugging port alone makes Chrome report `navigator.webdriver` as
`true` to every page, so `start` also passes
`--disable-blink-features=AutomationControlled`, which keeps it
`false`, as launch mode does by dropping `--enable-automation`.

| action | what it does |
| --- | --- |
| `status` (default) | reads the tree's `Local State`, `DevToolsActivePort` and `SingletonLock`; opens nothing |
| `signin` | opens the tree with no debugging switch, for the one-time sign-in; quit it after |
| `start` | launches Chrome detached with `--remote-debugging-port=0 --remote-debugging-address=127.0.0.1 --disable-blink-features=AutomationControlled`, then prints the setup steps |
| `stop` | DevTools `Browser.close`, waits, then `SIGTERM`; signals only the tree's own Chrome, never `SIGKILL` |
| `install-agent` | writes and loads `~/Library/LaunchAgents/ai.blowhorn.attach-chrome.plist`, which runs `start` at each login and logs to `data/logs/attach-chrome-agent.*.log` (or `--log-dir`) |
| `uninstall-agent` | unloads and removes that LaunchAgent; Chrome keeps running |

Off macOS every action but `status` is refused by name, and nothing is
started, signalled or written.

It writes no configuration: pointing `chrome.data_dir` at the tree,
and `chrome.launch_mode` at `cdp` for scheduled jobs, stay your
explicit steps. A recorded port counts only while a live Chrome holds
the tree, and it is evidence, not proof. Before a `cdp` run attaches
to this tree, it checks with `lsof` that the recorded port is
listened on by the pid holding the tree, on loopback only, and
refuses otherwise. `--json` on `status` adds `holder_pid`,
`stale_port` and `held_without_debugging`.

## `blowhorn chrome extension-install`

Writes the native-messaging host file Chrome launches to reach the
local Blowhorn app. Re-run it after moving the checkout or
reinstalling the app; without a current host file the extension cannot
talk to the engine.

## What a site sees: the user agent by driver

Your own user agent, on every driver. The extension and attach drivers
run inside your installed Chrome, so sites see the same agent string
your ordinary browsing sends. The launch driver starts that same
installed Chrome, never bundled Chromium, which would announce itself
as HeadlessChrome. A `--headless` request becomes the minimized
background window for exactly this reason: headless Chrome sends
`HeadlessChrome` in every request while its hints still claim Google
Chrome.

The launched window emulates nothing: the page reads the real screen, the real GPU and
your own permission state. A viewport override, a GPU switch or a blanket permission grant
each gave a reading no real Chrome gives, so the launch passes none of them (measured
2026-10-15).

## Extension mode: classic or background

With the extension driver, a run uses one of two behaviors:

| | classic | background |
| --- | --- | --- |
| Blowhorn's tab | opens inactive at the end of the window | opens inactive, grouped beside the tab you are on |
| focus emulation | from the first action that takes the debugger | from the first page load |
| Chrome's debugging bar | while an action holds the debugger, gone after a short idle period | for the whole run, from before the site loads |
| visible screenshot | switches to Blowhorn's tab for the capture | captured through the debugger, no tab switch |
| input | synthetic unless `BLOWHORN_EXTENSION_INPUT=trusted` | trusted unless `BLOWHORN_EXTENSION_INPUT=synthetic` |
| bringing the tab forward | before an automated login, and for a screenshot | only when you are needed (a code, a challenge, a sign-in you finish yourself) |

background is the default. classic is what the Chrome Web Store build 1.12.10
has always done, and `BLOWHORN_EXTENSION_ROLLBACK=classic` forces it on a
machine.
Where the mode comes from, top wins:

| layer | spelling |
| --- | --- |
| this machine | `BLOWHORN_EXTENSION_ROLLBACK=classic` forces classic |
| one scheduled job | its `Driver Mode`: `extension-classic` or `extension-background` |
| your account | the extension mode on Settings, Chrome extension (saved as `extensionMode` in your Layer5 Cloud preferences, so it follows you to every machine) |
| nothing set | background |

`BLOWHORN_EXTENSION_ROLLBACK=1` still swaps the driver for Blowhorn's own
Chrome as before; it says nothing about the mode. `0`, `false` and `off` read
as unset; any other value is refused before the run starts. On Settings the
selector is your account setting; the description under it is the mode this
machine runs, and the card says when the variable overrides the account or
holds a refused value. The features a
mode sets are `placement`, `first_page`, `lease_at_goto`, `quiet_screenshot`,
`checkpoint_front` and `trusted_input`. `first_page` is background only: a new
Blowhorn tab first loads a blank page that belongs to the extension, then the
site, so the site is the tab's second page. A site loaded as a tab's first page
reads its window size as zero while it loads; as the second page it often reads
the real size, but not always (about half the time when measured on
2026-10-17). An extension too old for a background feature runs that feature
the classic way, and the run says so once on stderr and carries on, so the
store build 1.12.10 keeps working in background mode. A run whose mode is not
the default names it once on stderr: `extension mode: classic, from the
account setting`.

In background mode Chrome's "started debugging this browser" bar stays up for
the whole run, and it goes away when the run ends. Closing it, opening
developer tools on Blowhorn's tab, or closing that tab takes the debugger away:
for the rest of that run every click, key press or quiet screenshot that needs
it fails as `input_revoked`, and the error names which of the three happened.
Run it again and leave the tab and the bar alone.

## `blowhorn chrome extension-mode`

```bash
blowhorn chrome extension-mode              # the mode a run would use, and why
blowhorn chrome extension-mode classic      # save classic to your account
blowhorn chrome extension-mode default      # clear it, so runs use background
```

With no mode it reads your account setting from Layer5 Cloud and writes
nothing; when Cloud cannot be read it says why (`account_error`) and shows
the cached setting a run would fall back to. With one it saves `extensionMode` to Layer5 Cloud; sign in
first with `blowhorn auth login`. `--json` prints one object: `mode`,
`source` (`rollback`, `account` or `default`), `account`, `account_error`,
`rollback`, `rollback_error`, `features` and `written`.

## `blowhorn chrome extension-status`

Whether the extension is installed, which version answers, and whether
it says connected. A version older than the run needs is the
`extension_outdated` refusal above.

It also reads each Chrome profile's `Secure Preferences`, then
`Preferences`, under the Chrome data directory for the extension's entry,
and lists every profile whose entry came from the Chrome Web Store
(`from_webstore`, or location `INTERNAL`) with its version, as
`webstore_profiles` in `--json`. A loaded-unpacked entry is not listed.
For a store install the report never says Load unpacked: a version too
old for this Blowhorn is told to update in `chrome://extensions`, and a
missing native host is told to run `blowhorn chrome extension-install`.
It writes nothing in that directory.

## One run per profile and platform

A profile's session on a browser platform (LinkedIn, X, Reddit, Hacker
News) belongs to one Blowhorn process at a time on a machine. Before a run
opens the session it takes a lock keyed by profile and platform, under
every launch mode. A second run that wants the same profile on the same
platform is refused with "profile `<name>` on `<platform>` is in use by
another blowhorn process; wait for it to finish or stop it": that profile
is skipped, its rows stay queued, and a scheduled job leaves it for the
next pass. Different profiles, or different platforms of one profile,
can run side by side. See [You're in control](/docs/explanation/youre-in-control/).

## Related

- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Install the Chrome extension](/docs/how-to/set-up/install-the-chrome-extension/) - install it.

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - write the mapping.
- [Choose how Blowhorn reaches Chrome](/docs/how-to/settings/launch-mode/) - when to leave the default.
- [Chrome extension permissions](/docs/reference/extension-permissions/) - what the extension may do.
- [Messages and exit codes](/docs/reference/messages/) - every refusal sentence.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - why your Chrome and not a bundled one.
