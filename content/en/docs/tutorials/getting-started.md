---
title: "Getting started with the Blowhorn CLI"
description: "List pending content, preview a run with a dry run, and publish from the command line."
weight: 10
draft: true
---


In this tutorial you will install Blowhorn, confirm it can see your profiles,
and watch it walk the posting queue end to end - without publishing anything.
It takes about ten minutes. Every command here is safe to run: the one command
that could publish is given with `--dry-run`.

You need macOS or Linux, Python 3.14, and a checkout of this repository. This
tutorial uses the contributor install; if you only want to use Blowhorn, install
the signed app instead ([Install the app](/docs/how-to/set-up/install-the-app/)).

## 1. Install {#section-1-install}

From the root of the checkout:

```bash
./tools/install.sh
export PATH="$HOME/.local/bin:$PATH"
```

The installer creates a virtualenv at `./venv`, installs the requirements,
downloads the Playwright Chromium runtime, and writes an `blowhorn` launcher to
`~/.local/bin`. It then runs `blowhorn setup`, which checks this computer, asks
before writing the Chrome native host, and lists what is left for you; answer
no for now if you only want this tutorial.

Confirm it worked:

```bash
blowhorn --help
```

You will see the command list. That list is the whole tool - every capability
is one of those subcommands.

Blowhorn keeps its queue, schedule and profiles in your account, so before it can read anything it needs the connection. On a machine that is already set up that is two commands; either way, `blowhorn store` then
opens the tunnel and reports rung by rung:

```bash
blowhorn store --import
blowhorn store
```

Connect to your account covers a machine
without that checkout. Nothing below works until `blowhorn store` ends in
`store usable`.

## 2. See who Blowhorn can act as {#section-2-see-who-blowhorn-can-act-as}

Blowhorn acts as a *profile*: a directory under `data/profiles/` holding one
identity's credentials and browser session.

```bash
blowhorn profile list
```

Now ask what each of them is actually set up to do:

```bash
blowhorn profile status
```

This opens no browser and calls no platform; its one read beyond your
checkout is your account's credentials. What it reports rests on one rule worth knowing
now: a profile may act on a platform when a **credential** for that platform
exists in your account, and never because a handle appears in its roster row.
That is deliberate - [Eligibility](/docs/explanation/eligibility/) explains why.

## 3. Look at the queue without touching it {#section-3-look-at-the-queue-without-touching-it}

Blowhorn posts what is waiting in the content queue. Ask what a run would
pick up right now:

```bash
blowhorn post --check-queue
```

Nothing is published and nothing is written back - this command only reads,
opens no browser and contacts no platform. You will see the pending rows for
each profile in scope.

Narrow it to one profile and one platform:

```bash
blowhorn post --check-queue --profile alex --platform linkedin
```

## 4. Rehearse a real run {#section-4-rehearse-a-real-run}

Now run the posting command itself, in rehearsal mode:

```bash
blowhorn post --profile alex --dry-run
```

Watch what it prints. It resolves the profile, selects rows, opens the flow
for each one, and reports what it *would* have published - then stops. The
rows are not marked done, so the same rows are still pending afterwards.
Confirm that:

```bash
blowhorn post --check-queue --profile alex
```

The same rows are still there. Nothing you have done so far has changed
anything outside your terminal.

## 5. Slow it down {#section-5-slow-it-down}

Blowhorn paces itself to look human. You can make it slower:

```bash
blowhorn post --profile alex --pace slow --dry-run
```

`--pace` is global - it works before or after the command word - and takes
`fast`, `normal` or `slow`.

## What you did

You installed Blowhorn, saw which identities it can act as and why, inspected
the posting queue read-only, and rehearsed a full posting run without
publishing. Everything you ran was safe by construction: `--check-queue` only
reads, and `--dry-run` stops before it publishes.

## Next

- [Post content](/docs/how-to/publish/post-content/) - when you are ready to publish for
  real.
- [Manage the content queue](/docs/how-to/publish/manage-the-content-worksheet/) -
  putting rows in the queue.
- [CLI reference](/docs/reference/cli/) - every command and flag.
