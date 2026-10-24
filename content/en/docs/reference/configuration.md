---
title: "Configuration reference"
description: "Precedence, every `.blowhorn.yaml` option, environment variables, and output logging."
weight: 218
---


How Blowhorn resolves what a run uses, and where its output goes.
`engine/blowhorn/config_schema.py` is the one list of options; `blowhorn
config show` prints each with its stored, environment, effective, and
source values. `blowhorn config set` edits the file without rewriting
it: comments, order, and quoting survive.

Precedence, highest first: the CLI flag, the environment variable, the
`.blowhorn.yaml` default, then the built-in. The file lives beside the
current directory by default (`./.blowhorn.yaml`); `--config` points
at another one.

Only the Blowhorn names are read: `./.blowhorn.yaml` and the `BLOWHORN_*`
environment variables.

## Every option `.blowhorn.yaml` supports

| Default key | Environment | Built-in | Means |
|---|---|---|---|
| `defaults.profile` | `BLOWHORN_PROFILE` | `all` | The profile a run uses when `--profile` is not given |
| `defaults.platform` | `BLOWHORN_PLATFORM` | `all` | The platform a run targets when `--platform` is not given |
| `defaults.exclude` | `BLOWHORN_EXCLUDE` | none | Profiles left out of `--profile all` |
| `defaults.headless` | `BLOWHORN_HEADLESS` | off | Unattended background window |
| `defaults.headed` | `BLOWHORN_HEADED` | off | Visible window in front |
| `defaults.dry_run` | `BLOWHORN_DRY_RUN` | off | Simulate every run |
| `defaults.pace` | `BLOWHORN_PACE` | `normal` | `fast`, `normal`, `slow`, or a number; commands that never pause accept and ignore it |
| `defaults.pace_by_platform` | `BLOWHORN_PACE_BY_PLATFORM` | none | A pace per platform, in `defaults.pace`'s values: `x: slow, linkedin: 1.5`. A platform with no entry runs at `defaults.pace`; a `--pace` flag or `BLOWHORN_PACE` covers every platform. `config show --json` reports each platform's effective pace and which setting supplied it |
| `defaults.no_mouse_move` | `BLOWHORN_NO_MOUSE_MOVE` | off | Skip the pointer simulation before clicks |
| `defaults.concurrency.per_platform` | `BLOWHORN_CONCURRENCY_PER_PLATFORM` | `platform` | `platform`: one automation per platform at a time across all profiles on this computer. `profile`: one automation per profile and platform at a time |
| `defaults.concurrency.max_runs` | `BLOWHORN_CONCURRENCY_MAX_RUNS` | none | At most this many automations running at once on this computer, however they were started; a run over the limit is refused and its activities stay queued. Unset runs as many as are started |
| `defaults.risk_profile` | `BLOWHORN_RISK_PROFILE` | `standard` | `cautious`, `standard` or `brisk`: pace, pointer movement, caps, spacing, quiet hours, outreach and how much runs at once in one choice (see below) |
| `defaults.risk_profile_by_platform` | none | none | A preset per platform, for example `x: cautious` |
| `defaults.risk_profiles` | none | none | A preset per profile: a name, or a map with `default` and platform keys |
| `defaults.approval.mode` | `BLOWHORN_APPROVAL_MODE` | `off` | `off`, `agent` or `all`: who must approve before work publishes (see below) |
| `defaults.caps` | none | none | Your own daily caps per platform and action, under the built-in ceilings (see below) |
| `defaults.quiet_hours` | `BLOWHORN_QUIET_HOURS` | none | Hours when the scheduler claims nothing, written `HH:MM-HH:MM` like `22:00-07:00` (the window may wrap midnight). A due activity inside it is held, not failed, and runs when the window ends. A profile's own Quiet Hours setting wins for its activities |
| `defaults.quiet_hours_tz` | `BLOWHORN_QUIET_HOURS_TZ` | this computer's zone | The IANA time zone `defaults.quiet_hours` is read in, like `America/New_York`. A profile's own Quiet Hours Time Zone setting wins for its activities |
| `defaults.concurrency.per_platform` | `BLOWHORN_CONCURRENCY_PER_PLATFORM` | your Risk Profile's value | `platform` (one profile per platform at a time) or `profile` (profiles may share a platform). Beats the Risk Profile's value (see below); reported by `blowhorn risk show` |
| `defaults.logs.directory` | `BLOWHORN_LOG_DIR` | `data/logs/` in the checkout | Where daily logs go |
| `defaults.logs.retention_days` | `BLOWHORN_LOG_RETENTION_DAYS` | 30 | Days of daily logs kept; 0 keeps all |
| `defaults.chrome.launch_mode` | `BLOWHORN_CHROME_LAUNCH` | `extension` | How a run reaches Chrome |
| `defaults.chrome.automation_data_dir` | `BLOWHORN_CHROME_AUTOMATION_DATA_DIR` | Blowhorn's own directory | Where a launched Chrome keeps its session |
| `defaults.chrome.data_dir` | `BLOWHORN_CHROME_DATA_DIR` | Your real Chrome directory | Where the installed Chrome is read from |
| `defaults.slack.auth_mode` | `BLOWHORN_SLACK_AUTH` | your captured session first | Which Slack credential may send: session, user-token, bot-token, or a list tried in order |
| (flag only) | `BLOWHORN_TEE_STDOUT` | off | Flush the stdout copy per write for a supervising wrapper |
| `defaults.store.backend` | `BLOWHORN_STORE_BACKEND` | `cloud` | `cloud` or `postgres` (the store database through the bastion tunnel, for maintainers). A `postgres` value in the file or in `BLOWHORN_STORE_BACKEND` opens Cloud unless `BLOWHORN_MAINTAINER=1`. Cloud uses the organization you signed in to. It reads and writes profiles, their social accounts and content, reads destinations, records and lists runs, and reads and writes analytics, activity, ledger entries and LinkedIn analytics pages. A changed ledger value is written. A later analytics or activity reading replaces the stored one. Run lists are the organization's for an organization admin and your own otherwise. Destinations are the ones you own, plus the ones assigned to the environment `BLOWHORN_CLOUD_ENVIRONMENT` (or `environment_id` in `cloud.yaml`) names, and only a destination's owner can change it. Analytics and activity lists are the organization's. Anything else is refused by name |
| `defaults.store.organization` | `BLOWHORN_STORE_ORGANIZATION` | none; the cloud store uses the organization you signed in to, and the Postgres store runs nothing while it is unset | The organization every activity is scoped to |
| `defaults.store.config` | `BLOWHORN_STORE_CONFIG` | a private file outside the checkout | The private document holding the connection |

`headed` and `headless` are one choice with two spellings: the higher
layer wins, so a `--headless` flag beats a `headed` default from the
file, and `--headed` wins a tie. The settings screen reports each on
its own; a flagless run resolves them together so exactly one
survives.

A version-1 file that still says `persistent` reads as `extension` on
every run; only a validated `config set` of another key moves the file
to version 2. The ten `store.*` connection options are private: they
stay out of `config show`.

## Risk Profile presets

| Dial | cautious | standard | brisk |
|---|---|---|---|
| Pace (when `defaults.pace` is unset) | slow | normal | fast |
| Pointer movement (when `defaults.no_mouse_move` is unset) | on | on | on |
| Caps (share of each built-in ceiling) | 25% | 100% | 100% |
| Spacing between public actions | 15 min plus up to 15 min | none | none |
| Quiet hours (local) | 22:00 to 07:00 | none | none |
| Outreach (connect, invite, follow) | off | on | on |
| Pause after a CAPTCHA or checkpoint | 72 h | 24 h | 12 h |
| Retries of a failed scheduled job | 0 | 0 | 1 |
| Warmup | 14 days | 7 days | 3 days |
| Runs sharing a platform (when `defaults.concurrency.per_platform` is unset) | one profile at a time | one profile at a time | different profiles may share |
| Runs at once overall, as the preset describes it (reported by `risk show`; not enforced until you set `defaults.concurrency.max_runs`) | at most 1 | no limit | no limit |

No preset can raise a built-in ceiling: the caps are a share of one, never more, and the concurrency values only ever hold runs back at or below the shipped posture (one profile per platform, which `standard` keeps).

Any dial you set yourself beats the preset for that dial: your own `defaults.pace`, `defaults.no_mouse_move` or `defaults.concurrency` value is the one that applies, and the rest of the preset still applies around it. A profile with a dial set outside the preset is a **custom** profile. `custom` is a description, not a fourth preset you can pick: `blowhorn risk show` names the dials set outside the profile, and `blowhorn config show` names the preset as a dial's source when the preset is the layer that supplied it.

The concurrency rows are the values the presets carry. `blowhorn risk show` reports them, each with the layer that supplied it. The limit on runs at once is enforced only when you set `defaults.concurrency.max_runs` yourself; a preset's own value is reported, not enforced, and the per-platform lock is not wired yet, so `defaults.concurrency.per_platform` is reported the same way.

Scheduled jobs on a new profile or a new computer run cautious until the warmup is done, whatever you chose -- the cautious concurrency values included. A run you start yourself is not held by the warmup, only noted; it still follows the caps, quiet hours and outreach setting of the preset you chose. When a run covers several profiles or platforms, a held one is skipped by name and the rest run. To run once anyway, add `--ignore-risk`, or choose **Do it anyway** next to a held item under Activity › History. Logins are never retried under any preset. Choose a preset in the app under Settings, or with `blowhorn risk set cautious` (add `--profile` to store it on one profile, `--platform` for one platform); `blowhorn risk show` says which preset is in effect and where it comes from.

## Approval mode

`defaults.approval.mode` decides whose writing is enough to publish.
`off` - the built-in - is the behaviour Blowhorn has always had: whoever
writes a content activity sets its `Approved?`, and actions that publish
without an activity (`post --amplify`, `post --message`, `follow`, an
ad-hoc `comment`, a confirmed `slack send`) publish as run. `agent` keeps
that for a person, but holds an agent's work: a caller marked with
`BLOWHORN_ACTOR=agent`, a scheduler run, or any run with no terminal
attached has its activities stored unapproved whatever the payload asked,
and its ad-hoc actions are refused with a sentence pointing at the queue.
`all` holds every activity and every ad-hoc action, whoever wrote it.
You at a terminal, or in the app, count as a person for writing activities (approving is `blowhorn content approve` at a terminal); under `all` the
app's own writes wait too, and the CLI is the door.

A schedule job that would publish on its own - `follow`, `comment`
with a target and a message, `post` with `amplify` - is a standing
instruction to publish unapproved, so creating one, or changing what
an existing one would publish, is refused for the same callers: an
agent under `agent`, anyone under `all`. A job that works the queue
is never refused, and a job already scheduled is not re-judged when
the mode changes: it runs as its creator's standing instruction.

The door is `blowhorn content approve <activity>`: it sets `Approved?`
and records who approved and when in the activity's `Approved by` column
(see [Content queue](/docs/reference/content-queue/)). Approving is a person's act, so
an agent-signalled caller is refused by `content approve` itself, in
every mode - an agent cannot approve its own work. An unknown mode is
refused by name before anything runs.

## Daily caps

Every platform and action already has a built-in daily ceiling, and a
Risk Profile preset may take only a share of it. `defaults.caps` lets you
set a lower daily cap of your own, per platform and per action:

```yaml
defaults:
  caps:
    x:
      post_per_day: 3
      follow_per_day: 20
```

The key is the action in your words; it bounds the action Blowhorn counts:

| You write | It bounds |
|---|---|
| `post_per_day` | posts |
| `comment_per_day` | comments |
| `follow_per_day`, `connect_per_day`, `invite_per_day` | outreach: follows, connects and invites together |
| `repost_per_day` | shares (reposts) |
| `amplify_per_day`, `react_per_day` | reactions |
| `accept_per_day` | accepts, on the platforms that have them |

The gate's own names (`outreach_per_day`, `share_per_day`,
`reaction_per_day`) work too. A platform with no such action refuses the
key by name, as do a zero, a negative or a fractional count.

A user cap can only lower: a value above the built-in ceiling is accepted
and simply never binds, and a preset's share or a warmup can still take
the effective cap lower. The count is the run ledger in your account,
over the trailing 24 hours, so the cap holds on every computer sharing
the account; a row it holds stays queued, reads `held` with the reason
`daily cap (N <action> a day, your cap)`, and runs when the oldest counted
action ages past a day. Caps are per day only; the built-in hourly
ceilings are unchanged.

Set one with `blowhorn config set defaults.caps.x.post_per_day 3` (an
empty value clears it), or write the map in the file. For one profile
only, the profile's `Daily Caps` store attribute takes the same caps in
one line -- `x.post:3, x.follow:20` -- and beats the file per action.
`blowhorn config show` reports every platform and action with its
built-in ceiling, your value when set, and the effective (lower) number.

A cap that cannot be read (a zero, a negative or fractional count, an unknown
platform or action) never uncaps the account: scheduled jobs and hand runs
for that platform, or for that profile when it is the `Daily Caps` attribute,
are held with the entry named until it is fixed, and `config show` lists the
caps as `invalid` with the reason.

## Output logging

The daily log is a copy; the terminal streams are never dropped, piped
or not. The directory resolves as `--log-dir`, then `BLOWHORN_LOG_DIR`,
then `defaults.logs.directory`, then the checkout's `data/logs/`. A default
that cannot be used fails silently; a directory you named reports why.
Only files the retention pass recognizes by name are ever deleted:
daily logs past their days (30 by default), and the three dateless
capture files rolling past their size bound. Per-job logs, the ledger,
and the scheduler heartbeat live beneath the same directory and are
never pruned by it.

`--tee-stdout` is about liveness, not logging: it flushes the stdout
copy per write, and with no usable log directory it line-buffers the
real stdout instead. It is read before command parsing, so it is not a
per-command flag.

## Related

- [Change your defaults](/docs/how-to/settings/defaults/) - change the defaults.
- [Choose how Blowhorn reaches Chrome](/docs/how-to/settings/launch-mode/) - the launch-mode option in practice.
- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) - the Settings screen.
- [Messages and exit codes](/docs/reference/messages/) - what a bad value reports.
- [How scheduling works](/docs/explanation/scheduling/) - what the heartbeat and per-job logs are for.
- [You're in control](/docs/explanation/youre-in-control/) - which options are safety dials.
- [CLI reference](/docs/reference/cli/) - every command and flag.
