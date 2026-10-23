---
title: "Create a Blowhorn account"
description: "Create your Blowhorn account, or sign in, from the desktop app's setup."
weight: 34
---


Your Blowhorn account lives in [Blowhorn](https://cloud.blowhorn.ai). The app's **Sign in** step has
two buttons:

- **Sign in:** opens your browser to sign in to an account you already have.
- **Create account:** opens your browser so you can sign up.

Either way, Blowhorn then asks whether to allow the app to sign in as
you; choose **Allow**. The browser tab then says Blowhorn received the
answer: close it and return to the app, where the step has ticked off. The
app never sees your password.

## How Create account works today

- **Your browser opens Blowhorn's sign-in page:** choose **Sign up** there.
  The sign-up page can't send you back to the app yet, so the app starts
  from the sign-in page, which can.
- **Google and GitHub work too:** they always run in your browser.
- **Nothing to copy or paste:** when sign-up finishes and you choose **Allow**,
  It hands you back to the app and the step ticks off.
- **Signing up with an email address adds a step:** Blowhorn sends you a
  verification email, and you choose **Allow** after you follow its link.
  The wait for a sign-up is ten minutes, twice the sign-in wait. If the
  wait runs out anyway, your account is kept: verify your email, then
  sign in. You do not need to create the account again.

From the command line, `blowhorn auth login --sign-up` does the same thing.
