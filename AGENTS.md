# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Add durable project-specific notes here as they are discovered through real work.

## Building the site locally

blowhorn.ai is Hugo with Docsy as a Hugo module, built like layer5io/docs. Run
`make setup` once (npm install) for the pinned toolchain (the dependency check
also accepts system `hugo` and `postcss`), then `make preview`
(live reload, http://localhost:1313) or `make build-production` (writes `public/`).
`make check` is exactly what CI runs. Go must be on PATH: Hugo fetches Docsy through it.

The marketing and legal pages do not use Docsy's templates: they render through
`layouts/home.html`, `layouts/trust-center.html` (the Trust Center hub at `/legal/`),
`layouts/legal.html` (each policy at `/legal/<name>/`), `layouts/brand.html` (the Brand page at `/brand/`) and `layouts/404.html` inside
`layouts/baseof.html`, with the header, footer and icon sprite in `layouts/_partials/`.

## Rules the site holds

- **No third parties.** The privacy page promises no cookies, no analytics and no asset
  loaded from another host; the only outside request is the download page's disclosed
  release lookup on api.github.com, and the footer newsletter form may post only to the Mailchimp host in
  `FORM_ACTION_HOSTS`. Never add an analytics id, a CDN script or stylesheet, or web
  fonts from elsewhere; never copy layer5io/docs' head, navbar, footer or its
  `[services.googleAnalytics]` block. `.github/scripts/check-third-party.py` fails the build.
- **Brand tokens only.** Every colour, type style, radius and shadow in
  `assets/css/site.css` is a token from `static/assets/brand/tokens.json`. Light is the
  default; dark follows the OS with no JavaScript. Brand SVGs are used as files, never
  recoloured. Platform logos are the owners' own files in `static/assets/platforms/`, unmodified, on white
  tiles (sources in `static/assets/brand/LICENSES.md`).
- **The brand kit is built, not edited.** `static/brand/blowhorn-brand-kit.zip` and
  `data/brand_colors.json` come from the product repository's brand build
  (`scripts/brand/build-brand-kit.py`, output in `marketing/brand/kit/`); copy them over unchanged.
- **The product name is Blowhorn.** "Outbox" is the product's old internal name; never put
  it on a public page.
- **The product repository is private.** Never link its files, issues or pull requests
  from a page; every reader would get a 404.

## CI runs through make

Every CI step that runs repository logic is a Makefile target and the workflow calls it
(`site.yml`, and the `dmg-*` steps of `publish-dmg.yml` backed by `.github/scripts/publish-dmg/`).
When you add or change a CI step, put the logic behind a make target, call the target from
the workflow, and list it in the README's target table. `make ci` reproduces site.yml's check job.

## Keeping URLs and anchors alive

`/`, `/legal/`, `/legal/privacy/`, `/legal/terms/`, `/assets/brand/...` and the home
page's anchors (`#platforms`, `#how`, `#trust`, `#download`) are linked from outside this
repo, and the old `/privacy.html` and `/terms.html` must keep redirecting to their
`/legal/` pages. `.github/scripts/check-site-contract.py` lists every one and fails the
build when one disappears. When a page moves, add the dead path to the page's `aliases:`
front matter rather than leaving a 404 (GitHub Pages has no server redirects, so an alias
is a meta refresh with a canonical link) and list it in the script's `REDIRECTS`, and keep a renamed heading's old anchor with
`### New Wording {#old-anchor-slug}`. To prove nothing was lost, build master and your
branch to separate directories and diff the `id=` attributes across both trees.

Do not give a page in `content/en/` a `url:` ending in `.html`: `url` names one path for
every output format, so the page's Markdown output (`index.md` format) overwrites its HTML.
New pages go in a section (such as `content/en/legal/`), which gets pretty URLs; `uglyURLs`
in `hugo.toml` applies only to top-level pages, and the home page's public URL comes from
`layouts/_partials/canonical.html`.

The Trust Center's summaries (front matter of `content/en/legal/_index.md`) restate what
the policies and public docs already say. Never add a certification, sub-processor,
retention period, encryption detail or compliance claim that a policy does not make.

## Verifying a change

Check the built HTML in `public/`, not the source. Goldmark's typographer is off so quotes
stay straight; HTML is not minified so html-validate can check what ships. For a visual
change, follow the screenshot checklist in `docs/deploy.md` (390, 820 and 1440 px, light
and dark, no horizontal scroll from 320 px).

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.

## Design rules

Before any layout or copy change, follow [DESIGN.md](DESIGN.md) (whitespace tokens, concision rules and the PR checklist).
