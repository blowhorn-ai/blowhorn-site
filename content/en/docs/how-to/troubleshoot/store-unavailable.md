---
title: "Fix cannot reach your organization"
description: "What the account-down state means, and what to do until the customer account path ships."
weight: 195
draft: true
---

Every command that needs your account prints one sentence and exits 3 when your account is unreachable. A tick in that state claims nothing and runs nothing,
but still writes its heartbeat, so `blowhorn schedule status` keeps answering
with your account as the last tick saw it.

This page stays a draft until the customer account path ships: today the only
connection is the one your Blowhorn administrator sets up, so most of the
fixing below is theirs, not yours.

## What you can do

Probe the connection now. `schedule status` never probes, because the app
polls it every 15 seconds:

```bash
blowhorn store
blowhorn schedule status
```

If the tunnel or network dropped, bring it back the way your administrator set
it up, then run `blowhorn store` again until it answers. Ticks resume claiming
on their next pass; due times carried forward while your account was gone, so a
recurring row runs once, not once per missed interval.

## What the run did while your account was gone

Run records waited in the local spool and replay on the next tick or run that
reaches your account, which prints how many it replayed. Nothing is lost: the
ledger is local first and shared second.

Commands that never need your account kept running throughout.

## Related

- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - what a tick does when your account answers
- [Find out why a job did not run](/docs/how-to/schedule/why-not-run/) - read one row after the outage
- [Troubleshooting](/docs/how-to/troubleshoot/troubleshooting/) - start from a symptom instead
