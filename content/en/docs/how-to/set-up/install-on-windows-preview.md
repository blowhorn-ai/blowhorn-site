---
title: "Install the Windows preview"
description: "Install, update and remove the early Blowhorn build for Windows, and what it does and does not do yet."
weight: 31
---

Install the early preview of Blowhorn for Windows. It is a test build for a
few people: the parts listed below work, and a good deal is not there yet. If
you want the full app today, use a Mac ([Install the app](/docs/how-to/set-up/install-the-app/)).

## Download

Download the preview from the release named **Blowhorn for Windows
(preview)** on the
[blowhorn-site releases](https://github.com/blowhorn-ai/blowhorn-site/releases)
page: the installer (`Blowhorn-<version>-x64-setup.exe`) and its `.sha256`
file. In PowerShell, in the folder you saved them to, check the installer:

```powershell
Get-FileHash .\Blowhorn-<version>-x64-setup.exe -Algorithm SHA256
```

The hash must match the one in the `.sha256` file.

## Install

1. Run the installer. It installs for your user only and asks for no
   administrator password.
2. Windows SmartScreen warns that it does not recognize the app, because the
   preview is signed with our own preview certificate, not yet with a
   publisher certificate. Choose **More info**, then **Run anyway**. You do
   this once per download.
3. Open **Blowhorn** from the Start menu.

The release also carries `Blowhorn-Preview.cer`, the public half of the
preview certificate, if you want to compare its fingerprint with the one in
the release notes. You do not need to import it to install.

Requires 64-bit Windows 10 or 11 and Google Chrome 142 or newer.

## What works in the preview

- Installing and removing the app with no administrator rights.
- The engine's own commands, with no Python on your machine: its version, its
  settings, and what each platform can do.
- Account, profile, schedule and content reads, as the native engine answers
  them. These are built and tested elsewhere and not yet tried against a real
  account on Windows.

## What does not work yet

- Posting to X, LinkedIn, Reddit, Hacker News and Bluesky. A command the
  Windows engine does not answer says so plainly, and changes nothing.
- The background service that runs your schedule when you sign in to Windows:
  it is set up, but the passes it runs are not on Windows yet.
- Connecting the Chrome extension to the app. The connection is registered for
  your user, and has not been tried against Chrome on Windows yet.
- Anything about the app window itself (tray, notifications, screens) that
  nobody has yet checked on a real Windows machine. Tell us what you see.
- Windows Store packaging and a publisher-signed installer.

## Update and remove

To update, run the newer preview's installer over the old one; your data stays
in your Blowhorn account. To remove Blowhorn, open **Settings, Apps,
Installed apps**, choose **Blowhorn** and **Uninstall**. The uninstaller
removes the app and leaves your data folder alone.
