---
title: "Job options and schedules"
description: "Schedule rows, recurrence words, driver mode, and the three pause scopes."
weight: 214
---

# Job options and schedules

What a schedule row holds, when it runs, and what keeps it from
running. This page describes; the steps live in the how-to guides
linked under Related.

A pass runs every ten minutes and claims the rows that are due. Several
machines sharing one store share the queue: a running row carries a lease,
and a row whose lease lapsed is reclaimable by the next pass.

## The row

| Field | Means |
|---|---|
| Command | What the pass runs: `post` and the other schedulable commands (`source` is not schedulable) |
| Platforms | Row filter, not a posting target: which rows the command reads |
| Profiles | Which profiles the run acts as |
| Recurrence | When the row comes due again |
| Driver mode | How the run reaches Chrome: `default`, `extension`, `cdp`, or `persistent` |
| Status | Where the row stands; `running` is a lease, never a lock |

`blowhorn schedule list` shows each row and whether it is due.
`blowhorn schedule get` returns one row with all fields.
`blowhorn schedule upsert` creates or updates a row from a JSON
payload (`--row` names the row; `--expected-fingerprint` rejects the
write when the row changed underneath you). `blowhorn schedule delete`
removes a row by number. `blowhorn schedule validate` checks every row
against the schema. `blowhorn schedule bootstrap` previews or writes a
starter set. `blowhorn schedule trigger-now` forces one row to run
immediately instead of waiting for the pass.

## Recurrence

| Word | Means |
|---|---|
| `once`, `none`, or blank | Runs one time, then never again |
| `hourly` | Every hour |
| `daily` | Every day |
| `weekly` | Every week |
| `monthly` | Every 30 days |
| `every:N` | Every N minutes |

Anything else is refused as an unsupported recurrence.

## Driver mode

`default` follows the same precedence every run follows: the
`--chrome-launch` flag, then the job's own mode, then the configured
default, which is the extension. Naming `extension`, `cdp`, or
`persistent` pins the job to that driver. A job pinned to a driver that
cannot do the work is refused by name before anything opens.

## Pause scopes

A row is claimed only when none of the three scopes says paused:

| Scope | Pauses | Lifted by |
|---|---|---|
| `machine` | This machine only, in `.blowhorn.pause.json` | `blowhorn schedule resume` on this machine |
| `all` | Every machine sharing your account | Resuming the organization-wide pause |
| `row` | One scheduled row, everywhere | Resuming that row |

`blowhorn schedule pause` pauses; `blowhorn schedule resume` resumes.
`blowhorn schedule status` shows whether processing is paused and the
last tick's heartbeat. `blowhorn schedule why <row>` explains why one
row has or has not run on this machine. Quitting the app pauses
nothing: the file, the organization-wide pause, and the row pauses keep
exactly what they said.

## Related

- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - create, pause, and resume jobs.
- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) - the "jobs" screen and the popover boards.
- [Settings and configuration](/docs/reference/configuration/) - the launch-mode default a job inherits.
- [How scheduling works](/docs/explanation/scheduling/) - passes, leases, and why a row waited.
- [CLI reference](/docs/reference/cli/) - the schedule commands.
