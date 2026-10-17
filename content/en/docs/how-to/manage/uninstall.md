---
title: "Uninstall Blowhorn"
description: "Remove the app, the service, the extension host and the checkout's build products. macOS only."
weight: 196
aliases: [/docs/how-to/uninstall/]
---


Remove Blowhorn from your machine: the background service, the Chrome native host,
the launchers, the desktop app and the checkout's build products. Your data
stays unless you ask for it to go, and your account is never touched.

macOS only. On Linux the command is refused by name and nothing is read or
removed.

## A machine that ran Outbox

If the machine still has an install from before the rename to Blowhorn, the
same run retires it too: the `io.layer5.outbox.service` and
`com.outbox.scheduler` LaunchAgents (booted out, then their files removed),
the `com.outbox.chrome_extension` and `com.outbox.actuator` native-host
manifests and their launchers, and `/Applications/Outbox.app`. Outbox's app
state, preferences and caches stay unless you pass `--purge`. Outbox's Chrome
trees under `~/.outbox` are always kept, because they can still be the live
ones until `blowhorn chrome migrate` has moved them. Remove that folder
yourself once you've migrated.

## See what would be removed

Always start with the dry run. It lists everything the installer, the app,
the service and the extension install can leave on this machine, says whether
each is present, and removes nothing:

```bash
blowhorn uninstall --dry-run
```

Each line carries one result, `would remove`, `not present`, `not checked`,
`kept`, `not unregistered`, or `never touched` for your account, with the
path. `not checked` means the item's state could not be read, with the reason;
nothing is done to it, and it is never reported as absent.

The dry run always shows the full list, even when the real run would refuse.
Anything that would stop the real run (the app still open, unsynced run
records) is listed first under "Nothing was removed", and the command exits 1
so a script can tell. Resolve those, then run the real command.

## Remove Blowhorn and keep your data

```bash
blowhorn uninstall
```

The command removes, in order, reporting each item as `removed`, `not
present`, `not unregistered` or `failed`:

1. **The background service.** A loaded `ai.blowhorn.service` is booted out
   and waited for, then its file under `~/Library/LaunchAgents` is removed. A
   label the app registered as its login item is booted out the same way; its
   Login Items entry is unregistered by the app itself in step 5.
2. **The Chrome native host.** The manifest under Chrome's
   `NativeMessagingHosts`, the launcher and the bridge socket beside it.
3. **The every-profile install entries.** The external-extensions file and
   Blowhorn's own entry in the managed policy, removed with the same
   administrator prompt that wrote them; other keys in that file stay.
4. **The launchers.** `~/.local/bin/blowhorn` and `~/.local/bin/blowhorn-axi`,
   when they carry the installer's marker. A file there that `tools/install.sh` did
   not write is kept and says so.
   Pass `--bin-dir` if you installed elsewhere.
5. **The desktop app.** `Blowhorn.app` first unregisters its own Login Items
   entries, then is removed. A bundle too old to unregister itself is reported
   `not unregistered`, naming the step left to you under System Settings >
   General > Login Items.
6. **The checkout's build products.** The virtualenv (removed only when it
   holds `pyvenv.cfg`), `node_modules/`, `desktop/node_modules/` and `data/logs/`.
   For the engine the app carries, the report calls its folder `home/` the
   checkout: its `data/logs/` goes here, and its `venv/` is kept because it holds
   only the app's interpreter link.

A failed item does not stop the run: everything else is still removed, and
the command exits 1.

Kept at the end, and named: your account connection file, the app's state
under `~/Library/Application Support/Blowhorn` (its preferences, its engine
record and, for the engine the app carries, that engine's folder `home/` with
your profiles' settings), Blowhorn's own Chrome trees, the per-user
Library state, the checkout's `data/cache/`, and the scheduler pause file.

The checkout itself (for example `~/code/blowhorn`, with `tools/uninstall.sh` in it)
is never removed, under any flag, and the summary names it. Delete that folder
yourself if you no longer need it. The engine's `home/` is not a checkout:
`--purge` removes it with the rest of the app's state.

The summary ends by saying the shared store was not touched. If your store
connection shows `127.0.0.1` (for example `postgresql://127.0.0.1:9432`), that
is the local tunnel Blowhorn opens to your account's database, not a database
on this machine.

## Remove the local data too

```bash
blowhorn uninstall --purge
```

`--purge` removes the kept list above as well. It shows what it is about to
remove and asks you to type `purge`; anything else cancels and removes
nothing. From a script with no terminal, pass `--yes`. `--json` needs `--yes`
too, because the prompt would otherwise land in the JSON output.

Your account, the content queue, the schedule, the profiles and the
ledgers on it, is not local data and is never touched, under any flag. Other
machines keep using it.

## Without a checkout

An install from the DMG alone puts no `blowhorn` command on your `PATH`. Run
the same command through the engine the app carries, with its own interpreter,
and the same flags:

```bash
BLOWHORN="$HOME/Library/Application Support/Blowhorn/home"
"$BLOWHORN/venv/bin/python" "$BLOWHORN/engine/blowhorn.py" uninstall --dry-run
```

Quit the app before the real run (see [When it refuses](#when-it-refuses));
the engine in that folder still runs with the app closed.

## When the venv is already gone

`tools/uninstall.sh` at the checkout root runs the same code with the system Python
and takes the same flags:

```bash
./tools/uninstall.sh --dry-run
./tools/uninstall.sh
./tools/uninstall.sh --purge
```

## When it refuses

The real run removes nothing while any of these is running, and names it (a
dry run names them too, above its preview): a scheduler tick, a pass of the background service, a run
holding the extension bridge, the desktop app, or run records still waiting
in the local spool for your account. Send those records first:

```bash
blowhorn store --replay-spool --log-dir <log-dir>
blowhorn uninstall
```

When your account will never be reachable again from this machine, give the
records up instead with `blowhorn uninstall --discard-unsynced-runs`, which
asks you to type `discard` (pass `--yes` from a script or with piped input).

If this machine was never signed in to the store (no `~/.config/blowhorn/store.yaml`),
the records can never be sent from here, and `blowhorn store --replay-spool`
fails with "no connection is configured". The refusal says so and points to
`--discard-unsynced-runs`, or to `blowhorn store --import` first if you want
to keep them.

To quit the desktop app, click the Blowhorn icon in the menu bar and choose
**Quit Blowhorn**. Closing the window is not enough: the app keeps running in
the menu bar. Otherwise wait for the run to finish, then run the command again. `blowhorn service status` and `blowhorn chrome
extension-status` show what is running.

## Delete the checkout

When you no longer need Blowhorn, remove the checkout folder yourself, for
example:

```bash
rm -rf ~/code/blowhorn
```

## Reinstalling afterwards

Installing the app again from its DMG, or a fresh `./tools/install.sh` from the
same checkout, produces a working install. Your kept account connection file is
picked up as it was.

## Related

- [Keep posting when the app is closed](/docs/how-to/schedule/background-service/) - stop the service before removing it
- [Fix the Chrome extension connection](/docs/how-to/troubleshoot/extension-connection/) - check what is running first
- [Change your defaults](/docs/how-to/settings/defaults/) - log directories the dry run reports on
