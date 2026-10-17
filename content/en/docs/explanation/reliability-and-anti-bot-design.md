---
title: "How Blowhorn paces itself"
description: "Human typing and pauses, per-run pace, and why a failed post is not retried."
weight: 284
---


Blowhorn acts at human speed, and stops at the first thing it cannot
confirm. Both are deliberate: speed and retries are what get an
account flagged.

{{< major >}}Nobody can promise you won't get flagged. I can promise I won't rush, won't repeat myself and won't touch your CAPTCHA.{{< /major >}}

Typing arrives keystroke by keystroke with a computed delay between
keys, and actions are separated by random pauses of a few seconds,
scaled by the run's pace. `--pace` sets it: `fast`, `normal`, `slow`,
or a numeric multiplier, resolved from the flag, then the environment,
then the defaults file. A long unattended run earns the slow pace; a
failure never earns a retry click.

Public actions are never repeated on a guess. The sending control is
clicked once per run; "no confirmation, the dialog still reads open"
reports the row not sent, never sends it again, and never reports it
sent either. What the platform showed after the click is a reading, not
a fact, so the row reads clicked, outcome not read, and waits for you.
See [How Blowhorn avoids repeat posts](/docs/explanation/never-twice/).

A typing failure fails only its own row. The dispatcher has no
per-row rescue around the loop, so a lost typing target would abandon
every remaining queued row for that profile; every call site therefore
contains the failure to its own unit of work instead.

Within a run, Blowhorn doesn't retry a failed post; it moves on to the next item. If a post goes out but Blowhorn can't record it, it stops that profile's queue rather than risk posting twice. Scheduled jobs only re-run a failure if you turn on retries, and they're off by default.

## Hacker News is the least forgiving platform

A Hacker News submission cannot be deleted, and coordinated-looking
promotion gets the whole domain banned. Blowhorn treats it
accordingly: at most 2 link submissions per profile per UTC day, titles
held to 80 characters with the row failing rather than truncating, no
voting ever, and a comment row that can only ever be a comment. A
rate-limited run fails the row and waits; it never retries to beat the
limiter.

## Related

- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - pace your run.
- [Post to Hacker News](/docs/how-to/publish/post-to-hacker-news/) - the strictest rules, worked.
- [Platforms](/docs/reference/platforms/) - per-platform limits.
- [How Blowhorn avoids repeat posts](/docs/explanation/never-twice/) - one click per run.
- [Change your defaults](/docs/how-to/settings/defaults/) - the pace default.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
