---
title: "Keep posting when the app is closed"
description: "Run scheduled passes from the background service, and quit cleanly."
weight: 153
---


Scheduled passes keep running with no window open. One background service owns
the timer and runs a pass every ten minutes, starting with one as soon as it
starts.

## Check the service

```bash
blowhorn service status
blowhorn service tick-now --follow
```

`service status` names the owner, whether the service is running, the last
pass and the pass in flight. `tick-now` asks the running service for a pass
now and watches it. In the app, the "this computer" screen shows the same state.

When this install is signed in to a Blowhorn account, one tick runs at a time. A
second `blowhorn schedule tick` or `blowhorn schedule trigger-now` while that
tick is running stops, and Blowhorn says it is already running a tick on this
install.

The owner tells you who manages it: the desktop app registered it itself, or
the command line installed it from a file. When the app owns it, the app's
setting "keep this computer on watch after quit" (on by default)
decides whether quitting stops it. Quitting with a pass in flight asks what to
do: finish, cancel at a safe point, or stay.

## Install it without the app

On a computer without the desktop app:

```bash
blowhorn service install
```

`service test` validates the schedule and previews a pass the way the service
would run it. `service stop` drains the pass in flight before it stops; the
definition stays, and `service start` loads it again. `service update` brings
a file-installed definition up to date with the checkout, and only reloads
when it differs.

Every verb takes `--dry-run` to print what it would do, and `--json` for the
shape the app reads.

## Cancel a pass in flight

```bash
blowhorn service cancel
```

Cancelling stops at the next safe point, never mid-post: the row the pass was
on returns to the queue exactly as claimed, with no retry counted, and the
next pass takes it up again. The run ledger records the pass as cancelled,
never failed.

## Related

- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - create the rows the passes run
- [Pause and resume posting](/docs/how-to/schedule/pause/) - hold claims without stopping the service
- [Find out why a job did not run](/docs/how-to/schedule/why-not-run/) - read one row's state
- [Uninstall Blowhorn](/docs/how-to/manage/uninstall/) - remove the service for good
- [You're in control](/docs/explanation/youre-in-control/) - what an unattended run will and won't do
