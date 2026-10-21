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
Chrome is running is one bounded process lookup. There are four
exceptions. `blowhorn chrome extension-status` also reads each Chrome
profile's `Secure Preferences` and `Preferences` for the extension's
entry alone (see [its section](#blowhorn-chrome-extension-status)).
`blowhorn chrome discover` reads an allowlisted set of identity fields
for setup's confirm step (see [its section](#blowhorn-chrome-discover));
nothing outside that list, and never a saved password or a cookie's
value beyond the one named there.
`blowhorn chrome map` also asks Chrome to open a window on the
extension's pairing page in the mapped Chrome profile, and creates this
machine's pairing key outside Chrome's directory (see [Pairing](#pairing)).
`blowhorn chrome extension-enable` asks Chrome to open a window on the
extension's Chrome Web Store page in each Chrome profile you name (see
[its section](#blowhorn-chrome-extension-enable)). When no Chrome is
running, either one starts Chrome to open that window and leaves it
running; neither drives anything in it.

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

A debugging port, and Playwright's `--remote-debugging-pipe`, each make
Chrome report `navigator.webdriver` as `true`. `start` and launch mode
both pass `--disable-blink-features=AutomationControlled` and
`--test-type`, which keeps the flag `false` and leaves the
unsupported-flag infobar off.

| action | what it does |
| --- | --- |
| `status` (default) | reads the tree's `Local State`, `DevToolsActivePort` and `SingletonLock`; opens nothing |
| `signin` | opens the tree with no debugging switch, for the one-time sign-in; quit it after |
| `start` | launches Chrome detached with `--remote-debugging-port=0 --remote-debugging-address=127.0.0.1 --disable-blink-features=AutomationControlled --test-type`, then prints the setup steps |
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
| Blowhorn's tab | opens inactive beside the tab you are on, in a Blowhorn group that is collapsed by default | opens inactive beside the tab you are on, in a Blowhorn group that is collapsed by default |
| focus emulation | from the first action that takes the debugger | from the first page load |
| Chrome's debugging bar | while an action holds the debugger, gone after a short idle period | for the whole run, from before the site loads |
| visible screenshot | captured through the debugger, without selecting the tab | captured through the debugger, without selecting the tab |
| input | synthetic unless `BLOWHORN_EXTENSION_INPUT=trusted` | trusted unless `BLOWHORN_EXTENSION_INPUT=synthetic` |
| bringing the tab forward | never. When Blowhorn needs you it turns the Blowhorn group red and opens it, posts a notification when "notify when something needs you" is on in Settings, and waits for you to click the tab | the same |
| no Chrome window open | that profile stops and you are asked to open a Chrome window. Opening one itself would bring Chrome in front of what you are doing. A post moves on to the next profile; other commands end there, and nothing that did not happen is recorded | the same |

background is the default. classic keeps the input and debugger behavior of
the Chrome Web Store build 1.12.10 (synthetic input, the debugger only while
an action holds it) with the same tab placement as background, and
`BLOWHORN_EXTENSION_ROLLBACK=classic` forces it on a machine.
Where the mode comes from, top wins:

| layer | spelling |
| --- | --- |
| this machine | `BLOWHORN_EXTENSION_ROLLBACK=classic` forces classic |
| one scheduled job | its `Driver Mode`: `extension-classic` or `extension-background` |
| your account | the extension mode on Settings, Chrome extension (saved as `extensionMode` in your Blowhorn preferences, so it follows you to every machine) |
| nothing set | background |

How the Blowhorn tab group sits beside your tabs between steps is one more
account setting: collapsed (the default) or open, saved as `chromeGroup` in
the same Blowhorn preferences, so it follows you to every computer. Set it on
Settings, Chrome extension, or with `blowhorn chrome extension-mode --group
open` (`default` clears it). A run reads it once when it starts.

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

With no mode it reads your account setting from Blowhorn and writes
nothing; when it cannot be read it says why (`account_error`) and shows
the cached setting a run would fall back to. With one it saves `extensionMode` to Blowhorn; sign in
first with `blowhorn auth login`. `--dry-run`, with a mode or `--group`, reads that stored account,
reports it with the change on top, and writes nothing; when the account cannot be read it says why
and changes nothing. `--json` prints one object: `mode`,
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

`--json` also carries `profile_states`: one item per Chrome profile
directory (`Default` and `Profile N` with a `Preferences` file), each
`{profile, state, version}`, read from the same two files. `state` is:

- `enabled` - the extension is in that profile and turned on.
- `disabled` - it is in that profile and turned off. The external route
  always adds it this way until you turn it on there.
- `removed` - Chrome added it from the external-extensions file and you
  removed it. Chrome does not add it again by itself; the store page can.
- `absent` - nothing is recorded there yet: Chrome has not opened that
  profile since the file was written, or no install route is on.

## `blowhorn chrome extension-enable`

```bash
blowhorn chrome extension-enable --chrome-profile 'Profile 1'
blowhorn chrome extension-enable --chrome-profile Default --chrome-profile 'Profile 1' --json
```

Asks Chrome to open the extension's Chrome Web Store page in each
Chrome profile you name, so you can turn the extension on there with one
click: **Enable now** where Chrome already added it turned off, **Add to
Chrome** where Chrome has not picked it up yet. Name a profile with
`--chrome-profile`, the directory `blowhorn chrome profiles` prints, more
than once for several. Each directory must be in Chrome's `Local State`,
the one file it reads; a directory Chrome does not have, or a blank one,
is refused before anything opens. It writes nothing, and whether you then turned the extension on
is read by `blowhorn chrome extension-status` (`profile_states`), never
by this command. `--dry-run` opens nothing.

`--json` prints `ok`, `dry_run`, `url` (the store page) and `profiles`,
one `{directory, display_name, opened, detail}` per profile, where
`detail` says why the page did not open (`chrome could not open the Chrome Web Store page: <reason>`). When it opened in no
profile, `ok` is `false` and the command exits 1.

## `blowhorn chrome discover`

```bash
blowhorn chrome discover
blowhorn chrome discover --json
```

The survey behind setup's Confirm troops step: for every Chrome profile,
who it is and which platform accounts it holds, with nothing applied.
It reads only this allowlist, and nothing else in Chrome's directory:

- `Local State` and each profile's `Preferences`: the profile's
  directory, display name and Google account identity fields (`name`,
  `user_name`, `gaia_name`) - no other `account_info` field.
- Each profile's `Login Data` (read-only): the saved-login **username**
  for an allowlist of hosts only - LinkedIn, X, Reddit, Hacker News,
  GitHub, Bluesky and Slack. Never the password column, never form data.
- Each profile's `Cookies`: the **value** of GitHub's `dotcom_user`
  cookie alone (the signed-in GitHub account), and for LinkedIn, X,
  Hacker News and Slack only whether a session cookie is **present** -
  never its value, and never the encrypted value of anything.

No history, no LevelDB, no other profile file. A database Chrome has
locked or that does not parse reads as "not found", never as an error.

The text form prints one row per profile: its identity, its mapping, and
one line per platform (`username`, `signed in`, or `-`). With `--json`
each profile also carries `resolution` - how its Google email resolves
against your account's users, under the same rule as profile creation:
`one` (with the user, and their account's social links for display
only), `several` (with the candidates), `none` (with the refusal's
sentence) or `no-email` - plus `proposed_slug` and `slug_state` (`free`,
`own`, `taken`, `invalid`) for the profile a confirm would create.
Discovery writes nothing; the social links it shows are never treated
as permission to post.

## `blowhorn chrome confirm`

```bash
blowhorn chrome confirm --payload-stdin [--dry-run] --json < assignments.json
```

Applies a confirmed assignments document - what setup's Confirm troops
step sends. The document is read from stdin (`--payload-stdin` is
required), so a GitHub token or Bluesky app password inside it reaches
neither the command line nor the log:

```json
{"assignments": [{"directory": "Profile 2", "profile": "ada", "create": true,
  "platforms": {"linkedin": {"attach": true, "session": true},
                "github": {"attach": true, "token": "..."}}}]}
```

Per assignment, in order: resolve the target profile (the directory's
existing mapping, a named existing profile, or a create under the
profile-creation rule - the Google email must resolve to one user,
`email` in the document overrides it, `subject` settles the several
case, and no person is ever invented); write the attached platforms'
keys (usernames; `LI_CHROME_SESSION` / `HN_CHROME_SESSION` naming the
directory when `session` is set; `GH_TOKEN`; `BLUESKY_HANDLE` with
`BLUESKY_APP_PASSWORD`); then write the mapping with `chrome map`'s own
checks. Slack writes no key - its note says to capture the session with
`blowhorn profile auth --platform slack <profile>`. A username omitted
from the document is re-read from discovery.

Each assignment answers for itself in `results` (`written` names keys,
never values), so a partial confirm is a successful confirm: the exit
code is 0 when at least one assignment landed, 1 when none did, and 3
on a store outage. `--dry-run` runs every check and writes nothing. No
pairing page is opened; pairing happens on the first run or through
`blowhorn chrome map`.

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
