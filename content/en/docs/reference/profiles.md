---
title: "Profile reference"
description: "What a profile is: its directory, its store row, its keys per platform, and the Chrome column."
weight: 217
---


A profile is one identity Blowhorn posts as: a directory beside a
store row. The directory holds `config.yaml` and `data/`. Your account
row holds the organization, the credential keys that moved there, and
the Chrome mapping. This page describes; the steps live in the how-to
guides under Related.

## Creating a profile

`blowhorn profile set <name> --create` (or `--register`) creates both
halves, row first. It resolves the profile's email to one live Blowhorn account: no match or several matches refuses by name, and only
`--subject <uuid>` gets past several. It refuses a silent rename and
the two slug conflicts, writes the row, and only then scaffolds the
directory. An account outage refuses before anything is written, the
directory included. `blowhorn profile delete` retires the row first,
then moves the directory.

`blowhorn profile get <name>` prints one profile. `blowhorn profile
status` reports every profile with its sessions. `blowhorn profile set
<name> KEY=VALUE` writes keys; unknown keys for `config.yaml` are
refused by name.

## Credential Loading

Eligibility is credential existence: a profile may post on a platform
exactly when the secret for that platform exists. Handles, sessions in
Chrome, and follower counts grant nothing.

| Platform | Keys | Where the run reads them |
|---|---|---|
| LinkedIn | `LI_USERNAME`, `LI_PASSWORD` | `config.yaml` |
| X | `X_USERNAME` (password beside it for automated sign-in) | `config.yaml` |
| Reddit | `RDDT_USERNAME` (password beside it for automated sign-in) | `config.yaml` |
| Hacker News | `HN_USERNAME`, `HN_PASSWORD` | Your account |
| Slack | `SLACK_USER_TOKEN`, `SLACK_BOT_TOKEN`, or a captured workspace session | Your account, never `config.yaml` |
| Bluesky | `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` | `config.yaml` |
| GitHub | `GH_TOKEN` | Your account |

GitHub, Hacker News, and Slack are your account-credential platforms: a
run reads their secrets from your account, and `profile set` writes their
keys there. Every other platform still reads `config.yaml` until its
module moves. `blowhorn profile auth --platform slack` captures a
workspace session through the run's browser driver and lands it in your account; no Slack app install is needed.

A profile you name that holds no credential for anything in scope stops
the run with the reason naming it. `--profile all` skips such profiles
quietly.

## The Chrome column

Your account row beside each profile carries the Chrome column: which real
Chrome profile this Blowhorn profile acts in on this machine, keyed by
hostname. `blowhorn chrome map` writes it; `blowhorn chrome unmap`
clears it. A browser run with no mapping for its profile refuses
before anything opens, and never falls back to another profile. The
mapping is identity, never permission: it says where the run acts, not
what it may do.

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - write the Chrome column.
- [Platforms](/docs/reference/platforms/) - what each platform acts with.
- [Chrome reference](/docs/reference/chrome/) - the mapping commands and their shapes.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
