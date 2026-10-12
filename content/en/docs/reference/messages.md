---
title: "Messages and exit codes"
description: "Every refusal sentence keyed by its first words, with the cause, the fix, and the exit code."
weight: 219
---

# Messages and exit codes

What a failed run prints, why, and what fixes it. Entries are keyed by
the sentence's first words. Exits: 0 ran clean; 1 the run failed; 2 the
invocation was wrong; 3 your account was unreachable. A run cancelled
between passes exits 75.

## Your account

A run that needs your account and cannot reach it prints the cause's own
wording, then `error: store unavailable`, and exits 3. There is no
traceback. Check the connection and run again; nothing was published
and nothing was marked done.

Any other store error prints its own sentence and exits 1. A ledger
write your account refuses names the person and stops the run before its
next platform action, so the run halts rather than acting without
recording.

## Eligibility and plans

A profile you named that is eligible for nothing in scope stops the run
with the reason and exits 1. `--profile all` skips such profiles
quietly instead. A run the organization's plan does not cover exits 1;
an unknown `BLOWHORN_ENTITLEMENT` value is refused by name rather than
read as off. Dry runs are never refused: they publish nothing. See
[Plans and limits](/docs/reference/plans/).

## Chrome and the extension

`another blowhorn run holds the Chrome extension bridge`: two runs want
the extension at once. Wait for the other run or stop it; this run did
nothing.

`chrome refused the connection (Allow was declined ...)`: the attach
handshake did not complete. Keep a Chrome window open, approve the
Allow dialog, and run again. In a scheduled pass the Allow window is
short; prefer the extension default.

`extension_outdated` with two versions: the installed extension is older
than the run needs. Reload or update the extension and run again.

A profile with no Chrome mapping on this machine, a mapped directory
Chrome no longer has, or an identity that drifted since binding is
refused by name before anything opens, with the command that re-maps
it. There is never a fallback to another profile.

## Sign-in

`X session expired ... redirected to login page` and `Reddit session
expired ... redirected to login page`: sign in again in that Chrome
profile, by hand, then run again. `X rejected the credentials for
@...`: the stored username or password is wrong; fix it and run again.
A CAPTCHA or second-factor challenge always hands back to you; an
unattended run never waits. For X, see
[Fix a sign-in that stopped working](/docs/how-to/troubleshoot/sign-in-problems/).

## The queue and the schedule

`title is ... characters; Hacker News allows 80 ...`: shorten the
title to 80 characters; the row failed rather than truncating because a
submission cannot be edited after it lands. `Rate limited: HN said
...`: Hacker News throttled the run; the row failed, wait before
retrying, and never retry to beat the limiter.

`Unsupported Recurrence '...'` and `Invalid recurrence interval
'...'`: the schedule row's word is not one Blowhorn knows; use `once`,
`hourly`, `daily`, `weekly`, `monthly`, or `every:N`. See
[Job options and schedules](/docs/reference/jobs/).

A row `clicked, outcome not read` is not an error: the sending control
was clicked and no confirmation was read back. Check the platform,
then clear "Date Promoted" to try again or leave it. See
[Content queue columns and row states](/docs/reference/content-queue/).

## Related

- [Content queue columns and row states](/docs/reference/content-queue/) - row states including unread.
- [Job options and schedules](/docs/reference/jobs/) - recurrence words.
- [Plans and limits](/docs/reference/plans/) - plan refusals.
- [Fix a sign-in that stopped working](/docs/how-to/troubleshoot/sign-in-problems/) - expired sessions.
- [How Blowhorn paces itself](/docs/explanation/reliability-and-anti-bot-design/) - why a run stops instead of retrying.
