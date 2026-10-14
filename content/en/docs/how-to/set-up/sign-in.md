---
title: "Sign in"
description: "Sign in to your organization from the app or the command line."
weight: 32
draft: true
---

# Sign in

Sign in to your organization so Blowhorn knows your plan: how many profiles
you can run and which platforms you can post to.

**Early access:** sign in from the command line or from the desktop app.
Both go through your browser, and the command line keeps the token in the
macOS Keychain.

## From the command line

```bash
blowhorn auth login
```

The command opens Layer5 Cloud in your browser. Sign in there, or create an
account with the page's Sign up link (`blowhorn auth login --sign-up` says
so up front). When you finish,
the browser comes back to Blowhorn and the command:

1. keeps the token: in the macOS Keychain, or elsewhere in a `cloud-token`
   file only you can read, beside `cloud.yaml`. It never prints it.
2. writes your organization and name to `cloud.yaml`, replacing those of
   whoever signed in before.
3. reads your plan once. If your account does not include Blowhorn yet, it
   opens Layer5 Cloud (<https://cloud.layer5.io>) in your browser to start
   using the Blowhorn beta. There is no form to fill in.

If no answer comes back within five minutes, the command stops; run it
again. `blowhorn auth login --dry-run` prints where it would sign you in and
opens, waits for and saves nothing.

Then check what the plan says:

```bash
blowhorn auth status
```

`auth status` reports the token as configured (never its value), the
organization id, and the plan it read. It writes nothing.

A token you export as `BLOWHORN_CLOUD_TOKEN` wins over the saved one.

The saved token is not renewed. When Layer5 Cloud stops accepting it, a
publishing run asks you to sign in: run `blowhorn auth login` again.

On a Mac, after Python is upgraded or Blowhorn's environment is rebuilt, the
Keychain asks once whether `python` may use the saved sign-in. Choose
**Always Allow**; a scheduled run cannot answer that prompt for you.

## From the app

Open `blowhorn://signin`, the link the Blowhorn Chrome extension's **Sign in**
offers. The app opens Layer5 Cloud in your browser; sign in there, or create
an account. `blowhorn://signup` starts the same sign-in for a new account
(see [Create a Blowhorn account](/docs/how-to/set-up/create-an-account/)). Cloud sends you back
to the app, and the app finishes the sign-in.
The token is kept by Blowhorn's command line, never by the app.

If your account has no Blowhorn plan yet, the app opens Layer5 Cloud
(`cloud.layer5.io`) so you can start the beta there.

## Sign out

```bash
blowhorn auth logout
```

Signing out removes the saved token, the organization and name in
`cloud.yaml`, and the cached plan check on this machine. If you exported
`BLOWHORN_CLOUD_TOKEN`, unset it in the shell too. Queued posts and profiles
stay where they are. `blowhorn auth logout --dry-run` lists what it would
remove and removes nothing.

## Related

- [Install the app](/docs/how-to/set-up/install-the-app/) - download and first run.
- [Add a profile](/docs/how-to/set-up/add-a-profile/) - create a profile once you are signed in.
- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) -
  the Setup screen.
