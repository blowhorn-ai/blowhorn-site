---
title: "Update Blowhorn"
description: "Install a newer Blowhorn from the app, follow each step as it runs, and what to do if an update stalls."
weight: 190
---

Blowhorn tells you when a newer version is out and installs it for you. You
need no GitHub account, and your settings, data and background service are
kept.

## Start an update

When a newer release is out, the menu-bar popup shows a card with the new
version and an **update** button. The Home screen and the Setup screen offer
the same update. Press **update** in any of them.

The app also checks each time you open it. If that check finds a newer
release, a prompt in the console window asks before anything is downloaded.

## What you see while it updates

The card names each step as it happens:

1. **downloading**, with a progress bar, the percent done, how many MB of the
   total have arrived, and about how long is left. The time left comes from
   how fast the download has been going over the last few seconds.
2. **verifying checksum and signature**. The download is compared with the
   release's `SHA256SUMS.txt` to catch a corrupted file, then the new app must
   be signed with the same Apple Developer ID team as the app you are running,
   and macOS Gatekeeper must accept it.
3. **installing**. The new app is copied into Applications and swapped in.
   If anything fails, your current version is put back.
4. **relaunching**. Blowhorn closes and the new version opens. If Blowhorn
   asks what to do about work in progress before it closes and you choose
   **stay open**, the new version stays installed and opens the next time you
   start Blowhorn, or when you press **update** again.

Verifying and installing have no bytes to count, so the bar sweeps and the
card says how long the step usually takes, for example "usually about 25
seconds". Blowhorn times these steps on your Mac each time it updates and
uses those timings next time. Until it has its own, it uses timings measured
on an Intel iMac: about 24 seconds to verify and 20 seconds to copy the app.

## If an update stalls

If the download stops moving for 30 seconds, or a step runs for well over
its usual time, the card says so and offers two buttons:

- **retry** stops the update and starts it again. Your current version stays
  installed until the new one has been verified. Once the new version is in
  Applications, retry only reopens it; nothing is downloaded again.
- **release page** opens the release on GitHub so you can update by hand.

The info button after the two buttons says how long nothing has moved.

If the new version is installed but Blowhorn could not reopen itself, the
card says so instead of opening the release page. Quit Blowhorn and open it
again to start the new version.

## Update by hand

On the release page, download `Blowhorn-<version>-mac-universal.dmg`, open
it, and drag Blowhorn to Applications, replacing the old copy. The update
in the app does exactly this for you, after checking the download. See
[Install the app](/docs/how-to/set-up/install-the-app/) for how to check a download
yourself.

## Related

- [Install the app](/docs/how-to/set-up/install-the-app/) - download, verify and open
  the signed Mac app.
- [Fix Blowhorn when its engine won't start](/docs/how-to/troubleshoot/engine-wont-start/)
- [Uninstall Blowhorn](/docs/how-to/manage/uninstall/)
