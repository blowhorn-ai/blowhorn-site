---
title: "Fix the Chrome extension connection"
description: "Reconnect the extension, resolve version mismatch, and clear bridge and profile contention."
weight: 194
---


When a run says the extension is not connected, ask the extension itself
first. This command opens no tab and contacts no platform:

```bash
blowhorn chrome extension-status
```

It reports whether the extension directory is installed, whether the native
host manifest is missing, current or stale against the checkout, which install
route is on disk (policy, external, or none), and whether the extension
answers hello on its socket. An answered hello proves the extension is loaded
in the real Chrome and talking.

## Not connected

Work through the report top to bottom: a missing directory or manifest means
the install did not finish, so install it again with your administrator. A
stale manifest means the checkout moved on without it: reinstall the native
host from the current checkout, then reload the extension on
`chrome://extensions`.

## Version mismatch after an update

A Blowhorn upgrade does not reinstall the extension. After an update, take the
[store update](/docs/how-to/set-up/install-the-chrome-extension/#from-the-chrome-web-store)
(never load it unpacked over a store install), or reload the unpacked copy on
`chrome://extensions`, then run
`blowhorn chrome extension-status` again until hello answers.

## Bridge busy

```text
another blowhorn run holds the Chrome extension bridge (pid 1234)
```

One mapped profile runs in one process at a time. Another run is acting as
that profile: wait for it, or stop it -- the message names its pid. Your activities stay queued, and a scheduled
job tries again next tick. A run that has hung stops sending its
heartbeat, and after 30 seconds without one the bridge is released on
its own, so a wedged run cannot hold the bridge indefinitely.

## Profile in use

When a run says the profile is in use by another Blowhorn process, the same
rule holds under any driver: wait for that run, or stop it. The profile is
skipped and its activities stay queued.

## Related

- [Choose how Blowhorn reaches Chrome](/docs/how-to/settings/launch-mode/) - run under another mode instead
- [Troubleshooting](/docs/how-to/troubleshoot/troubleshooting/) - start from a symptom instead
- [Keep posting when the app is closed](/docs/how-to/schedule/background-service/) - stop a pass cleanly before retrying
