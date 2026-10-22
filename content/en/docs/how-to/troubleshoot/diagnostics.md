---
title: "Run a diagnostics check with Tells"
description: "Drive one profile to tells.blowhorn.ai under each operating mode, save the reports on this computer, and compare what each mode leaks."
weight: 197
---

Diagnostics is internal tooling for the Blowhorn organization. The desktop
app shows its Diagnostics area only when your session holds the Access
Diagnostics permission key: `blowhorn auth status --json` lists the keys
your session holds in the Blowhorn parent organization as
`permission_keys`. When the key is not there, the area is not shown at
all. The same runs are available from the command line.

## Run one mode

```bash
blowhorn diagnostics tells-run --profile alex --json
```

This drives the profile to the live [tells.blowhorn.ai](https://tells.blowhorn.ai/),
waits for its inspection to finish, and saves the report it renders as one
package on this computer. `--mode` chooses how Blowhorn reaches Chrome:

- `extension-background` -- the default: the extension driver in
  background mode, the way Blowhorn normally runs.
- `extension-classic` -- the extension driver in classic mode.
- `cdp` -- attach to the Chrome you already have open.
- `persistent` -- Blowhorn launches its own Chrome.

`--anonymous` uses a fresh throwaway profile labelled `anonymous` instead
of a named profile. The extension modes are refused for it by name: a
fresh profile has no Blowhorn extension installed, and a run that
pretended otherwise would measure nothing. `cdp` and `persistent` run.

## Run every mode

```bash
blowhorn diagnostics tells-sweep --profile alex --json
```

A sweep runs each mode in order and saves one package per mode plus a
sweep manifest naming them. A mode that fails is recorded in its own
package and in the manifest, and the sweep goes on: the comparison
between modes is the finding, so a partial sweep is still evidence.

## Read what you saved

```bash
blowhorn diagnostics reports --json
blowhorn diagnostics report --id <id> --json
```

Packages live on this computer only, under
`data/cache/diagnostics/tells` (or `BLOWHORN_DIAGNOSTICS_DIR` when set).
Nothing is uploaded. Each package names the Blowhorn and Chrome
versions, the mode and its driver, the profile and whether it was
anonymous, and the report exactly as the page produced it -- or why the
run failed.

## The audit trail

Each run, sweep and opening of the diagnostics area is recorded to
Blowhorn Cloud as an event (category `blowhorn`, actions
`diagnostics_run` and `diagnostics_open`) when you are signed in, so who
ran what, when, is on record. Posting is best-effort: signed out or
offline never fails a run.

```bash
blowhorn diagnostics opened --json
```

The desktop app runs this when the Diagnostics area opens; it answers
`{"ok": true, "posted": true}` when the event reached Blowhorn Cloud.
