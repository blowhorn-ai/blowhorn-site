# System requirements


> What your computer needs to run Blowhorn: macOS, Google Chrome, the compatibility matrix, and a Blowhorn account.



What your computer needs before you install Blowhorn. Requires macOS 13
or newer and Google Chrome 142 or newer.

| Need | Requirement | Checked by |
|---|---|---|
| macOS | 13 or newer, Apple silicon or Intel (one universal build) | The desktop build declares the floor (`minimumSystemVersion` 13.0). Guided setup does not check the macOS version |
| Google Chrome | 142 or newer, the real Google Chrome (not Chromium, not Chrome for Testing), installed, opened once, and signed in | Guided setup, before the welcome; `blowhorn chrome status` |
| Engine | Bundled in the app, with its own Python; nothing to install | Setup, "Blowhorn folder" and "helper tools" rows |
| Account | A Blowhorn account your profile belongs to | Setup, "organization connection" row; `blowhorn store` |
| Background runs | The background service, registered from the app | Setup, "this computer on duty" row |

macOS 13 is the floor the desktop build declares
(`minimumSystemVersion: 13.0`), and every release is one universal DMG
(`Blowhorn-<version>-universal.dmg`) for Apple silicon and Intel Macs.
The engine underneath also runs on Linux; the desktop app needs a Mac.
The supported desktop is the Mac app. Windows is a preview for 64-bit
Windows 10 or 11, described in the matrix below.

## Compatibility matrix

Floors, recorded Chrome versions, per-feature Chrome minimums, the DevTools
protocol pin, and the Windows preview.

### Floors

| Floor | Requirement |
|---|---|
| macOS | 13 or newer, Apple silicon or Intel, one universal DMG. Declared as `minimumSystemVersion` 13.0 |
| Google Chrome | 142 or newer. Real branded Google Chrome only: not Chromium, not Chrome for Testing |

Chrome 142 is the product floor, not an extra feature row. Trusted input
into a Blowhorn tab that is not selected needs
`Emulation.setFocusEmulationEnabled`. From Chrome 142 the page reports
visible and focused. The floor was measured on 2026-10-21 on signed Google
Chrome 142.0.7444.176, and the same day on signed Google Chrome
145.0.7632.160. Chrome for Testing builds used below the floor are not
product quality evidence. One check failed on every build in that
measurement, including installed Chrome 155: the dedicated attach Chrome's
`webdriver` reading. The same check failed in the Chrome 158 run below.

### Tested Chrome

The quality lane is pinned to Google Chrome 155. Recorded branded Google
Chrome quality runs cover 155 through 158, most recently 158.0.8127.36 for
the combined quality suite. They do not cover every release from 155
through 158.

| Chrome | When | Blowhorn | What ran |
|---|---|---|---|
| 155.0.8059.80 | 2026-10-17 to 2026-10-18, macOS | 1.22.0, 1.23.1 | live suites |
| 155.0.8059.84 | 2026-10-30 to 2026-10-31, Linux | 1.64.0 | smaller suites |
| 156.0.8078.48 | 2026-10-28 | 1.41.0, 1.42.0 | narrow live suites |
| 156.0.8078.74 | 2026-11-02 | 1.85.0, 1.87.0 | pair-tab-close |
| 157.0.8103.52 | 2026-11-23 | 2.13.0, 2.14.0, 2.14.1 | attach-chrome |
| 158.0.8127.36 | 2026-11-20 | 2.11.0 | combined quality suite: 34 passed, 1 failed |

The Chrome 158 row is the most recent combined quality suite. Its one
failure is the dedicated attach Chrome's `webdriver` reading, the same
check that failed on every build in the 2026-10-21 floor measurement,
including installed Chrome 155. The Chrome 157 row is a later, narrower
attach-chrome run. No newer quality record than these rows is in this set.

### Per-feature Chrome minimums

Only Chrome minimums Blowhorn enforces or relies on, above the 142 floor.

| Feature | Chrome | What it means |
|---|---|---|
| Split view (`split_view`, `--window split-view`) | 155 | Uses `chrome.tabs.create` with `splitWithTabId`. On older Chrome, or when the split cannot be made, Blowhorn uses its own window (`own_window`) |
| `Target.createTarget` parameter `focus` | 146 | Chromium added this experimental parameter at commit position r1573508 (2026-01-23). It shipped in Chrome 146, stable on 2026-03-10. Blowhorn sends `focus: false` with `background: false` so a foreground tab can open without raising the Chrome window. Product code does not gate on Chrome 146. Chrome 142 to 145 lack the parameter. An unknown parameter may be ignored by older Chrome. That has not been confirmed on a live Chrome 142 to 145 |

`Extensions.loadUnpacked` needs Chrome 137 or newer, already below the
floor, so it is not a row here. No other command Blowhorn sends has a
Chrome minimum above 142.

### DevTools protocol pin

The Chrome DevTools protocol vocabulary is pinned to
[ChromeDevTools/devtools-protocol](https://github.com/ChromeDevTools/devtools-protocol)
revision r1756183 (commit `ce722882bee61612660eb40f513fca67585890da`),
protocol version 1.3, from `browser_protocol.json` and `js_protocol.json`,
read 2026-11-27.

That revision is Chromium trunk, around Chrome 160, not a shipped Chrome
release. On 2026-11-27 trunk builds were about 160.0.8188 (r17563xx) and
Chrome stable was 158 (revision r1727472). The product minimum stays
Google Chrome 142.

### Windows preview

The supported desktop is the Mac app. A Windows preview exists for 64-bit
Windows 10 or 11. It is a test build for a few people. Install steps are
in [Install the Windows preview](/docs/how-to/set-up/install-on-windows-preview/).
The engine also runs on Linux. The desktop app needs a Mac.

Install the real Google Chrome the normal way and sign in before you map
anything; how Blowhorn finds Chrome is in the
[Chrome reference](/docs/reference/chrome/#requirements). Tested versions and the
protocol pin are in the matrix above.

The app carries its engine and Python, so your computer needs no git and no
Python. A contributor running the engine from a checkout instead needs
Python 3.14, the floor `tools/install.sh` enforces and the only supported
version. Either way the Setup screen checks the engine, so a broken engine
or interpreter shows up there first, not mid-run.

Network access to your account is required for the content queue, the schedule, profiles, and run history. Your account keeps those in sync; your computer holds the app, the engine, and your Chrome sessions.
Offline behavior is a plans question, not a requirements one: see
[Plans and limits](/docs/reference/plans/).

## Related

- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) - what the Setup screen checks.
- [Plans and limits](/docs/reference/plans/) - what "free during early access" covers.
- [How Blowhorn works](/docs/explanation/how-it-works/) - why your account and the app are separate.
- [Install the Windows preview](/docs/how-to/set-up/install-on-windows-preview/) - the test build for 64-bit Windows 10 or 11.
- [Chrome reference](/docs/reference/chrome/) - how Blowhorn finds Google Chrome.

