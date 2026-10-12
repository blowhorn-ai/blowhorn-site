---
title: "Add a profile"
description: "Create a profile from the desktop app or the command line."
weight: 60
draft: true
aliases: [/docs/how-to/add-a-profile/]
---

# Add a profile

A profile is one voice you post as. Create one from the desktop app or from
the command line.

**Early access:** creating a profile resolves the person against a Blowhorn account, and customer onboarding for that account is not open yet.
This page stays a draft until it is.

A profile is two halves. The directory `profiles/<name>/` holds
`config.yaml` and the per-profile data; the row in the store's profiles is
what every job reads to select it. Creating a profile writes both, the row
first. A profile with a directory and no row looks healthy in
`blowhorn profile list`, but no job can reach it. What each half holds is
in the [Profile reference](/docs/reference/profiles/).

## Before you start

- The store must be reachable. With the store down the create is refused
  (exit 3) and nothing is written on either side, not even the directory.
  Check with `blowhorn store`, or the Setup screen's store row in the
  desktop app.
- The person needs an account in your organization, and you need its email.
  A profile is never created without one: there is no `--force` and no
  placeholder. If no account holds the email, create the account first.

## From the desktop app

1. Open **Profiles** and click **add profile**.
2. Fill in the name, the email (required: it finds the account) and any
   handles you know.
3. Click **create profile**.

When no account holds the email, the refusal is shown inline; create the
account and try again. When several accounts hold it, the form lists them
and asks which one this profile is; choosing one and clicking **create
profile** again sends that account's id through.

## From the command line

```bash
blowhorn profile set sam --create EMAIL=sam@example.com
```

`EMAIL` is required: it is how the account is found (exact,
case-insensitive). Add the handles you know in the same command:

```bash
blowhorn profile set sam --create EMAIL=sam@example.com \
  LI_PROFILE_URL=https://www.linkedin.com/in/sam/ X_USERNAME=samposts \
  RDDT_USERNAME=sam_r BLUESKY_HANDLE=sam.bsky.social GH_USERNAME=samgh
```

The reply names the account the profile is bound to. Passwords and tokens
are set afterwards with a plain `blowhorn profile set sam KEY=VALUE`.

Rehearse with `--dry-run`: it touches neither the store nor the disk, and
it still refuses everything a real run would refuse.

### When the email cannot decide

Two refusals name `--subject <uuid>` as the way through:

- **No account holds the email.** Create the account first, or, when the
  profile's address legitimately differs from the account's, name the
  account with `--subject`.
- **Several accounts hold the email.** The refusal lists their ids and
  names; pick one and pass it as `--subject`.

`EMAIL` stays required with `--subject`. It is refused when it names no
live account, and refused when the email resolves unambiguously to a
different account: binding a profile to the wrong person is the failure
worth a refusal.

### Refusals that mean a conflict

- **The email already belongs to another profile**: one person, one
  profile. Use the existing one.
- **The name is held by another profile**: pick another name.

Re-creating your own deleted profile with the same name revives its row.
Any handle left blank in the file is never read as "clear it".

## Register a profile that exists only locally

A directory created before profiles had rows, or restored from a trash
copy, needs a row before any job can select it:

```bash
blowhorn profile set sam --register
```

`--register` resolves the person exactly as `--create` does, scaffolds
nothing, and is safe to run again. The directory is the profile's
identity, so a `config.yaml` whose `PROFILE` names something else, or is
empty or missing, is refused; fix the file, or pass `PROFILE=sam`.

## Delete a profile

```bash
blowhorn profile delete sam --yes
```

The command retires the profile's row first, then moves `profiles/sam/`
aside. With the store unreachable the delete is refused and nothing moves.

## Related

- [Sign in](/docs/how-to/set-up/sign-in/) - sign in before profiles mean anything.
- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - give
  the profile its Chrome.
- [Sign a profile in to each platform](/docs/how-to/set-up/platform-accounts/) - the sessions
  and credentials each platform needs.
- [Profile reference](/docs/reference/profiles/) - what each half of a
  profile holds.
