---
title: "Install the app"
description: "Download the signed Mac app from blowhorn.ai and verify it."
weight: 30
aliases: [/docs/how-to/install-the-app/]
---


Download the signed Blowhorn app for macOS, verify it, install it, and open
it.

The app carries its own engine and Python, so you need no copy of the
Blowhorn repository, no git and no Python on your Mac.

## Download

Download the latest build from
[blowhorn.ai/download](https://blowhorn.ai/download/): it hands you the
current release's files from the
[blowhorn-site releases](https://github.com/layer5io/blowhorn-site/releases).

- `Blowhorn-mac.dmg` - the latest build, for Apple silicon and Intel Macs.
- `SHA256SUMS.txt` - the checksums for that release.

Verify the download before you open it. With both files in the same folder:

```bash
shasum -a 256 -c SHA256SUMS.txt --ignore-missing
```

The line for `Blowhorn-mac.dmg` must read `OK`.

## Install

1. Open the downloaded `.dmg`.
2. Drag the app onto **Applications** in the same window. Major Blowhorn
   points at it.
3. Open it from Applications. A notarized build opens without a warning.
   Don't run it from the disk image: a copy run from the
   disk image disappears when you eject it, so the app does not use its
   engine there and asks you to move it to Applications.

You need macOS 13 or newer and Google Chrome. Chrome is not bundled: Blowhorn
drives the Chrome profiles you already sign in to, through its Chrome
extension, which you add to each Chrome profile you post from
([Install the Chrome extension](/docs/how-to/set-up/install-the-chrome-extension/)).

## First run

The app opens on its Setup screen until its engine is ready; after that the
guided setup takes over (see below). Setup checks, in order, the engine
(bundled in the app), its helper tools, the connection to your organization's
data, your Chrome profile mappings
([Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/)), and
the background service. Each row says what it found, or what to do next.
Every row is described under Setup in
[The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/#setup).

**The installed app runs only the engine it carries.** It does not look for
a checkout of the Blowhorn repository, at `~/code/blowhorn` or anywhere else,
so a checkout you already have keeps its own profiles and settings and the
app does not read them. If the engine in the app cannot start, Setup says so
in one line; [Fix an engine that won't start](/docs/how-to/troubleshoot/engine-wont-start/)
walks through it.

Connecting the Blowhorn Chrome extension to this machine takes no pop-up:

- **Connect it today:** the guided setup's **Getting ready** step connects
  it. The extension can then reach the
  app from every Chrome profile. Chrome is not opened and no Chrome setting
  changes.
- **Launching the app changes nothing:** it only looks. Nothing is written
  until you connect.
- **Safe to repeat:** if it's already connected, nothing is written again.
- **Guided setup:** the first time you open the app, the guided setup walks
  you through signing in, Getting ready and the rest, one step at a time.

See [Set up Blowhorn the first time](/docs/how-to/set-up/first-run-setup/).

Then check sessions and run a dry-run post. Nothing is published until you
post without `--dry-run`.

Your settings and data stay in `~/Library/Application Support/Blowhorn/home`,
outside the app, so replacing or updating the app keeps them.

## Update

Updates come from the same releases page, and you need no GitHub account
for them. The app checks for a newer release every four hours (or when you
press **check now**), and once more each time you open it. When an installed
Blowhorn opens and that check finds a newer release it can install, a
prompt in the console window asks before anything is downloaded. **Download** downloads, verifies,
installs and reopens the app; if the install fails, a dialog says so and
your current version is put back. **Later** installs nothing and skips that
version, so the next release asks again; **Update** in the app still offers
it meanwhile. The **?** icon next to the title explains how the update
installs.

**Update** in the app and **Download** on that dialog take the same path.
They download the newer `.dmg` and check it twice before touching your
installed app. The release's `SHA256SUMS.txt`
catches a corrupted download, and a download that does not match is
discarded. That file comes from the same release as the `.dmg`, so it cannot
tell you who built it. What proves that is the code signature: the new app
must be signed with the same Apple Developer ID team as the app you are
running, macOS Gatekeeper must accept it, and the app must be the version
the release names and newer than yours. Only then does Blowhorn install
it and relaunch. A copy of Blowhorn that is not signed with a Developer ID
cannot make that comparison, so it installs nothing and opens the release
page instead. When the app cannot install the update itself, it opens the
release page and you download the newer `.dmg`,
verify it as in [Download](#download), and drag the app over the old copy.
The background service and your settings are kept. The engine is part of
the app, so updating the app updates the engine too.

[Update Blowhorn](/docs/how-to/manage/update-blowhorn/) shows each step the update
takes and what to do if it stalls.

## Related

- [What runs when the app is closed](/docs/explanation/distribution/) - the
  background service, quitting, and updates.
- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) -
  every screen, including Setup.
- [Install the Chrome extension](/docs/how-to/set-up/install-the-chrome-extension/) - the
  extension each mapped Chrome profile needs.
- [Uninstall Blowhorn](/docs/how-to/manage/uninstall/) - remove it cleanly
