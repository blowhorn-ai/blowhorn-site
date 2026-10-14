---
title: "Chrome reference"
description: "The mapping commands, the two launch modes, the extension default, and Linux differences."
weight: 224
---

# Chrome reference

How Blowhorn finds and reaches your Google Chrome. Every browser run
reads the profile mapping first and refuses a profile without one,
before anything opens. This page describes; the steps live in the
how-to guides under Related.

## What it reads, and what it never reads

`blowhorn chrome` reads two files under Chrome's data directory,
`Local State` and `DevToolsActivePort`, and nothing else: never
cookies, saved passwords, storage, or the keychain. It writes nothing
there and opens no browser, DevTools, or network connection. Whether
Chrome is running is one bounded process lookup. The one exception is
`blowhorn chrome extension-status`, which also reads each Chrome
profile's `Secure Preferences` and `Preferences` for the extension's
entry alone (see [its section](#blowhorn-chrome-extension-status)).

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
directory, which is why this is never your daily Chrome. `status`
reads that tree's two files and opens nothing; `start` launches Chrome
detached and prints the steps that finish the setup. It writes no
configuration: pointing `chrome.data_dir` at the tree stays your
explicit next step. A recorded port is evidence a Chrome is up, not
proof a connect would succeed.

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
News) belongs to one Blowhorn process at a time on a Mac. Before a run
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
