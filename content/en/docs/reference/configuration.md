---
title: "Configuration reference"
description: "Precedence, every `.blowhorn.yaml` option, environment variables, and output logging."
weight: 218
---

# Configuration reference

How Blowhorn resolves what a run uses, and where its output goes.
`blowhorn/config_schema.py` is the one list of options; `blowhorn
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
| `defaults.no_mouse_move` | `BLOWHORN_NO_MOUSE_MOVE` | off | Skip the pointer simulation before clicks |
| `defaults.risk_profile` | `BLOWHORN_RISK_PROFILE` | `standard` | `cautious`, `standard` or `brisk`: caps, spacing, quiet hours, outreach and pace in one choice (see below) |
| `defaults.risk_profile_by_platform` | none | none | A preset per platform, for example `x: cautious` |
| `defaults.risk_profiles` | none | none | A preset per profile: a name, or a map with `default` and platform keys |
| `defaults.logs.directory` | `BLOWHORN_LOG_DIR` | `logs/` in the checkout | Where daily logs go |
| `defaults.logs.retention_days` | `BLOWHORN_LOG_RETENTION_DAYS` | 30 | Days of daily logs kept; 0 keeps all |
| `defaults.chrome.launch_mode` | `BLOWHORN_CHROME_LAUNCH` | `extension` | How a run reaches Chrome |
| `defaults.chrome.automation_data_dir` | `BLOWHORN_CHROME_AUTOMATION_DATA_DIR` | Blowhorn's own directory | Where a launched Chrome keeps its session |
| `defaults.chrome.data_dir` | `BLOWHORN_CHROME_DATA_DIR` | Your real Chrome directory | Where the installed Chrome is read from |
| `defaults.slack.auth_mode` | `BLOWHORN_SLACK_AUTH` | your captured session first | Which Slack credential may send: session, user-token, bot-token, or a list tried in order |
| (flag only) | `BLOWHORN_TEE_STDOUT` | off | Flush the stdout copy per write for a supervising wrapper |
| `defaults.store.backend` | `BLOWHORN_STORE_BACKEND` | `postgres` | The one store backend; anything else is refused by name |
| `defaults.store.organization` | `BLOWHORN_STORE_ORGANIZATION` | none; while unset, nothing runs | The organization every row is scoped to |
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
| Caps (share of each built-in ceiling) | 25% | 100% | 100% |
| Spacing between public actions | 15 min plus up to 15 min | none | none |
| Quiet hours (local) | 22:00 to 07:00 | none | none |
| Outreach (connect, invite, follow) | off | on | on |
| Pause after a CAPTCHA or checkpoint | 72 h | 24 h | 12 h |
| Retries of a failed scheduled job | 0 | 0 | 1 |
| Warmup | 14 days | 7 days | 3 days |

Scheduled jobs on a new profile or a new Mac run cautious until the warmup is done, whatever you chose. A run you start yourself is not held by the warmup, only noted; it still follows the caps, quiet hours and outreach setting of the preset you chose. When a run covers several profiles or platforms, a held one is skipped by name and the rest run. To run once anyway, add `--ignore-risk`, or choose **Run anyway** next to a held job in the app's Runs screen. Logins are never retried under any preset. Choose a preset in the app under Settings, or with `blowhorn risk set cautious` (add `--profile` to store it on one profile, `--platform` for one platform); `blowhorn risk show` says which preset is in effect and where it comes from.

## Output logging

The daily log is a copy; the terminal streams are never dropped, piped
or not. The directory resolves as `--log-dir`, then `BLOWHORN_LOG_DIR`,
then `defaults.logs.directory`, then the checkout's `logs/`. A default
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
