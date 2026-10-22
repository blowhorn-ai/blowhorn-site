---
title: "You're in control"
description: "Every worry in one place: getting banned, posting by mistake, posting twice, embarrassing yourself, and AI running away. The controls that stop each one, and where they live."
weight: 291
---


Blowhorn is built for AI. Agents can drive it, queue for it and run it on
autopilot. But the AI is never in control. You are. Even when you hand
approval to an AI agent and let it run, the policies inside Blowhorn still
decide what may happen, how fast, and when to stop.

{{< major >}}You give the orders. I carry them out: one window, one profile, one platform at a time. Nobody types into two windows at once. Not in my unit.{{< /major >}}

This page gathers every worry people bring to a tool that posts as them,
and answers each with the control that handles it, where that control
lives, and the page that documents it.

<!-- Video placeholder: "You're in control" overview (60-90 s). What Blowhorn will and won't do on its own, the human limit, and where the controls live. -->

## Blowhorn limits itself to what a human could do

Any given Blowhorn install only runs one automation on a given platform
for a given profile at a time. You wouldn't expect a human to have two
browser windows open, typing into both at once, so Blowhorn doesn't
either. It acknowledges that limit and holds itself to it.

Here is how that is enforced today:

- **One profile, one platform, one process.** Before a run opens a
  LinkedIn, X, Reddit or Hacker News session for a profile, it takes a
  lock on that profile and platform on this computer. A second run that wants
  the same profile on the same platform is refused with "profile ... is
  in use by another blowhorn process; wait for it to finish or stop it",
  and its activities stay in the queue for the next pass. The lock is the same
  whichever way Blowhorn reaches Chrome.
- **Scheduled work runs one job at a time.** The background service runs
  one pass at a time, and a pass works through its jobs one after
  another, never side by side.
- **One send per action.** The send control is clicked once. There is
  no retry click.

Coming soon: an option to go stricter still, so that only one
automation runs on a platform at a time even across different profiles.

<!-- Video placeholder: "Blowhorn limits itself to what a human could do". Two runs for the same profile and platform; the second waits. -->

## Will I get banned?

Nobody can promise that for any tool, and we won't. Platforms change
their rules, and automation can still be blocked or sessions broken,
especially on X. What Blowhorn does is behave like a careful person and
stop instead of guessing:

- **It types and clicks like a person.** Typing arrives key by key with a
  computed delay between keys, actions are separated by random pauses,
  and clicks land at slightly varied points with natural hover and press
  timing. You set the pace.
- **It caps itself.** At most 2 Hacker News link submissions per profile
  per day, and at most 400 X follows per profile a day and 15 in any 15
  minutes. `--limit` caps how many people a follow or accept run
  takes on, and how many jobs a scheduler pass runs.
- **It doesn't retry blindly.** Within a run, Blowhorn doesn't retry a failed post; it moves on to the next item. If a post goes out but Blowhorn can't record it, it stops that profile's queue rather than risk posting twice. Scheduled jobs only re-run a failure if you turn on retries, and they're off by default.
- **It never solves a CAPTCHA or a 2FA prompt.** When a platform asks for
  one, Blowhorn stops and leaves it for you. In a visible window it can
  wait while you finish it; unattended, the run stops.
- **It walks away from warnings.** A LinkedIn invitation flagged "Take
  care when connecting" is skipped, never confirmed.

Read more in [How Blowhorn paces itself](/docs/explanation/reliability-and-anti-bot-design/)
and [Why flagged invitations are skipped](/docs/explanation/invitation-safety/).

Curious what sites can see about your browser? Run the free check at
[Blowhorn Tells](https://tells.blowhorn.ai/). It shows what a page can read,
not what a platform will decide.

<!-- Video placeholder: "Will I get banned?" Typing at slow and normal pace side by side, a rate cap stopping a run, and a CAPTCHA left for the user. -->

## Will it post something I didn't mean to?

- **Nothing goes out unapproved.** A content activity is published only when
  its `Approved?` column reads `yes` or `true`. Anything else is a draft.
- **An activity never widens.** A blank or unknown `Profile` is refused, never
  read as "everybody". An activity with `Comment on` set can only ever be a
  comment.
- **Rehearse first.** `--check-queue` lists what a run would do, and
  `--dry-run` walks it end to end without publishing, following or
  writing anything. Make dry run your default until you trust a setup.
- **Stop it any time.** Pause this computer, every computer in your organization,
  or one scheduled job, each with a reason. A job already running
  finishes first, because killing a browser mid-post can leave a
  half-done action on the platform.

## Will it post twice?

- **One click per run.** The send control is clicked a single time.
- **"Clicked, outcome not read" is not a retry.** When Blowhorn clicked
  but could not read a confirmation, the activity is recorded as clicked and
  held for you. It is neither sent again nor marked done.
- **One computer per job.** Every computer sharing your organization's queue claims
  a scheduled job before it runs it, under a lease, so two computers can't
  run the same job at once.
- **Done is recorded per profile.** `Date Promoted` records when each
  profile published an activity, so the next run skips it.

Read more in [How Blowhorn avoids repeat posts](/docs/explanation/never-twice/).

## Will it embarrass me?

- **No guessing at what landed.** A post's link is recorded only when
  Blowhorn read it back. It never records the page it started on as the
  new post.
- **Hacker News is held to its own rules.** Titles over 80 characters
  fail the activity rather than being cut, Blowhorn never votes there, and a
  rate-limited run waits rather than retrying.
- **Your words, unchanged.** Blowhorn's actions on these platforms are
  scripted, not written by AI. It types the text in your queue.

## What if an AI agent is driving?

An agent drives Blowhorn the same way you do: through the queue and the
documented CLI. Every rule on this page applies no matter who started
the run. The rate caps, the one-at-a-time lock, the single send click
and the refusal to solve a CAPTCHA are built in, not flags an agent can
drop. Give the agent dry run first,
keep `Approved?` as your gate, and pause any scope the moment something
looks off. Lifting a pause takes `blowhorn schedule resume`, or an
explicit `--ignore-pause` on a single run.

<!-- Video placeholder: "Handing approval to an AI agent". An agent queues activities, dry-runs them, and a pause stops the next claim. -->

## Every control, and where it lives

| Control | What it does | Where it lives | Reference |
|---|---|---|---|
| Dry run | Walks a run without publishing, following or writing | `--dry-run` on every action command; `defaults.dry_run`; Settings in the app | [Configuration](/docs/reference/configuration/), [`blowhorn post`](/docs/reference/post/) |
| Check the queue | Lists what a run would do, opening nothing | `blowhorn post --check-queue` | [`blowhorn post`](/docs/reference/post/) |
| Approval gate | Only approved activities are published | The `Approved?` column of each content activity | [Content queue](/docs/reference/content-queue/) |
| Pause | Stops new claims on this computer, every computer, or one scheduled job | `blowhorn schedule pause`, with `--all` or `--activity`; the pause controls in the app's popover and console | [Pause and resume posting](/docs/how-to/schedule/pause/) |
| Stop the current pass | Ends the background service's pass at its next safe point; the activity in progress returns to the queue | `blowhorn service cancel` | [CLI reference](/docs/reference/cli/) |
| Pace | How fast Blowhorn types and how long it pauses between actions | `--pace fast`, `normal`, `slow` or a number; `defaults.pace`; Settings in the app | [Change your defaults](/docs/how-to/settings/defaults/) |
| Pointer movement | Turns the pointer movement before clicks on or off | `defaults.no_mouse_move`; Settings in the app | [Configuration](/docs/reference/configuration/) |
| Run size | Caps how many people a follow or accept run takes on, and how many jobs a pass runs | `--limit` on `follow`, `accept` and `schedule tick` | [CLI reference](/docs/reference/cli/) |
| Excluded profiles | Leaves profiles out of `--profile all` | `--exclude`; `defaults.exclude`; Settings in the app | [Change your defaults](/docs/how-to/settings/defaults/) |
| Rate caps | 2 Hacker News submissions per profile per day; 400 X follows per profile a day and 15 per 15 minutes | Built in | [Platforms](/docs/reference/platforms/) |
| No blind retries | Within a run, Blowhorn doesn't retry a failed post; it moves on to the next item. If a post goes out but Blowhorn can't record it, it stops that profile's queue rather than risk posting twice. Scheduled jobs only re-run a failure if you turn on retries, and they're off by default. | Built in; scheduled-job retries are opt-in | [How Blowhorn paces itself](/docs/explanation/reliability-and-anti-bot-design/) |
| One automation per platform per profile | A second run for the same profile and platform on this computer is refused | Built in | [Chrome reference](/docs/reference/chrome/) |
| One send per action | The send control is clicked once; an unread outcome is held for you | Built in | [How Blowhorn avoids repeat posts](/docs/explanation/never-twice/) |
| One computer per job | A scheduled job is claimed by one computer at a time | Built in, through your account | [How scheduling works](/docs/explanation/scheduling/) |
| CAPTCHA and 2FA | Left for you; never solved | Built in | [Fix sign-in problems](/docs/how-to/troubleshoot/sign-in-problems/) |

## Your Risk Profile

Think of your Risk Profile as the dials for how much risk you'll take
and how fast you want things produced. One choice sets them together:
cautious, standard (the default) or brisk. It covers caps, spacing
between actions, quiet hours, outreach, the pause after a sign-in
challenge and, unless you set the pace yourself, the pace. Pick
cautious for a new account or an unattended run, and brisk for an
established one you are watching. A new profile or a new computer runs
cautious until it has some history, whatever you chose.

Choose it in the app under Settings; for one profile or one platform,
use `blowhorn risk set`. The [configuration reference](/docs/reference/configuration/#risk-profile-presets)
lists what each preset sets.

## Related

- [How Blowhorn paces itself](/docs/explanation/reliability-and-anti-bot-design/) - human pacing and the no-retry rule.
- [How Blowhorn avoids repeat posts](/docs/explanation/never-twice/) - one click per run.
- [Why flagged invitations are skipped](/docs/explanation/invitation-safety/) - walking away from warnings.
- [Pause and resume posting](/docs/how-to/schedule/pause/) - the three pause scopes.
- [Change your defaults](/docs/how-to/settings/defaults/) - pace, exclusions and dry run.
- [Configuration reference](/docs/reference/configuration/) - every option and where it is set.
- [Platforms](/docs/reference/platforms/) - actions and limits per platform.
