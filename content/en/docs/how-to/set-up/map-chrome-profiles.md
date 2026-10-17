---
title: "Map Blowhorn profiles to Chrome profiles"
description: "Say which real Chrome profile each Blowhorn profile belongs to on this machine."
weight: 50
aliases: [/docs/how-to/map-chrome-profiles/]
---


Tell Blowhorn which of your real Google Chrome profiles each Blowhorn
profile belongs to on this machine. Every run that drives a browser reads
the mapping first and refuses a profile without one, so mapping is the
one-time setup every browser run depends on.

A mapping is identity, never permission: it does not make a profile
eligible for any platform. Eligibility is credential existence, decided in
your account ([Eligibility](/docs/explanation/eligibility/)).

Nothing in this guide runs a browser. What each command prints and its JSON
shape are in the [Chrome reference](/docs/reference/chrome/). How a run
then reaches Chrome is
[Choose how Blowhorn reaches Chrome](/docs/how-to/settings/launch-mode/):
by default runs drive Chrome through the Blowhorn extension, with no
Attach approval and no launched browser.

## From the desktop app

Each profile on **Profiles** has a **chrome** heading. It names the Chrome
profile the mapping records and whether that mapping holds. **Change** or
**map** opens the Chrome profiles list; a directory mapped to someone else
is disabled. **Confirm** maps the same directory again when Chrome's name
or account has changed. A deleted Chrome profile has no confirm: pick
another.

The Setup screen's **chrome profiles** row reports the same state for every
profile at once.

## Before you start

- Your account is reachable from this machine: `blowhorn store` says so. The
  mapping lives there, keyed by this machine's hostname, so it is the same
  on every terminal and in the desktop app on this machine, and does not
  follow you to another machine.
- The Blowhorn profile is in your account's profiles. `blowhorn chrome
  suggest` lists every profile your account knows; a name missing there cannot
  be mapped.
- Chrome's profile list is readable: `blowhorn chrome profiles` lists it.
  Chrome does not have to be running.

## See what Chrome has

```bash
blowhorn chrome profiles
```

```
chrome profiles (3) in /Users/you/Library/Application Support/Google/Chrome
    directory  name      account                    mapped to (on studio)
    Default    Person 1  -                          -
  * Profile 2  Ada       ada@example.com            -
    Profile 5  Grace     grace@example.com          -
  * last used
```

The **directory** column is the name a mapping records, exactly as printed.
Chrome silently creates a new, empty profile for any directory name it does
not know, so `blowhorn chrome map` refuses a directory that is not in this
list rather than recording it.

## Let Blowhorn propose a mapping

```bash
blowhorn chrome suggest
```

```
chrome mapping proposal for studio (3 profiles); nothing is applied
  profile  directory  name   account             note
  ada      Profile 2  Ada    ada@example.com     name match
  grace    Profile 5  Grace  grace@example.com   name match
  marcus       -          -      -                   none
to apply a row you agree with:
  blowhorn chrome map ada 'Profile 2'
  blowhorn chrome map grace 'Profile 5'
```

A row is proposed when exactly one Chrome profile's display name matches
the Blowhorn profile's name (case and punctuation ignored). Two matches are
named as ambiguous and nothing is proposed; no match is `none`; a profile
that already has a mapping keeps it and says so. The command applies
nothing. Copy the `blowhorn chrome map` line for each row you agree with.

## Map a profile

```bash
blowhorn chrome map ada 'Profile 2'
```

```
mapped profile ada to chrome profile 'Profile 2' 'Ada' (ada@example.com) on studio
```

The command checks three things and refuses with one sentence and exit 1
when any fails: the Blowhorn profile is in your account's profiles (`all` is
every profile, not one, so map each profile by name), Chrome has that
directory, and the directory is not already mapped to another Blowhorn
profile on this machine. Then it records the display name and signed-in
account Chrome shows for the directory and prints what it recorded.

Quote a directory name that contains a space. Add `--dry-run` to run the
checks and record nothing; add `--json` for the recorded row as JSON.

Mapping a profile that already has a mapping replaces it. Mapping it to the
directory it already has refreshes the recorded name and account, which is
how you confirm a profile after Chrome's name or account changed. A
directory still held by a profile you have since deleted is released the
moment you map another profile to it; the command says so.

## Check the mappings

```bash
blowhorn profile status --chrome
```

```
| Profile | Linkedin | X | ... | Chrome              | Notes |
| ada     | valid    | - | ... | Profile 2           |       |
| grace   | -        | - | ... | Profile 5 (drift)   |       |
| marcus      | -        | - | ... | -                   |       |
```

The Chrome column shows the mapped directory and, when its recorded
identity no longer holds, why:

| shown | meaning | what to do |
| --- | --- | --- |
| `Profile 2` | mapped, and the name and account Chrome shows still match the ones recorded | nothing |
| `Profile 5 (drift)` | Chrome now shows a different display name or signed-in account for that directory | check the profile in Chrome, then `blowhorn chrome map grace 'Profile 5'` to confirm the new identity |
| `Profile 5 (missing)` | Chrome no longer has that directory | `blowhorn chrome profiles`, then map the profile again |
| `Profile 5 (unknown)` | Chrome's profile list could not be read, so the identity cannot be checked | `blowhorn chrome status`, then fix what it names |
| `-` | no mapping on this machine | `blowhorn chrome map <profile> <directory>` |

`blowhorn chrome profiles` shows the same thing from Chrome's side, in its
`mapped to` column. A profile whose mapping does not hold is refused by
name: `ERROR` and a non-zero exit when you named the profile, one
`WARNING` line and the walk continues when `--profile all` reached it.
Nothing falls back to another profile or to a Blowhorn-owned folder.

## Remove a mapping

```bash
blowhorn chrome unmap ada
```

Only your account's row goes. Nothing under Chrome's directory is touched, and
the Chrome profile keeps its sessions.

## The Chrome extension in that profile

A mapping does not install the Chrome extension. Chrome keeps an extension
per Chrome profile, and the Blowhorn extension drives only the profile it
is installed in, so install it in every Chrome profile you post from.

## When your account cannot be reached

`chrome profiles`, `chrome map`, `chrome unmap`, `chrome suggest` and
`profile status --chrome` each read your account, so each ends with your account's one named sentence and exit 3 when it is unreachable, even when
Chrome's profile list cannot be read either, because your account is asked
first. `chrome status` never opens your account.

## Related

- [Sign a profile in to each platform](/docs/how-to/set-up/platform-accounts/) - after the
  mapping, the sessions and credentials each platform needs.
- [Chrome reference](/docs/reference/chrome/) - every `chrome` command
  and JSON shape.
- [Eligibility](/docs/explanation/eligibility/) - why a mapping alone
  lets a profile post nowhere.
