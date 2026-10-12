---
title: "Getting started with the desktop app"
description: "Install the app, connect Chrome, and preview your first post without publishing."
weight: 20
draft: true
---

# Getting started with the desktop app

In this tutorial you will install the Blowhorn menu-bar console, point it at
your checkout, and use it to inspect a run - without letting it publish
anything. It takes about fifteen minutes.

You need macOS 13 or newer, a browser signed in to GitHub, and a checkout of
this repository with the CLI already installed
([Getting started with the CLI](/docs/tutorials/getting-started/)).

## 1. Install the app {#section-1-install-the-app}

The app ships as one universal DMG that runs on Apple silicon and Intel Macs.

1. Open the [download section at blowhorn.ai](https://blowhorn.ai/#download)
   in your browser.
2. Download `Blowhorn-mac.dmg`, the newest release.
3. Open the DMG and drag `Blowhorn.app` to `/Applications`.
4. In Terminal, run:

   ```sh
   xattr -cr /Applications/Blowhorn.app
   ```

Step 4 is not optional. Do it before you first open the app, and the app will
open normally.

## 2. Open it and meet the Setup screen {#section-2-open-it-and-meet-the-setup-screen}

Launch `Blowhorn.app`. Because this is the first run, it opens on **Setup**: four
checks, each either `ok` or offering the action that fixes it.

Work down the rows:

1. **blowhorn checkout** - if it did not find your checkout, click **choose
   folder…** and select it.
2. **python environment** - this should already be `ok` from the CLI tutorial.
3. **store** - the connection to your account. If it is not configured yet, click
   its **import** action and follow
   Connect to the store.
4. **background service** - nothing to do here: once the rows above are ok
   the app registers the service itself, and this row only reports it. You do
   not need it to finish this tutorial.

Each probe is bounded by a 20-second timeout (60 s for the store's full **test
connection**), so a row that cannot answer will tell you rather than hang.

## 3. Turn on dry-run before anything else {#section-3-turn-on-dry-run-before-anything-else}

Still on the Setup screen, find the **dry-run by default** switch below the
four rows and turn it **on**.

This is the important step of this tutorial. With it on, runs you start from
the app rehearse instead of publishing. Turn it off later, deliberately, when
you want the app to post for real.

Now click **open console**.

## 4. Look at the queue {#section-4-look-at-the-queue}

The console's Content screen reads the same content queue the CLI does - it
runs `blowhorn content list --json` once and its pending tab shows the rows that
are due, each with who would post it (the same selection
`blowhorn post --check-queue` prints).

Nothing here publishes on its own. The screen reads on no timer - it shows you
what it read when it read it.

## 5. Find the app in your menu bar {#section-5-find-the-app-in-your-menu-bar}

Close the console window. The app is still running: its icon sits in the menu
bar, and clicking it opens the popover with the service state, the next
scheduled tick, and the content about to post: **ready to post** lists the rows
some profile would post on its next run - its count is the `pending` beside
content in the console's rail - and **scheduled to post** lists what waits for
a later `Promote On`.

Installing the app is what installed the background service, and quitting the
app does **not** stop it - the switch **keep the background service running
after quit**, on by default, is the one thing that decides that. With it off,
quitting stops the service (asking you first if a pass is in flight), and the
next launch starts it again. See
[What runs when the app is closed](/docs/explanation/distribution/).

## What you did

You installed the console from its DMG, cleared the quarantine flag macOS puts
on it, pointed it at your checkout, made every run from the app a rehearsal by
default, and read the queue.

## Next

- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) -
  every screen you just used.
- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - when you want the
  scheduler the Setup screen offered.
- [What runs when the app is closed](/docs/explanation/distribution/) - the
  background service, quitting, and updates.
