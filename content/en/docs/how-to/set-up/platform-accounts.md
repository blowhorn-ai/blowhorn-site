---
title: "Sign a profile in to each platform"
description: "Browser sign-ins, tokens, and app passwords each profile needs before it can post."
weight: 65
---


One section per platform. LinkedIn, X, and Reddit sign in by hand in your
Chrome; Bluesky takes a handle and an app password; GitHub takes a token;
Hacker News takes a username and password, or a confirmed Chrome session;
Slack takes a captured session.

Do the mapping first
([Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/)):
every browser sign-in below opens in the profile's mapped Chrome.

## LinkedIn, X, Reddit

Each keeps a persistent browser session. Refresh it with `profile auth`.
With the username and password in the profile's `config.yaml`
(`LI_USERNAME` and `LI_PASSWORD`, `X_USERNAME` and `X_PASSWORD`,
`RDDT_USERNAME` and `RDDT_PASSWORD`), the login is attempted for you;
otherwise the browser opens and you sign in by hand.

```bash
blowhorn profile auth --platform linkedin --profile ada
blowhorn profile auth --platform x --profile ada
blowhorn profile auth --platform reddit --profile ada
```

With `--headless` the browser still opens as a background window and only
the automated login is attempted; the manual fallback is skipped. A
CAPTCHA or second-factor challenge always hands back to you: unattended
runs never wait for a person.

LinkedIn can also work from a **confirmed Chrome session** instead of a
stored password: when setup's Confirm troops step found you signed in to
LinkedIn in a Chrome profile and you confirmed it, the profile holds
`LI_CHROME_SESSION` naming that Chrome profile, and runs use the session
in the mapped Chrome profile. If that session signs out, sign in again in
Chrome; there is no password for Blowhorn to fall back to unless you store
one too.

## Bluesky

Log in with a handle and an app password. The pair is stored only when
Bluesky accepts it, so a refused credential is never saved.

```bash
blowhorn profile auth --platform bluesky --profile ada
```

In a terminal it asks for both (the stored handle is the default; a blank
app password keeps the stored one). Supply them without a prompt with
`--handle` and `--app-password-stdin`. Otherwise the stored pair is logged
in with and nothing is written. Make the app password in your Bluesky
account settings; your main password never goes here.

## GitHub

Store a personal access token as the profile's `GH_TOKEN`. It lands in the
profile's GitHub credential in your account, never in `config.yaml`:

```bash
blowhorn profile set ada GH_TOKEN=<token>
```

Then validate it without following or reacting to anything:

```bash
blowhorn profile status --profile ada --check-platform github
```

The check reports the login the token signs in as and its scopes. A
classic token needs `user:follow` to follow and `repo` to react; a
fine-grained token needs read and write on Followers to follow, and on
Issues (and Pull requests for PR targets) to react.

## Hacker News

Store the login with `profile set`. Both keys are needed; the password is
read from your account and never from `config.yaml`:

```bash
blowhorn profile set ada HN_USERNAME=<account> HN_PASSWORD=<password>
```

Or work from a **confirmed Chrome session**: if setup's Confirm troops
step found you signed in to Hacker News in a Chrome profile and you
confirmed it, the profile holds `HN_CHROME_SESSION` naming that Chrome
profile instead of a password, and runs use that session. If it signs
out, sign back in in Chrome, or store a password as above.

Check it landed, with the password shown only as set or not set:

```bash
blowhorn profile get ada
```

## Slack

Capture your signed-in web session into the profile's Slack credential in
your account:

```bash
blowhorn profile auth --platform slack --profile ada
```

A browser window opens; sign in to Slack, and the session is extracted. No
Slack app install is needed. To capture a new workspace, name it:

```bash
blowhorn profile auth --platform slack --profile ada --workspace acme.slack.com
```

Omit `--workspace` to refresh every workspace already listed under
`slack_workspaces` in that credential.

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - the
  mapping every browser sign-in opens in.
- [Post content](/docs/how-to/publish/post-content/) - publish once every platform
  is signed in.
- [Profile reference](/docs/reference/profiles/) - where each credential
  is stored.
- [Eligibility](/docs/explanation/eligibility/) - a credential is
  permission.
- [Requirements](/docs/reference/requirements/) - what each computer needs
