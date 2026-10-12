---
title: "Who can post as whom"
description: "A credential is permission, a handle is not; a Chrome mapping is identity, not permission."
weight: 282
---

# Who can post as whom

Blowhorn decides who may post as whom from one fact: whether the
profile holds the platform's credential. Nothing else grants it.

A handle is not authorization. A username in a roster, a display name
in Chrome, or a follower count says who someone is, never what Blowhorn
may do as them. The roster notices that explain a thin selection are
diagnostics, not gates: nothing in the run treats a listed handle as
consent to post. What each platform's credential is, and where the run
reads it, is [Profile reference](/docs/reference/profiles/).

A Chrome session is not authorization either. Being signed in to a site
in a Chrome profile lets the run act there, but the run still checks
the profile's credential first. A named profile with no credential for
anything in scope stops the run with the reason; `--profile all`
skips such profiles quietly.

A Chrome mapping is identity, not permission. It says which real
Chrome profile the run acts in on this machine, and its refusal checks
run before anything launches or attaches. It never grants, and no
fallback to another profile or folder ever applies when it does not
hold.

One profile is one person's posting identity, created row-first in your account and scaffolded beside it. Creating it resolves the person's email to one Blowhorn account and refuses none-or-several by name,
because two people sharing a posting identity could never be told
apart in the ledger.

## Related

- [Profile reference](/docs/reference/profiles/) - the credential per platform.
- [Platforms](/docs/reference/platforms/) - what each credential unlocks.
- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - the mapping half.
- [Content queue columns and row states](/docs/reference/content-queue/) - the refused blank profile.
