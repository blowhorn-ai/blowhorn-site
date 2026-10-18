---
title: "Fix Blowhorn when its engine won't start"
description: "What to do when the menu-bar popup says Blowhorn's engine couldn't start or isn't responding."
weight: 196
---

The Blowhorn app carries its own engine, the part that runs your jobs and
posts. You never need a copy of Blowhorn's code or anything else installed
for it. When the engine can't run, the menu-bar popup shows one line saying
what to do next. The info button beside it has the details.

## "Move Blowhorn to Applications, then open it again"

Blowhorn is running straight from its disk image, or from a temporary copy
macOS made because the app was opened from Downloads. The engine needs a
permanent place, so it does not start from there.

1. Quit Blowhorn.
2. Drag Blowhorn to the Applications folder.
3. Open it from Applications.

## "Blowhorn's engine couldn't start"

1. Quit Blowhorn from the popup's power button, then open it again.
2. If the line comes back, download Blowhorn again from the
   [releases page](https://github.com/layer5io/blowhorn-site/releases) and
   drag it to Applications, replacing the old copy. Your settings and data
   live outside the app, so they are kept.

An older Blowhorn looked for a copy of Blowhorn's code in your home folder
and said "engine unavailable" when it found none. Current versions never
look for one. If you still see that message, update Blowhorn. See
[Update Blowhorn](/docs/how-to/manage/update-blowhorn/).

## "Blowhorn's engine isn't responding"

The engine started but did not answer. Press the refresh button at the top of
the popup. If that doesn't help, quit Blowhorn and open it again.

## Related

- [Troubleshooting](/docs/how-to/troubleshoot/troubleshooting/) - start from the symptom.
- [Update Blowhorn](/docs/how-to/manage/update-blowhorn/)
- [Install the app](/docs/how-to/set-up/install-the-app/)
