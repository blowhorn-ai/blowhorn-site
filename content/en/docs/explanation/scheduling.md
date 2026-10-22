---
title: "How scheduling works"
description: "Ten-minute passes, one shared queue across computers, leases, and the three pause scopes."
weight: 286
---


Posting on autopilot means a pass that runs without you, a queue every
computer can share, and pauses that mean what they say. This page explains
the arrangement; the words and commands are in
[Job options and schedules](/docs/reference/jobs/).

{{< major >}}One awake computer, set up for the profile. That's all the schedule needs.{{< /major >}}

One pass runs every ten minutes. It wakes, claims the activities that are
due, runs them one at a time, writes the ledger, and sleeps again. A
pass that finds nothing due costs nothing and changes nothing. The
service owns the passes while the app is closed; your terminal owns
the pass you trigger by hand, which never waits for the interval.

Several computers share one queue through leases, not locks. A claimed activity
says running with a lease timestamp, and the holder renews the lease
as it works. An activity whose lease lapsed is some dead computer's, and the
next pass reclaims it. That is why an activity's Status never reads as a
lock, and why two computers never work the same activity: the claim statement
reads the lease alone, atomically, and only one claimant wins it.

Three pause scopes cover the three reasons to stop. This computer's
file stops this computer and nothing else, for maintenance on one computer.
The organization-wide pause stops every computer sharing your account, with a
reason every banner repeats. One activity's pause holds that activity everywhere
until resumed. An activity is claimed only when none of the three says
paused, and quitting the app touches none of them: pausing is always
explicit, resuming always named.

An activity that did not run is never a mystery. `schedule why` reads the
claim the pass would make: paused at some scope, not yet due, lease
held by a living run, or eligible and waiting for the next pass. The
popover says the same thing in fewer words: due now, running, paused,
or needs you.

## Related

- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - create and edit jobs.
- [Pause and resume posting](/docs/how-to/schedule/pause/) - the pause scopes in practice.
- [Find out why a job did not run](/docs/how-to/schedule/why-not-run/) - read `schedule why`.
- [Job options and schedules](/docs/reference/jobs/) - recurrence words and scopes.
- [What runs when the app is closed](/docs/explanation/distribution/) - the service behind the passes.
- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) - the Routines view of Activity.
- [Collect and read your analytics](/docs/how-to/measure/analytics/) - read what the passes produced.
- [You're in control](/docs/explanation/youre-in-control/) - pause, one job at a time, one computer per job.
