---
title: "Change your defaults"
description: "Set pace, excluded profiles, dry-run default, notifications and logs, in the app or the config file."
weight: 170
aliases: [/docs/how-to/configure-blowhorn/]
---

# Change your defaults

Set the defaults every run starts from: pace, excluded profiles, dry-run,
notifications and logs. Change them in the app's Settings, or with `blowhorn
config set` for the whole checkout.

## See what is in effect

```bash
blowhorn config show
blowhorn config show --json
```

## Change a default

```bash
blowhorn config set defaults.pace slow
blowhorn config set defaults.exclude ada,kate
blowhorn config set defaults.dry_run true
```

A flag beats an environment variable, which beats `.blowhorn.yaml` in the
directory you run from, which beats the built-in. Every option and its
environment variable is listed in the configuration reference.

To read one option and learn which document holds it:

```bash
blowhorn config get defaults.profile
blowhorn config get store.password        # set / not set, never the value
```

Your account connection is configured the same way, but its `store.*` keys live
in a private file, never in `.blowhorn.yaml`. During early access your
Blowhorn administrator sets them up.

## Choose where output is written

```bash
blowhorn post --profile ada --log-dir ./logs      # this run only
export BLOWHORN_LOG_DIR=./logs                    # this shell
blowhorn config set defaults.logs.directory ./logs
```

## Choose how long the daily logs are kept

```bash
blowhorn config set defaults.logs.retention_days 7     # keep a week
blowhorn config set defaults.logs.retention_days 0     # keep every daily log
export BLOWHORN_LOG_RETENTION_DAYS=7                   # this shell
```

Every run deletes daily logs older than that (30 days if you set nothing),
judged by the date in the file name. Nothing else in the directory is pruned.

## Related

- [Choose how Blowhorn reaches Chrome](/docs/how-to/settings/launch-mode/) - the launch and driver settings these defaults sit above
- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - per-job parameters that beat these defaults
- [Review what ran](/docs/how-to/measure/review-runs/) - read the logs these settings keep
- [You're in control](/docs/explanation/youre-in-control/) - how pace and dry run fit with the built-in limits
