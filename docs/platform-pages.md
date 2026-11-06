# Platform pages

A platform product page (blowhorn-site#466) shows what Blowhorn does on one
platform, from your own computer: an activity selector and one call to action in the
hero, then **Only on your computer**, a local-action stage that explains how the
extension acts as you in your own signed-in browser. X is the first page, at the
noindex preview route **`/preview/platforms/x/`**.

Read at base `c081f015e8adb977507d85b233658c4ee3956d5a` (master, #491) on 2026-11-06
(America/Chicago) for issue #500, which replaced the setups rail with a carousel.

## Figma delta (intentional)

The X frame in Figma (`mM9B4Zv9ON3pIyh3IvB4Il`, node `902:114`, on the shared contract
`902:111`) is the original draft-centred layout: a draft storyboard in the hero and a
try-on playground as section two. This preview deliberately supersedes it with a
local-action direction, requested by the product owner:

| Figma 902:114 (draft-centred) | This preview (local-action) |
|---|---|
| Hero storyboard of a draft, with write, review, track steps | Hero is copy, activity selector, the extension call to action and a decorative orbit (no draft) |
| Section two: a try-on playground (draft, starters, image picker) | Section two: **Only on your computer**, a stage of three scenes (amplify, follow with a local log, dry fire) |
| No account of what runs on the computer | Reach line from the platform YAML, a diagram of this computer, the extension and the signed-in sessions |

Figma was not edited, and this page does not claim parity with it. The matrix, rules
of engagement, Field Manual and Activities sections are unchanged in content.
Reconcile the frame with this direction before the page leaves preview.

**Setups (issue #500, approved; an intentional delta from 902:114).** The frame's
setups row becomes a carousel: one setup in focus, the next peeking in, a pager and
previous and next controls. The three real setups, their copy buttons and source
links are unchanged.

## Files

| What | Where |
|---|---|
| Shared contract and one record per page | `data/platform_pages.json` |
| Shape | `schemas/platform_page.schema.json` (`make check-schemas`) |
| Joins and build-time guards | `layouts/_partials/platform-page-data.html` |
| Template | `layouts/platform-page.html` |
| Styles, script | `assets/css/platform-page.css`, `assets/js/platform-page.js` |
| Vendored libraries (exact npm release files, sha256-pinned) | `assets/js/vendor/embla-carousel-8.6.0.umd.js`, `assets/js/vendor/motion-mini-14.10.0.js`; notices in `THIRD-PARTY-NOTICES.md` |
| Cutouts (alpha channel only) | `static/assets/brand/cast/icons/` |
| Checks and DOM harness | `.github/scripts/check_platform_pages.py`, `platform_page_harness.js`, `test_platform_pages.py` |
| Page file | `content/en/preview-platform-<id>.md` |

## What is joined, and what is quoted

Facts that exist in the platform YAML are joined, never retyped:

- the reach line (`reach` in `data/platforms/x.yaml`);
- the amplify scene's line (the YAML's `behavior` for amplify);
- the follow scene's line (the YAML's `limits` for follow: 400 a day, 15 in 15
  minutes, counted from that profile's follow log on this computer).

Every other sourced fact quotes a public page verbatim, and the checker fails a
quote the page does not carry: the session boundary sentence
(`/docs/explanation/your-own-chrome/`), the amplify retweet-or-quote line
(`/docs/how-to/publish/amplify-a-post/`), the dry-fire line
(`/docs/reference/use-the-desktop-app/`, "checks the sign-in and stops before
composing"), the rules of engagement and the Field Manual.

## Behavior

### The hero

An activity selector (Post, Respond, Amplify) swaps the intent line and marks the
matrix rows bound to the type. One primary call to action installs the browser
extension from the download page's Web Store link, with nothing under it.

### Only on your computer

- A reach line, then three native radios (Amplify, Follow, Dry fire (desktop)). The first is
  checked at load.
- Each scene shows one text panel. The script hides the others and sets `data-scene`
  on the section, which the CSS reads to draw that scene's diagram (profiles lit,
  per-profile logs, the dry-fire gate).
- Each change plays the diagram once and announces the scene once, from the visitor's
  choice only. Choosing the scene already shown plays nothing. The replay button plays
  the diagram again and announces nothing. `data-pp-run` counts the plays.
- The diagram is decorative (`aria-hidden`), its nodes are HTML so names wrap, and its
  signal lines are one SVG path each (`pathLength`). It appears only once the script
  runs; without script the three panels show as stacked text.
- Motion (the local stage's CSS only): one finite draw of the signal and one fade-in of
  the relay, slips and outcome per play, under `prefers-reduced-motion: no-preference`
  only. The fade is opacity only, because those parts are positioned by their own
  transforms. The stage has no infinite animation (the checker fails one), so there is
  nothing to pause.
- Cutouts are the alpha-channel `icons/` set. The originals under
  `static/assets/brand/cast/` are opaque VP8 and would sit in a black box, so the
  checker fails any cutout without an alpha channel.

### Setups carousel

- The row is a native scroll-snap row until the script runs. Without script, or
  without the vendored libraries, it stays that row (touch, trackpad and arrow keys on
  the focused row), two setups wide on a desktop and one with a peek on a phone; its
  controls and pager stay hidden.
- With the script, the row gets `.is-embla` and Embla (stable v8, `align: center`,
  `containScroll: trimSnaps`, no loop, no free drag) puts one setup in focus with its
  neighbours peeking in. Drag and swipe settle on a setup.
- Keys: Left and Right move one setup, Home and End go to the ends. Up and Down are
  left to the page (the row is horizontal). The keys act only on the carousel's own
  controls (the viewport, the arrows, the dots), so arrows inside a code card still
  scroll that code.
- The pager (dots beside the arrows) is one 44px target per setup, labelled with its
  position and name. The arrows and dots use `aria-disabled` at the ends, never
  `disabled`, so focus stays on them.
- Setups out of view are `inert`: they cannot take focus, so Tab never lands in an
  offscreen copy button or link. A focused peek is brought into view by Embla.
- Status: one polite line announces each change of setup once, "Setup 2 of 3: CLI.",
  from a key, arrow, dot, drag or button. A settle on the same setup says nothing.
- Motion, through the vendored Motion mini build (`Motion.animate`, WAAPI): the pager
  thumb slides to the dot in focus, and the newly selected setup settles in (opacity
  and a 6px rise, 320 ms). Both are finite. A move that interrupts a settle stops it
  first. Motion's stop() leaves the in-flight values in the setup's inline style, so
  the script clears that style, and the setup returns to its stylesheet values. The
  thumb is then placed on its dot. Browser checks cover a second press less than 100 ms
  after the first, and a preference change mid-settle.
- Reduced motion (`prefers-reduced-motion: reduce`) disables every animation the
  script starts: Embla's duration is 0 (a jump, never a snap), Motion is not called,
  and the thumb and setup are placed directly. A change to the preference while the
  page is open is applied at once: running motion stops, Embla keeps its setup and
  takes the new duration.
- The copy buttons and source links are the same elements the page ships; the carousel
  moves them, it does not rebuild them.

Each vendored file is its upstream license banner (a comment, the full MIT notice)
followed by the npm release body, byte for byte. The body's sha256 is the upstream pin;
the whole served file's sha256 is the served pin. Both are in
`.github/scripts/check_platform_pages.py` and `THIRD-PARTY-NOTICES.md`. The banner is
the only change, and it is a comment. The page loads them as local, fingerprinted scripts
before the page script, each with `defer`, and never re-minifies them. To update one,
unpack the new npm release, put its license banner in front of the release file, and
change the name, the version and both hashes in both places.

### No composer

The local stage has no text-entry field, no file input and no submission form in
`<main>`. Its radios (activity and scene) are native and named. The checker fails a
form, a text field or a file input anywhere in `<main>`. `assets/js/platform-page.js`
(the stage, the activity selector and the setups carousel) makes no request and touches
no storage, cookie or extension API, and the checker fails a script that does. The two
vendored libraries make no request either; they are local files. This promise covers
that script and those files only: the site's own consent banner, newsletter form and
other global scripts are outside this page's scope.

### Visual direction (the "break free" pass)

- **Hero:** copy, the activity selector and Start stay in one column on a phone. On a
  desktop the copy sits left and a decorative orbit sits right: the laptop cutout on two
  rings with the platform logo on a white tile. The orbit is `aria-hidden`, carries no
  caption and follows Start in source order. It is never a draft or a composer.
- **Stage:** a near-black theatre (`--near-black`, checked by the build) with a radial
  relay glow and faint contour rings. The extension is the focal medallion; the computer
  sits left, the signed-in profiles fan out right from the relay, and the outcome lands at
  the bottom. Cutouts float on the route with no box behind them and no caption; the
  route names are the only labels.
- **Amplify:** four profile slips fan out at fixed per-child angles and lengths (CSS
  custom properties, never inline). **Follow:** the same slips straighten into a ledger
  with a log stroke each, and the mouse-marine cutout guards below. **Dry fire (desktop):**
  the shipped dry fire is the desktop app's, so this scene names the desktop app on the
  relay, drops the extension cutout, and shows an "Extension flow planned" tag beside the
  diagram. The fan dims and the route to the outcome breaks in coral at the stop. The
  panel repeats that the extension flow is planned, not shipped.
- **Phone:** a 480 px theatre with the relay and fan moved left and in, two narrow route
  nodes and no full-length stack of boxes; no page overflow at 320 px.
- **Motion:** finite only. In the local stage (routes draw, spokes grow, the relay, slips
  and outcome fade in once per play; the ledger eases once on a scene change). In the
  setups carousel (Embla's snap, the pager thumb, the selected setup's settle; see
  Setups carousel). Reduced motion removes all of it; high contrast solidifies the
  edges. Nothing on the page is infinite (the checker fails one in the page's CSS).
- **Rules of engagement** are an open numbered gauge (each row a source link and a bar
  for its daily figure), not a stamp card. **Field Manual** is one two-column briefing
  with a rule between the facts. Their source text and links are unchanged. Activities
  is unchanged; the setups are a carousel (Setups carousel, above).

## Stage geometry checks

Check the stage in a real browser at 320, 390, 640, 820, 1039, 1040, 1280 and 1440 px,
in light and dark, in every scene (amplify, follow, dry fire). Measure with
`getBoundingClientRect` and the rendered height, not estimates:

- The page has no horizontal overflow: the document is no wider than the viewport.
- Every visible `.pp-slip`, `.pp-out`, `.pp-relay` and `.pp-crew-guard` lies inside
  `.pp-theatre`, which clips at its edges (`overflow: hidden`).
- The follow guard and the outcome do not overlap.
- Exactly one scene panel is visible, and it is the selected scene.

On a phone the outcome is anchored to the theatre's bottom edge, so taller text grows it
upward and never past the edge. The follow guard sits on the left edge, clear of the
relay and the outcome.

## Preview route rules

The page file sets `layout: platform-page`, `platform: <id>`,
`url: /preview/platforms/<id>/`, `noindex: true`, `exclude_search: true`,
`sitemap: {disable: true}` and `build: {list: never}`; `hugo.toml` excludes
`/preview/**` from llms.txt. Nothing in the navigation links to it.
`make check-platform-pages` fails if the built page is indexed, listed in the sitemap,
llms.txt, llms-full.txt or the search index, or linked from another page. It also fails
if any built page names the private product repository or its issue.

## Add the next platform

1. Confirm the platform is `supported` in `data/integrations.json`, its
   `data/platforms/<id>.yaml` lists the actions you want as types and as local scenes,
   and each has a `data/action_examples.json` entry.
2. Add a record to `pages` in `data/platform_pages.json`: route, two to four activity
   types bound to listed actions, the local stage (three scenes in the order amplify,
   follow, dry fire; joins from the YAML; sourced lines quoting public pages), the
   matrix copy, and sourced rules of engagement, Field Manual facts and setups.
   Leave the contract alone.
3. Add `content/en/preview-platform-<id>.md` with the front matter above.
4. Run `make check-schemas`, `make check-platform-pages` and `make test-scripts`, then
   check 1280 and 390 px in light and dark, and 320 px for overflow (`DESIGN.md`,
   `docs/deploy.md`).

Promoting a page out of preview is a deliberate change: the schema's `route` pattern
is preview-only, and a promoted page needs a new route, a navigation entry, sitemap and
search inclusion, removal of the reviewer note, and an update to these rules.

## Checks for the setups carousel

- `make check-platform-pages` (in `make check`) builds the page and runs the script
  through `platform_page_harness.js` against stubs of the two libraries: the option set
  Embla receives, its select, slidesInView, reInit, scrollTo and destroy, and each
  Motion call (a stop() commits the in-flight value, as the real library does). It
  covers the keys (Up and Down passed through), the pager, the buttons, the drag settle,
  inert setups, the announcement, a settle interrupted by a second move or by the
  preference changing, reduced motion from load and changed while open, the no-script
  row, and an Embla that throws on start or finds other than one stop per setup (the
  row falls back and the error is logged).
- The same target fails a vendored file whose body or served bytes are not the pinned
  ones, a file without its license banner, a page that loads a library twice, out of
  order or from another host, a carousel that is not hidden without script, and a
  single-setup or missing copy button.
- `make test-scripts` (`test_platform_pages.py`) breaks the script and the built page in
  each of those ways, including removing the settle reset, and checks that the failure
  is named.
- `make check-platform-carousel` is the real-browser pass. It is not in `make check`,
  because it needs a Chromium and the `playwright-core` package. It builds the site,
  serves it on a random local port and drives Chromium through: the Left, Right, Home
  and End keys, Up and Down left to the page, Tab order past an inert setup, the
  dots, a mouse drag and a touch swipe, copy and source links, two presses less than
  100 ms apart and reduced motion changed mid-settle (the rest state of every setup
  and the thumb is checked after each), reduced motion changed while open (every move
  a jump, no animation anywhere on the page), a resize, an Embla that throws on start,
  320, 390, 820 and 1440 px in light and dark, the no-script row, and that only this
  origin is requested. Run it after changing the row's markup, the script, or
  Embla's options.

  ```sh
  npm install --no-save playwright-core
  CHROME_PATH=/path/to/chrome make check-platform-carousel
  ```

  `CHROME_PATH` is optional; without it Playwright uses the browser it installed for
  `playwright-core`. `SHOTS_DIR` picks where the screenshots and `results.json` go
  (default: a temporary folder).

The footer of the site carries a status pulse, an infinite animation outside this page
(`assets/css/site.css`). It stops under reduced motion. The page's own CSS and script
have none.

## Known limits and planned work

- **Planned, not shipped: a dry run from the extension.** Today the desktop app's dry
  fire checks the sign-in and stops before composing, and posts nothing
  (`/docs/reference/use-the-desktop-app/`). The stage marks the extension version as
  planned. Product tracking is the private product issue
  `blowhorn-ai/blowhorn#2178` (planned anonymous extension flow). That issue appears in
  this document only. It must never appear on a rendered page, and the built-page check
  enforces that.
- **The call to action installs the extension only.** The extension works with the
  Blowhorn desktop app; no link installs both or carries the picked platform and type.
  When one exists, change the label, `extensionHref` and the check together.
- **The Web Store link is written in several templates** (`layouts/download.html`,
  `download-thanks.html`, `_partials/header.html`, `footer.html`, `home/ways-in.html`,
  this page's data partial, `content/en/legal/terms.md`). The check ties this page to
  the download page's copy; the fix is one `data/extension.json`, as its own change.
- **No recording exists**, so the stage is an illustration. It says so in the
  reviewer note and never presents itself as footage.
- **One platform so far.** The schema allows more records; only X has one.
