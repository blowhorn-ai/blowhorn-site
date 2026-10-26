---
title: "Profile reference"
description: "What a profile is: a profile in your organization, the list every command reads, its keys per platform, and the Chrome column."
weight: 217
---


A profile is one identity Blowhorn posts as: a profile your organization
holds in your Blowhorn account. Each one has an id, a name, an optional
description, and, unless it is a brand, the member it represents. Its
platform accounts and their credentials are kept in your account too.
This page describes; the steps live in the how-to guides under Related.

## Which profiles exist

Your organization's profile list is the only answer. Every command reads it
once per run and selects from it: `--profile all` is every profile on it
minus the excluded list, and a name you type must match one profile on it,
ignoring case. A name two profiles share is refused until one is renamed.
A folder under `data/profiles/` neither adds a profile nor keeps a deleted
one alive.

`blowhorn profile list` prints the list. With `--json` each item carries
the profile's `id`, `name`, `description`, `userId`, `owner`, and `person`:
the represented member's name and email, or `null` for a brand.

What a run learns about a profile on this computer, such as the last
session check and the X follower history, is kept in
`data/cache/profiles/<profile id>/`. That folder is safe to delete; the
next check or collection writes it again.

## Creating a profile

`blowhorn profile create --payload-stdin` creates a profile in your
organization from a JSON document on stdin holding the fields a person
sets:

| Field | Required | What it is |
|---|---|---|
| `name` | yes | Lowercase letters, digits, `-` or `_`, at most 64 characters, never `all`, and not a name another profile uses |
| `description` | no | What the profile is for, at most 1000 characters |
| `userId` | no | The member the profile represents, as `blowhorn org members` lists them. Leave it out for a brand |

Blowhorn adds your organization, and you own the profile. Any other key,
such as an email, a handle or a credential, is refused, and every refusal
comes before anything is sent. No folder is created and no email is
looked up.

`blowhorn profile update <name-or-id> --payload-stdin` takes the same
document and replaces those three fields. The document is the whole of
them: a description left out is cleared, and a `userId` left out makes
the profile a brand. The profile's run settings (Risk Profile, caps and
quiet hours) are read just before the write and kept as they are, and its
owner does not change.

Both take `--dry-run`, which makes the same checks and sends nothing.
`blowhorn org members` lists the members a profile can represent, with
each one's user id, name and email.

The desktop app's Add profile form and profile detail use the commands
above. The older `blowhorn profile set <name> --create` (or `--register`)
is still in the CLI: it resolves the profile's email to one live Blowhorn
account, writes the row, and then scaffolds a local directory.
`blowhorn profile delete` retires the profile's row and moves its local
directory aside when it has one; a profile with no directory on this
computer, which is every profile created with `profile create`, is
retired and nothing moves.

`blowhorn profile get <name>` prints one profile: its id, description and
the person it represents, the accounts mapped to it, and which fields each
platform's credential holds. A credential field is shown only as set,
never with its value. `blowhorn profile status` reports every profile with
its sessions. `blowhorn profile set <name> KEY=VALUE` writes a platform key
to that platform's credential in your account; an unknown key is refused
by name.

## Credential Loading

Eligibility is credential existence: a profile may post on a platform
exactly when the secret for that platform exists. Handles, sessions in
Chrome, and follower counts grant nothing.

| Platform | Keys |
|---|---|
| LinkedIn | `LI_USERNAME`, and `LI_PASSWORD` or `LI_CHROME_SESSION` |
| X | `X_USERNAME` (password beside it for automated sign-in; `X_APP_KEY`, `X_APP_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET` for the API) |
| Reddit | `RDDT_USERNAME` (password beside it for automated sign-in; `RDDT_CLIENT_ID` and the other `RDDT_*` keys for OAuth) |
| Hacker News | `HN_USERNAME`, and `HN_PASSWORD` or `HN_CHROME_SESSION` |
| Slack | `SLACK_USER_TOKEN`, `SLACK_BOT_TOKEN`, or a captured workspace session |
| Bluesky | `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` |
| GitHub | `GH_TOKEN` |

Every platform reads its credential from your account, and only from
there: a run takes the secret from the same read that decided the profile
may post, and `profile set` writes the keys there. No file on this
computer holds a credential, and a key left in a profile's old local
file is never read. `blowhorn profile auth --platform slack` captures a
workspace session through the run's browser driver and lands it in your
account; no Slack app install is needed. `blowhorn profile auth --platform
bluesky` logs in with a handle and app password and stores them only when
Bluesky accepts them.

LinkedIn and Hacker News also accept a **confirmed Chrome session**
instead of a password: `LI_CHROME_SESSION` and `HN_CHROME_SESSION` name
the Chrome profile directory whose signed-in session the person
confirmed on setup's Confirm troops step. The run then works through
that profile's live session in its mapped Chrome profile. If the session
has signed out and no password is stored, the run says so and stops for
that platform. The session counts toward eligibility only because the
credential row exists - a browser that merely happens to be signed in
grants nothing.

A profile you name that holds no credential for anything in scope stops
the run with the reason naming it. `--profile all` skips such profiles
quietly.

## The Chrome column

Your account row beside each profile carries the Chrome column: which real
Chrome profile this Blowhorn profile acts in on this computer, keyed by
hostname. `blowhorn chrome map` writes it; `blowhorn chrome unmap`
clears it. A browser run with no mapping for its profile refuses
before anything opens, and never falls back to another profile. The
mapping is identity, never permission: it says where the run acts, not
what it may do.

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - write the Chrome column.
- [Platforms](/docs/reference/platforms/) - what each platform acts with.
- [Chrome reference](/docs/reference/chrome/) - the mapping commands and their shapes.
- [`blowhorn org`](/docs/reference/cli/org/) - the members a profile can represent.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
