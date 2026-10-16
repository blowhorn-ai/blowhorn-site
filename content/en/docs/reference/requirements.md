---
title: "System requirements"
description: "What your Mac needs to run Blowhorn: macOS version, Chrome, and a Blowhorn account."
weight: 210
---

# System requirements

What your Mac needs before you install Blowhorn.

| Need | Requirement | Checked by |
|---|---|---|
| macOS | 13 or newer, Apple silicon or Intel (one universal build) | The build declares the floor; Setup checks the rest |
| Browser | Google Chrome, installed and signed in | Setup, "chrome profiles" row; `blowhorn chrome status` |
| Engine | A Blowhorn checkout with a working Python environment | Setup, "blowhorn checkout" and "python environment" rows |
| Account | A Blowhorn account your profile belongs to | Setup, "store" row; `blowhorn store` |
| Background runs | The background service, registered from the app | Setup, "background service" row |

macOS 13 is the floor the desktop build declares
(`minimumSystemVersion: 13.0`), and every release is one universal DMG
(`Blowhorn-<version>-universal.dmg`) for Apple silicon and Intel Macs.
The engine underneath also runs on Linux; the desktop app needs a Mac.
Windows is not supported.

Chrome must be the real Google Chrome, not Chromium and not a headless
build. Blowhorn drives the Chrome profiles you already use, so install
Chrome the normal way and sign in before you map anything. The extension
needs Chrome profiles to attach to; without Chrome every browser run
refuses before it acts.

Python 3.14 is the floor `tools/install.sh` enforces, and it is the only
supported version. The desktop app carries its own engine check on the
Setup screen, so a broken checkout or interpreter shows up there first,
not mid-run.

Network access to your account is required for the content queue, the schedule, profiles, and run history. Your account keeps those in sync; your Mac holds the app, the engine, and your Chrome sessions.
Offline behavior is a plans question, not a requirements one: see
[Plans and limits](/docs/reference/plans/).

## Related

- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) - what the Setup screen checks.
- [Plans and limits](/docs/reference/plans/) - what "free during early access" covers.
- [How Blowhorn works](/docs/explanation/how-it-works/) - why your account and the app are separate.
