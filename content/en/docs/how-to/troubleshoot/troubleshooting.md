---
title: "Troubleshooting"
description: "Start from the symptom: find the fix for what Blowhorn just told you."
weight: 190
---

# Troubleshooting

Start from what you saw. Each symptom names its fix page.

## A post did not go out, or might have

- **X post NOT sent under the extension driver.** The extension's typing does
  not reach X's editor, so the run stops before anything is typed and tells
  you to rerun with `--chrome-launch persistent`. See [Post to X when it will
  not confirm](/docs/how-to/troubleshoot/x-posting/).
- **The run clicked Post but read nothing after it.** The row says `clicked,
  outcome not read`: check the platform, then clear the date or leave it. See
  [Settle something Blowhorn could not confirm](/docs/how-to/troubleshoot/clicked-not-confirmed/).

## Sign-in problems

- **LinkedIn, X or Reddit says the session expired.** Sign in again in your
  mapped Chrome profile, or run `blowhorn profile auth` for that platform. See
  [Fix a sign-in that stopped working](/docs/how-to/troubleshoot/sign-in-problems/).
- **A CAPTCHA or second factor appears mid-run.** The run stops and hands the
  browser back to you. Complete the challenge by hand, then run again. See
  [Fix a sign-in that stopped working](/docs/how-to/troubleshoot/sign-in-problems/).
- **X sign-in under the extension driver stops at once.** The extension's
  typing does not reach X's form either. Sign in by hand in the tab, or run
  with `--chrome-launch cdp`. See [Fix a sign-in that stopped working](/docs/how-to/troubleshoot/sign-in-problems/).

## Chrome and the extension

- **The extension says not connected, or the versions mismatch.** Re-approve
  the connection after an update, or check which install route is on disk with
  `blowhorn chrome extension-status`. See [Fix the Chrome extension
  connection](/docs/how-to/troubleshoot/extension-connection/).
- **Another run holds the bridge or the profile.** Wait for it, or stop it;
  your rows stay queued. See [Fix the Chrome extension
  connection](/docs/how-to/troubleshoot/extension-connection/).
- **A run refuses an unmapped profile, or asks for an allow dialog you cannot
  see.** Check the mapping, or switch mode for that run. See [Choose how
  Blowhorn reaches Chrome](/docs/how-to/settings/launch-mode/).

## Schedule and store

- **A job did not run.** Ask the row directly: `blowhorn schedule why
  <row>`. See [Find out why a job did not run](/docs/how-to/schedule/why-not-run/).
- **Nothing is claimed on this machine.** You may be paused. See [Pause and
  resume posting](/docs/how-to/schedule/pause/).
- **Every account-backed command exits 3 saying your account is unavailable.**
  Bring your connection back; nothing was claimed and nothing is lost. The
  full story lives in the account-unavailable guide, which ships when the
  customer account path does. Until then: run `blowhorn store` to probe the
  connection now, and `blowhorn schedule status` to read the last tick's view
  of it. It never probes, because the app polls it every 15 seconds.

## Related

- [Find out why a job did not run](/docs/how-to/schedule/why-not-run/) - one row's state in one command
- [Settle something Blowhorn could not confirm](/docs/how-to/troubleshoot/clicked-not-confirmed/) - the held-row procedure
- [Change your defaults](/docs/how-to/settings/defaults/) - pace, excluded profiles, logs
