---
title: "Check that onboarding still finishes"
description: "Run the onboarding happy path against the built app before a release."
weight: 36
---


`make onboarding-e2e` walks the desktop app's first-run wizard from Create
account through a dry run of the first post. It uses the app you just built
(`desktop/out`), a local stand-in for the Blowhorn service, and a throwaway Chrome
profile. It does not sign in to a social platform, and it does not open your
own Chrome profile.

The throwaway home is seeded from the same `.blowhorn.yaml` a packaged app
seeds, then given a `postgres` backend. That is the file an older install
left behind. The walk reaches the console only when the engine opens Cloud
anyway. In the app, Activity shows the draft and Routines runs a preview-only
check. A `blowhorn post --dry-run` then reports the fixture row without
publishing it.

Build the app first, from `desktop/`, with the electron-vite build, and build
it again after a pull, a rebase or any edit under `desktop/src`. The check
launches whatever is in `desktop/out` and refuses to start when that build is
older than its source, naming the newer file. Then, from the checkout:

```bash
make onboarding-e2e
```

The check needs Node.js 22, Google Chrome, and a display. On Linux with no
display it starts Xvfb itself. It finds the Electron binary the way the
`electron` package does, so the Linux binary and the macOS app inside
`Electron.app` both start. A packaged Mac app is the same walk:

```bash
node desktop/scripts/onboarding-e2e.mjs --app /path/to/Blowhorn.app
```

Each step prints its name. A failure names the step and leaves a screenshot
of that screen in the temp directory the script prints at the start. If the
local Cloud stand-in raises, the check stops and prints that error. Pass
`ONBOARDING_E2E_ARTIFACTS` when you want those screenshots in a directory you
choose.

A desktop release runs this check after the app is built and before it
packages the DMG. The verify phase runs it again with `--app` pointed at
the app inside the mounted DMG. A broken onboarding stops the release there.
The same script is what `make onboarding-e2e` runs.

A program the check starts opens the sign-in URL. Your default browser
stays closed, including on macOS.

On macOS the Chrome for this check is launched with a throwaway
`--user-data-dir` under the system temp directory, `--use-mock-keychain`,
and `--password-store=basic`. A user-data directory outside that temp
directory is refused. If branded Chrome cannot load the unpacked extension,
the check uses a cached Chrome for Testing build. The check also sets
`BLOWHORN_KEYCHAIN=0`, so the engine keeps the fixture token in the
throwaway home and does not write the login keychain.
