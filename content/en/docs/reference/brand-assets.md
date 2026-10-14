---
title: "Brand assets reference"
---
# Brand assets reference

Where the Blowhorn brand lives in the checkout, which product files carry it,
and the commands that rebuild them. The rules for using the brand are in
[the brand kit](../../brand/README.md).

## The brand kit

[`brand/`](../../brand/README.md) holds version 1 of the identity: the brand
book, [the logo concepts and system](../../brand/logo.md),
[Major Blowhorn](../../brand/mascot.md), [voice](../../brand/voice.md) and the
design tokens in `brand/tokens.json`. `brand/draft/` is the superseded first
exploration.

| Folder | Holds | Rebuilt by |
|---|---|---|
| `brand/logo/` | The Crowhorn system: icon, wordmark, lockups, one-colour files, app icons, favicons, the Layer5 lockup | `make brand-build` |
| `brand/logo/concepts/` | Concepts A to J: symbol, wordmark and lockup each | F to J by `make brand-build`; A to E are archived |
| `brand/logo/textured/` | Placeholders for the oil-paint editions, produced outside the repository | `make brand-build`, until the painted PNG replaces each one |
| `brand/mascot/`, `brand/marketing/` | Interim Major Blowhorn art, the social avatar and banner | Archived; replaced by hand |

`scripts/brand/build-logo.py` draws the marks in code (`marks.py`), outlines
every letter with HarfBuzz and fontTools, and measures and rasterises with
Playwright's Chromium (`svgkit.py`). The four fonts it outlines are vendored in
`scripts/brand/fonts/` under the SIL Open Font License (`OFL.txt`). It needs
the dev requirements (`./venv/bin/pip install -r requirements-dev.txt`) and the
Chromium runtime that `make cli-install` installs.

## Product icons

| File | What it is | Comes from |
|---|---|---|
| `desktop/assets/app-icon.svg` | The macOS app icon master: the Crowhorn on a charcoal tile on Apple's icon grid (824 px inset 100 px) | A copy of `brand/logo/blowhorn-app-icon-macos.svg`, written by `make brand-build` |
| `desktop/assets/app-icon.png` | Its 1024 px render | `make brand-build` |
| `desktop/assets/blowhorn-icon-set/icon-{16..1024}.png` | The app icon at every size | `make desktop-icons-build` |
| `desktop/assets/app-icon.icns` | Those sizes packed for macOS; `electron-builder.yml` reads it | `make desktop-icons-build` |
| `desktop/assets/tray/blowhorn{,Paused,Attention}Template{,@2x}.png` | The menu-bar template glyphs | `make desktop-icons-build`, from 22 px grids in `desktop/scripts/make-icons.py` |
| `extension/icon{16,32,48,128}.png` | The Chrome extension's icons, byte-identical to the icon set | `make desktop-icons-build` |

The menu-bar glyphs are drawn on their own 22 px grid rather than scaled down
from the app icon, and carry state by shape, never by colour:

| State | Glyph |
|---|---|
| live | The Crowhorn in silhouette (mouthpiece, comb, eye, wattle, open bell) with three blast lines |
| paused | The same horn with two pause bars where the blast lines were |
| attention | The live glyph with a dot in the top-right corner |

## Rebuilding

```bash
make brand-build          # brand/logo/, concepts F to J, placeholders, the app icon master
make desktop-icons-build  # icon set, .icns, menu-bar templates, extension icons
```

Chromium measures and rasterises, so a rebuild on another machine can move a
viewBox or a PNG pixel by a hair; review the diff before committing. On macOS
`pnpm icon` in `desktop/` still re-renders the master PNG from the SVG with
QuickLook before running the same icon build.

`tests/test_desktop_icons.py` pins the icon set, the `.icns` and the menu-bar
glyphs; `tests/test_brand_kit.py` pins the brand files the product and the
brand book name.
