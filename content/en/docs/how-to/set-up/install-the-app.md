---
title: "Install the app"
description: "Download the signed Mac app from blowhorn.ai and verify it."
weight: 30
aliases: [/docs/how-to/install-the-app/]
---

# Install the app

Download the signed Blowhorn app for macOS, verify it, install it, and open
it.

**Early access:** the app does not bundle its command-line engine yet. On
first run it asks for a checkout of Blowhorn, which your Blowhorn
administrator gives you access to (see [First run](#first-run)).

## Download

Download the latest build from the
[blowhorn-site releases](https://github.com/layer5io/blowhorn-site/releases),
the same place the [blowhorn.ai/download](https://blowhorn.ai/download/) button links:

- [Blowhorn-mac.dmg](https://github.com/layer5io/blowhorn-site/releases/latest/download/Blowhorn-mac.dmg) -
  always the latest build, for Apple silicon and Intel Macs.
- [SHA256SUMS.txt](https://github.com/layer5io/blowhorn-site/releases/latest/download/SHA256SUMS.txt) -
  the checksums for that release.

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

You need macOS 13 or newer and Google Chrome. Chrome is not bundled: Blowhorn
drives the Chrome profiles you already sign in to, through its Chrome
extension, which you add to each Chrome profile you post from
([Install the Chrome extension](/docs/how-to/set-up/install-the-chrome-extension/)).

## First run

Until it finds the Blowhorn checkout and its Python environment, the app
opens on its Setup screen; after that the guided setup takes over (see
below). Setup checks, in order, the Blowhorn
checkout, its Python environment, the connection to your organization's
data, your Chrome profile mappings
([Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/)), and
the background service. Each row says what it found, or what to do next.
Every row is described under Setup in
[The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/#setup).

Connecting the Blowhorn Chrome extension to this machine takes no pop-up:

- **Connect it today:** the guided setup's **Getting ready** step connects
  it, or run `blowhorn setup` in Terminal. The extension can then reach the
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

**Early access:** signing in with your Blowhorn account and a bundled
engine that needs no checkout are still being built. When they ship, they
replace the checkout and Python rows.

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
The background service and your settings are kept.

## Related

- [What runs when the app is closed](/docs/explanation/distribution/) - the
  background service, quitting, and updates.
- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) -
  every screen, including Setup.
- [Install the Chrome extension](/docs/how-to/set-up/install-the-chrome-extension/) - the
  extension each mapped Chrome profile needs.
- [Uninstall Blowhorn](/docs/how-to/manage/uninstall/) - remove it cleanly
