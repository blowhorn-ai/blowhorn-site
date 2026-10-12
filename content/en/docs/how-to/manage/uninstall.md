---
title: "Uninstall Blowhorn"
description: "Remove the app, the service, the extension host and the checkout's build products. macOS only."
weight: 196
aliases: [/docs/how-to/uninstall/]
---

# Uninstall Blowhorn

Remove Blowhorn from your Mac: the background service, the Chrome native host,
the launchers, the desktop app and the checkout's build products. Your data
stays unless you ask for it to go, and your account is never touched.

macOS only. On Linux the command is refused by name and nothing is read or
removed.

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

## Remove Blowhorn and keep your data

```bash
blowhorn uninstall
```

The command removes, in order, reporting each item as `removed`, `not
present`, `not unregistered` or `failed`:

1. **The background service.** Each loaded label is booted out and waited for,
   then its file under `~/Library/LaunchAgents` is removed. A label the app
   registered as its login item is booted out the same way; its Login Items
   entry is unregistered by the app itself in step 5.
2. **The Chrome native host.** The manifests under Chrome's
   `NativeMessagingHosts`, the launchers and the bridge socket beside them.
3. **The every-profile install entries.** The external-extensions file and
   Blowhorn's own entry in the managed policy, removed with the same
   administrator prompt that wrote them; other keys in that file stay.
4. **The launchers.** `~/.local/bin/blowhorn` and the pre-rename shim, when
   they carry the installer's marker. A file there that `install.sh` did not
   write is kept and says so. Pass `--bin-dir` if you installed elsewhere.
5. **The desktop app.** Each bundle first unregisters its own Login Items
   entries, then is removed. A bundle too old to unregister itself is reported
   `not unregistered`, naming the step left to you under System Settings >
   General > Login Items.
6. **The checkout's build products.** The virtualenv (removed only when it
   holds `pyvenv.cfg`), `node_modules/`, `desktop/node_modules/` and `logs/`.

A failed item does not stop the run: everything else is still removed, and
the command exits 1.

Kept at the end, and named: your account connection file, the app's preferences
and engine record, Blowhorn's own Chrome trees, the per-user Library state,
the checkout's `cache/`, and the scheduler pause file.

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

## When the venv is already gone

`uninstall.sh` at the checkout root runs the same code with the system Python
and takes the same flags:

```bash
./uninstall.sh --dry-run
./uninstall.sh
./uninstall.sh --purge
```

## When it refuses

The command removes nothing, in a dry run too, while any of these is running,
and names it: a scheduler tick, a pass of the background service, a run
holding the extension bridge, the desktop app, or run records still waiting
in the local spool for your account. Send those records first:

```bash
blowhorn store --replay-spool --log-dir <log-dir>
blowhorn uninstall
```

When your account will never be reachable again from this machine, give the
records up instead with `blowhorn uninstall --discard-unsynced-runs`, which
asks you to type `discard`. Quit the app or wait for the run to finish, then
run the command again. `blowhorn service status` and `blowhorn chrome
extension-status` show what is running.

## Reinstalling afterwards

A fresh `./install.sh` from the same checkout produces a working install.
Your kept account connection file is picked up as it was.

## Related

- [Keep posting when the app is closed](/docs/how-to/schedule/background-service/) - stop the service before removing it
- [Fix the Chrome extension connection](/docs/how-to/troubleshoot/extension-connection/) - check what is running first
- [Change your defaults](/docs/how-to/settings/defaults/) - log directories the dry run reports on
