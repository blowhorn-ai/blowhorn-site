---
title: "Install the Chrome extension"
description: "Add the Blowhorn extension from the Chrome Web Store, or load it unpacked during early access."
weight: 40
aliases: [/docs/how-to/install-the-chrome-extension/]
---


Blowhorn drives Chrome through its Chrome extension. Chrome keeps an
extension inside each Chrome profile, and the extension drives only the
profile it is installed in. Install it in every Chrome profile you post
from.

**Early access:** the Chrome Web Store listing is awaiting review. Until it
is approved, load the extension unpacked as described below.

## From the Chrome Web Store

Open the
[Blowhorn listing](https://chromewebstore.google.com/detail/fcflpiagmpcfifgknledeknedfopnapf)
(item `fcflpiagmpcfifgknledeknedfopnapf`) in each Chrome profile you post
from and choose **Add to Chrome**. Write the native host the extension
talks to, then confirm the extension answers:

```bash
blowhorn chrome extension-install
blowhorn chrome extension-status
```

An answered hello means the extension is loaded in some Chrome profile and
talking. The report also lists each Chrome profile with a Web Store
install and its version.

If it says the extension is too old for this Blowhorn, update it: open
`chrome://extensions`, turn on **Developer mode**, and choose **Update**
(or restart Chrome). Do not load it unpacked over a store install.

## Check it from the toolbar

On first install the extension opens the Blowhorn welcome page. Its
toolbar button shows a red **!** until this Chrome profile is ready.
Click it to see what is missing, then follow its one button:

- **Download the Blowhorn app** - the app is not installed.
- **Update the Blowhorn app** - the app is too old for this extension.
- **Finish setup in Blowhorn** - Blowhorn changed in a way that needs the
  guided setup again; opens it in the app. Updating alone never asks for
  it again; it appears only when a new version of Blowhorn needs
  something the earlier setup did not do.
- **Sign in** - opens the app's sign-in.
- **Map this profile in Blowhorn** - opens the app's mapping screen for
  this Chrome profile.

When everything is in place the popup names the linked Blowhorn
profile and signed-in account, and offers **Change mapping**.

## Load it unpacked in one Chrome profile

When only one Chrome profile needs the extension, write the native host and
follow the printed steps. Through the Blowhorn mapping:

```bash
blowhorn chrome extension-install --profile kate
```

By the Chrome profile directory, as `blowhorn chrome profiles` prints it:

```bash
blowhorn chrome extension-install --chrome-profile 'Profile 12'
```

`--chrome-profile` can be given more than once. Either flag with
`--all-profiles` is refused. A `--profile` inherited from
`BLOWHORN_PROFILE` or `defaults.profile` does not count: type it on this
command.

The printed steps are: switch to that Chrome profile, open
`chrome://extensions`, turn on Developer mode, choose **Load unpacked**,
select the `extension/` directory the command names, then check with
`blowhorn chrome extension-status`. There is no file the command can write
that installs an extension in one profile only, so this route always ends
with those clicks.

See the files first, and write nothing:

```bash
blowhorn chrome extension-install --profile kate --dry-run
```

## Every Chrome profile on this machine

**Every profile** (the default) writes Chrome's
`ExtensionInstallForcelist`. Chrome installs the extension the next time
each profile starts, with no click in that profile. That is every Chrome
profile on this machine, including ones no Blowhorn profile uses. Chrome
shows **Managed by your organization**. macOS asks for an administrator
password once. Cancelling that dialog writes nothing.

```bash
blowhorn chrome extension-install --all-profiles
```

**Ask in each profile** writes Chrome's external-extensions file instead, so
Chrome offers the install in each profile and you click once there. There is
no managed banner.

```bash
blowhorn chrome extension-install --all-profiles --external
```

On Linux both files live where only root can write. Blowhorn never asks for
root and refuses to run under `sudo`: a write it cannot make is refused
with the file, its exact content, and the one `sudo` command that writes
that file. Write that file, then run the plain install as yourself for the
host.

## See which route is on disk

```bash
blowhorn chrome extension-status
```

The report includes `Install route: policy`, `external`, or `none`. A
policy line ends `not confirmed in chrome`; an external line ends `waiting
for your click`. Those lines say what Chrome was asked to do, never that a
profile's copy was confirmed.

## From the desktop app

Settings has one **chrome extension** card. The segmented control is the
route: **every profile** or **ask in each profile**. The button stays
**install chrome extension** either way. After the command, the card lists
one row per Chrome profile with the same words the terminal prints.

## Move an install made before the extension id changed

Installs made before the current store item used the retired id
`alogghnpabnbkmhgeceffnlcbcnlpoap`, which has no store listing and never
updates on its own. The native host still accepts that id beside the store id
`fcflpiagmpcfifgknledeknedfopnapf`, so an old copy can connect and tell you it
is out of date. Move it to the store install so Chrome keeps it current:

1. Run the install again with the flags you used the first time.
2. In each Chrome profile that loaded the extension unpacked, open
   `chrome://extensions`, remove the old copy, and choose **Load unpacked**
   again with the `extension/` directory.
3. If you used `--all-profiles`, remove the old id's entry by hand: the
   command adds and removes only the current id.
4. Check with `blowhorn chrome extension-status`.

Your profile mappings (`blowhorn chrome map`) do not name the extension id
and do not change.

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - which
  Chrome profile each Blowhorn profile belongs to.
- [Chrome reference](/docs/reference/chrome/) - the flags, the files, and
  the JSON shapes.
- [Requirements](/docs/reference/requirements/) - what each machine needs
