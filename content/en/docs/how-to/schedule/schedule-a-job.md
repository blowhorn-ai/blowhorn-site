---
title: "Schedule a job"
description: "Run posts and other commands on a schedule, from Activity › Routines or the command line."
weight: 150
aliases: [/docs/how-to/schedule-runs/]
---


Put a command on a schedule so it runs on its own, with or without the app open.

## From the app

Open **Activity** in the rail and switch to its **Routines** view. It opens on a week calendar; switch to "day",
"month" or "list" above it, and the screen remembers your choice. Clicking a
day in the month opens that day, and the day view becomes the one it
remembers.

To add a job, choose "schedule something", or click a free time in the day or week
calendar to start one at that time. Pick the command, the profiles and
platforms it runs for, and how often it repeats. The "browser driver" control
pins which Chrome route that job uses; leave it at the default unless one job
needs its own route.

To move a job, drag its next time to another time. Only the next one moves, and
only to a time still ahead; the dashed times after it follow on their own. From
the keyboard, open the job and choose "edit", then change "when".

A job that has finished (it ran once, or gave up after its retries) has no
next time. To run it again, open it, choose "edit" and give it a new "when":
it is scheduled again on the same row, with its full set of retries, and its
last run stays in its history.

If you have no routines yet, the screen offers "add sample routines…" instead: it
previews a starter set of rows first, and writes them only when you apply the
preview. It never edits routines you already set up.

Open a job (click it, or focus it and press Enter) to change it, or choose "do it now"
to run it without waiting for its time. With "preview only" on, it previews the pass and claims nothing.

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

To move a job, change its `Run At`. Its next run moves with it unless the same
payload sets `Next Run At` itself.

A row that has completed or given up has no next run in `schedule list`.
Giving it a new time - a `Run At` that changes, or a `Next Run At` - runs it
again: the same write sets its `Status` back to `scheduled` and its `Retry
Count` to 0, so it gets its full `Max Retries` again, and keeps its `Last Run
At`, `Last Error` and `Last Log Path`. Raising `Max Retries` alone does not run
it again, and a payload that sets `Status` itself decides the status instead.

```bash
blowhorn schedule upsert --row 4 --payload '{"Run At": "2026-10-20 09:00:00"}'
```

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
