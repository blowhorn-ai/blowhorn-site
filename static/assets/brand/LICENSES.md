# Licences for the assets in this directory

## Brand assets (`logo/`, `mascot/`, `marketing/`, `tokens.json`)

The Blowhorn name, the Crowhorn mark, the Blowhorn wordmark, Major Blowhorn and
the marketing art are copyright Layer5, Inc. They are published here for the
site's pages and, with the downloadable kit on the Brand page (`/brand/`), so
press, partners and the community can refer to Blowhorn. They are not licensed
for use in anyone else's product names, logos or marks. The files are byte-identical copies of version 1 of
the brand kit (`brand/` in the Blowhorn product repository, landed as
PR #354). Never recolour, outline, shadow or rotate the mark; see the brand
book for the rules.

The locked-6 Major Blowhorn cutout (`mascot/locked-6/major-6-hat-left.png`) is the
product repository's `marketing/cast/major-blowhorn/cutouts/major-6-hat-left.png`,
copied unchanged; the `.webp` beside it is
a lossy re-encode of that file for the home page hero, with no other change.

Old Thunderlung (`mascot/thunderlung/`, PNG and WebP) is the product repository's
`marketing/cast/major-blowhorn/thunderlung/brand-style/` cutouts of Major's bugle,
with and without its red cord, approved 28 Oct 2026 and copied unchanged.

The two kits on the Brand page (`/brand/blowhorn-brand-kit.zip` and
`/brand/blowhorn-logo-kit.zip`) are built by the product repository and published
unchanged, under the same terms. They carry no font files: the full kit's
README links the three families on Google Fonts.

The cast art (`cast/*.webp`) is 960x540 re-encodes of the cast locked on 18 Oct 2026
(`marketing/cast/` in the product repository), unchanged otherwise, plus the four
machine Recruit Chicks (`cast/recruit-chick-macbook`, `-imac`, `-laptop-lap` and `-mac-studio`) added on
20 Oct 2026. The `cast/icons/*.webp` files are square crops of the same art with the black ground keyed out. `cast/major-6-hat-left-horn.webp` is the locked
`major-6-hat-left` art with three Caribbean Green (#00D3A9) sound arcs added at the
bullhorn; Major himself is not redrawn.

## Fonts (`fonts/`)

All three families are licensed under the SIL Open Font License, Version 1.1
(`fonts/OFL.txt`). The woff2 files were produced from the upstream variable
masters published in [google/fonts](https://github.com/google/fonts) with
fontTools: Bricolage Grotesque keeps its `opsz` and `wght` axes with the
`wdth` axis pinned to 100; the Instrument Sans and JetBrains Mono files are
static instances at the weights `tokens.json` names.

- Bricolage Grotesque: Copyright 2022 The Bricolage Grotesque Project Authors
  (https://github.com/ateliertriay/bricolage)
- Instrument Sans: Copyright 2022 The Instrument Sans Project Authors
  (https://github.com/Instrument/instrument-sans)
- JetBrains Mono: Copyright 2020 The JetBrains Mono Project Authors
  (https://github.com/JetBrains/JetBrainsMono)

## Platform logos (`../platforms/`)

The site shows each platform's own published logo, unmodified, so readers
recognize the platforms Blowhorn works with. The files in
`static/assets/platforms/` are byte-identical copies of what each owner
publishes, downloaded on 9 October 2026. They are never recoloured, redrawn,
cropped, outlined or animated; each sits alone on a white tile with the
platform's name as its label, and the home page, docs landing and footer
carry the trademark line below.

| File | Owner | Source |
| --- | --- | --- |
| `linkedin-in-bug.png` | LinkedIn Corporation | `LI-In-Bug.png` from `in-logo.zip`, https://brand.linkedin.com/downloads (guidelines: https://brand.linkedin.com/in-logo) |
| `x-logo-black.png` | X Corp. | `logo-black.png` from https://about.x.com/content/dam/about-twitter/x/brand-toolkit/x-logo.zip (toolkit: https://about.x.com/en/who-we-are/brand-toolkit) |
| `reddit-logo.png` | Reddit, Inc. | `Reddit_Logo.png` from the Reddit brand page, https://redditinc.com/brand (brand system: https://redditbrand.lingoapp.com/s/Logo-d9x3n2/) |
| `hacker-news-y18.svg` | Y Combinator | `y18.svg` as served by https://news.ycombinator.com/ (no published logo kit) |
| `slack-mark.svg` | Slack Technologies, LLC (Salesforce) | The Slack mark slack.com serves, https://a.slack-edge.com/9cc0056/marketing/img/nav/logo.svg (media kit: https://slack.com/media-kit) |
| `bluesky-butterfly-blue.svg` | Bluesky Social, PBC | `bluesky_media_kit_logo_transparent_1.svg`, https://bsky.social/about/support/icons (guidelines: https://bsky.social/about/support/branding) |
| `github-invertocat-black.svg` | GitHub, Inc. | `SVG/GitHub_Invertocat_Black.svg` from https://brand.github.com/GitHub_Logos.zip (guidelines: https://brand.github.com/foundations/logo) |
| `youtube-simple-icons.svg` | Google LLC | `icons/youtube.svg` from Simple Icons (https://simpleicons.org, CC0 1.0), downloaded on 13 October 2026, unmodified. A monochrome rendering of the owner's mark, used until the owner's own file replaces it |
| `instagram-simple-icons.svg` | Meta Platforms, Inc. | `icons/instagram.svg` from Simple Icons (https://simpleicons.org, CC0 1.0), downloaded on 13 October 2026, unmodified. A monochrome rendering of the owner's mark, used until the owner's own file replaces it |
| `tiktok-simple-icons.svg` | ByteDance Ltd. | `icons/tiktok.svg` from Simple Icons (https://simpleicons.org, CC0 1.0), downloaded on 13 October 2026, unmodified. A monochrome rendering of the owner's mark, used until the owner's own file replaces it |
| `facebook-simple-icons.svg` | Meta Platforms, Inc. | `icons/facebook.svg` from Simple Icons (https://simpleicons.org, CC0 1.0), downloaded on 13 October 2026, unmodified. A monochrome rendering of the owner's mark, used until the owner's own file replaces it |
| `google-chrome-logo.svg` | Google LLC | `chrome-logo.svg` from https://www.google.com/chrome/static/images/chrome-logo.svg, downloaded on 21 October 2026, unmodified |

LinkedIn, X, Reddit, Hacker News, Slack, Bluesky, GitHub, YouTube, Instagram, TikTok, Facebook and Google Chrome are trademarks of
their respective owners. Blowhorn is not affiliated with or endorsed by any of
them. The logos are used only to name the platforms Blowhorn works with, under
each owner's brand guidelines, and are not licensed for any other use.

## Organisation logos (`../orgs/`)

The logo ticker under the home page hero and the testimonial attributions
show the logos of organisations Blowhorn users work at (`data/user_logos.json`
and `data/testimonials.json`). The original set of 22 was supplied by the
Blowhorn team on 25 October 2026 (dropped in the repo as `user-logos/`) and replaced the previous set the same day. The
files are the owners' logos with one uniform treatment applied before
publishing, so the strip reads as one set: converted to grayscale, each
canvas or viewBox trimmed to the drawn art (full-canvas background shapes
removed), and the five white lockups (Apptega, Aqueduct, Clutch, Innovacare,
Northwinds) stored inverted, so the set reads dark on the light ground at
one height. The logos render bare, with no plate or tile behind them; in
dark mode the strip and theme-following testimonial cards invert the logos
by CSS. Paper cards keep their light ground and do not invert the logos. No
logo is redrawn, outlined or re-proportioned; aspect ratios are the owners' own.

| File | Owner | Source |
| --- | --- | --- |
| `airtex.svg` | Airtex | Team-supplied set, 25 October 2026 |
| `apptega.webp` | Apptega, Inc. | Team-supplied set, 25 October 2026 |
| `aqueduct.png` | Aqueduct | Team-supplied set, 25 October 2026 |
| `ascension.svg` | Ascension | Team-supplied set, 25 October 2026 |
| `bigcommerce.svg` | BigCommerce | Team-supplied set, 25 October 2026 |
| `caritas-argentina.svg` | Caritas Argentina | Team-supplied set, 25 October 2026 |
| `clutch.svg` | Clutch | Team-supplied set, 25 October 2026 |
| `designer-shoe-warehouse.svg` | Designer Shoe Warehouse | Team-supplied set, 25 October 2026 |
| `evercraft.svg` | Evercraft | Team-supplied set, 25 October 2026 |
| `gamestop.svg` | GameStop | Team-supplied set, 25 October 2026 |
| `horstmann.svg` | Horstmann | Team-supplied set, 25 October 2026 |
| `hydroxydase.svg` | Hydroxydase | Team-supplied set, 25 October 2026 |
| `innovacare.svg` | Innovacare | Team-supplied set, 25 October 2026 |
| `kahlua-surfing.svg` | Kahlua Surfing | Team-supplied set, 25 October 2026 |
| `laufenn.svg` | Laufenn | Team-supplied set, 25 October 2026 |
| `luar-music.svg` | Luar Music | Team-supplied set, 25 October 2026 |
| `nextlevel.webp` | NextLevel | Team-supplied set, 25 October 2026 |
| `northwinds.svg` | Northwinds | Team-supplied set, 25 October 2026 |
| `opencart.svg` | OpenCart | Team-supplied set, 25 October 2026 |
| `pediatric-partners.svg` | Pediatric Partners | Team-supplied set, 25 October 2026 |
| `rai-sport.svg` | Rai Sport | Team-supplied set, 25 October 2026 |
| `university-of-nottingham.svg` | The University of Nottingham | Team-supplied set, 25 October 2026 |
| `suburban-propane.webp` | Suburban Propane Partners, L.P. | https://investor.suburbanpropane.com/images/logo.png (owner's investor-site header, https://investor.suburbanpropane.com/) |
| `wawa.webp` | Wawa, Inc. | https://cdn.phenompeople.com/CareerConnectResources/WAWWAWUS/images/2020_WawaLogo_RGB-1718209550627.png (owner's careers-site header, https://careers.wawa.com/) |
| `quiktrip.svg` | QuikTrip Corporation | https://www.quiktrip.com/app/themes/quiktrip/public/images/qt-logo-transparent.svg (owner's site header, https://www.quiktrip.com/) |
| `vayner-media.webp` | VaynerMedia, LLC | PNG embedded in https://vaynermedia.com/wp-content/themes/vaynermedia/assets/images/vm-logo-white.svg (owner's site logo, https://vaynermedia.com/) |
| `rive.svg` | Rive, Inc. | https://framerusercontent.com/images/CmpP37tfaDkGdDPeW4w9jr54aEw.svg (owner's site header, https://rive.app/) |
| `c4-energy.webp` | Nutrabolt (Woodbolt Distribution LLC) | https://cellucor.com/cdn/shop/files/C4OTG_0990_Video_Logos_Powerlifting_BlackLogo_2.png?v=1684342695 (owner's C4 Energy site, https://c4energy.com/) |

The six additions were retrieved from the owners' public sites on 6 November
2026, with the same grayscale and trim treatment. VaynerMedia's SVG contains
a raster PNG, stored here as lossless WebP and inverted from white to dark.
Rive's white monogram is also stored inverted. C4's solid yellow canvas was
removed; the mark and its antialiased silhouette were retained. Wawa was
reduced from 3042px to 1200px wide. No shapes or proportions were redrawn.
Apptega reuses the original team-supplied file, unchanged.

Three quoted companies remain text-only pending permission review:

- Roblox restricts general and commercial logo use: https://en.help.roblox.com/hc/en-us/articles/115001708126-Roblox-Name-and-Logo-Community-Usage-Guidelines
- Meta requires approval for all logo use: https://www.meta.com/brand/resources/meta/company-brand/
- Google excludes business marketing from its general logo-use guidance: https://about.google/brand-resource-center/brand-elements/

These source records do not establish press-use clearance, a partnership,
or a grant of trademark rights.

The names above are trademarks of their respective owners. Blowhorn is
not affiliated with or endorsed by any of them. The logos name the
organisations of Blowhorn users and are not licensed for any other use.

## Alternate storybook style (/home-alt/)

- Fraunces (`static/assets/alt-style/Fraunces-Variable.woff2`): Copyright 2018 The Fraunces Project Authors, SIL Open Font License 1.1 (`static/assets/alt-style/OFL-Fraunces.txt`).
- The illustrations in `static/assets/alt-style/` are original Blowhorn artwork.

## Alternate oil-painting style (/home-oil/)

- The paintings in `static/assets/oil-style/` are original Blowhorn artwork. Sources and the prompts log live in the blowhorn repository, `marketing/brand/oil-style/`.
- The page reuses Fraunces from `static/assets/alt-style/` (SIL Open Font License 1.1).
