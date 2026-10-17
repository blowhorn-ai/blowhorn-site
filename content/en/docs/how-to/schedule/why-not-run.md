---
title: "Find out why a job did not run"
description: "Ask Blowhorn why one scheduled row ran or not, in one read-only command."
weight: 152
---


One command names the reason a row has or has not run on this machine, in the
order the scheduler itself decides it, and ends in one plain sentence:

```bash
blowhorn schedule why 7
```

```text
row 7 · post · your-profile · linkedin

  enabled        yes
  valid          yes
  paused         no - row not held, studio not paused, all-machines not paused
  due            yes - next_run_at 2026-08-31 06:00:00, 14 min ago
  claimed        yes - laptop:9912 since 2026-08-31 06:02:10, lease expires 2026-08-31 06:32:10
  this machine   studio · store reachable · last tick 2026-08-31 06:14:02 (2 min ago)
  last run       2026-08-30 06:03:11 on laptop · ok · 12 attempted, 12 confirmed

studio did not run row 7 because laptop:9912 claimed it at 2026-08-31 06:02:10 and still holds the lease (expires 2026-08-31 06:32:10).
```

Read it top to bottom: enabled, valid, paused (naming the scope and how to lift
it), due, claimed, this machine, last run. The closing sentence is the answer;
quote it in a bug report with `--json` for the same answer machines can read.

## What the common answers mean

- **Paused.** The scope is named: the row, this machine, or all machines. Lift
  it with `blowhorn schedule resume`, with `--all` or `--row 7` to match.
- **Claimed by another machine.** A claim is a lease, not a lock: the holder
  renews it every ten minutes while the job runs, and a dead machine stops
  renewing, so its rows return to the pool when the lease lapses. `schedule
  list` names every holder in its Locked By column; your own claims read
  `(this machine)`.
- **Not due.** `Next Run At` has not passed yet. `schedule status` shows an
  estimated next tick for this machine.
- **Invalid.** `blowhorn schedule validate` names what the row breaks.

The command is read-only: it claims nothing, runs nothing and changes nothing,
so it is safe against a row that is mid-flight.

## Related

- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - create rows and run passes by hand
- [Pause and resume posting](/docs/how-to/schedule/pause/) - lift the scope that holds the row
- [Review what ran](/docs/how-to/measure/review-runs/) - the ledger behind "last run"
- [Troubleshooting](/docs/how-to/troubleshoot/troubleshooting/) - start from a symptom instead
