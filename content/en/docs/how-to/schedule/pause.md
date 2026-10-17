---
title: "Pause and resume posting"
description: "Stop every scheduled claim on one machine, every machine, or one row, then resume."
weight: 151
---


Stop Blowhorn from claiming scheduled work without stopping the service. Reach
for this when a platform challenges a sign-in, when a session expires, or on
any day you want nothing to go out.

{{< major >}}Whole unit standing down. Your call. Unpause when you're ready.{{< /major >}}

## Pause this machine

```bash
blowhorn schedule pause --reason "LinkedIn challenge on kate"
blowhorn schedule status
blowhorn schedule resume
```

The flagless pause writes a local file beside your config, so it works even
when everything else is broken, and it survives a crash, a restart and a
reboot. Ticks keep running every ten minutes but claim nothing and exit 0.
Due times carry forward: a recurring row that fell due during the pause runs
once on resume, not once per missed interval.

A job already running finishes first. Killing a browser flow mid-post can leave
a half-done action on the platform, so the pause stops the next claim, never
the running job.

In the app, choose "pause this machine" in the popover or on the console. While
paused, the app also skips its session probe, so a paused Blowhorn opens no
browser at all.

## Pause every machine, or one row

```bash
blowhorn schedule pause --all --reason "X is rate limiting us"
blowhorn schedule pause --row 7 --reason "waiting on the page owner"
blowhorn schedule resume --all
blowhorn schedule resume --row 7
```

A row is claimed only when none of the three scopes says paused: this machine,
all machines, or that row. `--all` and `--row` live in your account, so every
machine sharing it honours them on its next claim; the flagless pause never
touches your account. In the app the same three scopes are "pause this machine",
"pause all machines" and "pause this row", each with a reason. Home says which
pause holds - "Paused on this Mac", "Paused on all Macs", or both - and its
resume lifts that pause only.

Lifting one scope leaves the other two as they were. A held row still reads
`due: yes` beside `paused: yes` in `blowhorn schedule list`: due keeps meaning
its time has passed. A pause is not `Enabled: no`: disabling a row is
editorial, with no reason and no intent to resume.

`trigger-now` on a held row exits 1 and names the scope. `--ignore-pause` on
`tick` or `trigger-now` overrides every scope, and a dry run previews through
the pause: held rows read `held` rather than `would-run`.

## Related

- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - create rows and run passes by hand
- [Find out why a job did not run](/docs/how-to/schedule/why-not-run/) - see which scope holds a row
- [Keep posting when the app is closed](/docs/how-to/schedule/background-service/) - the service that keeps ticking while paused
- [Change your defaults](/docs/how-to/settings/defaults/) - pace, excluded profiles, logs
- [You're in control](/docs/explanation/youre-in-control/) - every other safety control
