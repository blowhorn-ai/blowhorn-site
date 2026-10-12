---
title: "Schedule a job"
description: "Run posts and other commands on a schedule, from the Jobs screen or the command line."
weight: 150
aliases: [/docs/how-to/schedule-runs/]
---

# Schedule a job

Put a command on a schedule so it runs on its own, with or without the app open.

## From the app

Open the "jobs" screen and choose "new job". Pick the command, the profiles and
platforms it runs for, and how often it repeats. The "browser driver" control
pins which Chrome route that job uses; leave it at the default unless one job
needs its own route.

If the schedule is empty, the screen offers "bootstrap schedule" instead: it
previews a starter set of rows first, and writes them only when you apply the
preview. It never edits a schedule that already holds rows.

Open a row to change it, or run it now without waiting for its time. A dry run
previews the pass and claims nothing.

## From the command line

List what is scheduled and whether each row is due:

```bash
blowhorn schedule list
blowhorn schedule list --due-only
```

Check every row against the supported schema before it costs you a pass:

```bash
blowhorn schedule validate
```

Seed an empty schedule with the starter set. It refuses a schedule that already
holds rows unless you pass `--replace`, which deletes them all first:

```bash
blowhorn schedule bootstrap --dry-run
blowhorn schedule bootstrap
```

Run one pass by hand, or force one row now:

```bash
blowhorn schedule tick --profile all
blowhorn schedule trigger-now 4
```

Read or write a single row. Row numbers are stable: they are assigned when a
row is created and never reused, so a number you noted keeps meaning the same
row:

```bash
blowhorn schedule get 4
blowhorn schedule upsert --payload '{"Command": "post", "Profile": "all", "Recurrence": "daily"}'
blowhorn schedule delete 4
```

`upsert` and `delete` accept the fingerprint `schedule get` returns, and refuse
a stale edit rather than writing over someone else's change.

## What a job can run

A job runs one Blowhorn command with its own profiles, platforms and
parameters. `post`, `comment`, `follow`, `accept`, `withdraw`, `analytics`
and `report` are schedulable. `find` is not:
it prints search results and changes nothing.

`Recurrence` takes `once`, `hourly`, `daily`, `weekly`, `monthly`, or
`every:<minutes>` for a minute count. A job whose profile is `all` runs for
every profile except the excluded ones; name a profile in the row to include an
excluded one for that job only.

Each pass writes a per-job log under `<log-dir>/scheduler/`, records its
heartbeat so `blowhorn schedule status` can report it, and appends one line per
pass to the run ledger. When the pass cannot reach your account it claims nothing,
exits 3, and says so in one line.

## Related

- [Pause and resume posting](/docs/how-to/schedule/pause/) - stop every claim without stopping the service
- [Find out why a job did not run](/docs/how-to/schedule/why-not-run/) - read one row's state in one command
- [Keep posting when the app is closed](/docs/how-to/schedule/background-service/) - the background service that runs the passes
- [Change your defaults](/docs/how-to/settings/defaults/) - pace, excluded profiles, logs
- [You're in control](/docs/explanation/youre-in-control/) - the limits every scheduled job runs under
