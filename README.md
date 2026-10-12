<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="static/assets/brand/logo/blowhorn-lockup-horizontal-on-dark.svg">
    <img alt="Blowhorn" src="static/assets/brand/logo/blowhorn-lockup-horizontal.svg" width="360">
  </picture>
</p>

# Blowhorn site and downloads

This repository is two things for **Layer5 Blowhorn**:

1. **The marketing site** at [blowhorn.ai](https://blowhorn.ai). It is a [Hugo](https://gohugo.io) site with [Docsy](https://www.docsy.dev) as a Hugo module, built like [docs.layer5.io](https://github.com/layer5io/docs) and deployed to GitHub Pages by [`site.yml`](.github/workflows/site.yml). The Pages custom domain is already blowhorn.ai, so the project URL <https://layer5io.github.io/blowhorn-site/> only redirects there; the site is reachable once the domain's DNS points at Pages, as [`docs/deploy.md`](docs/deploy.md) describes.
2. **Public downloads.** macOS disk images and their checksums are published as [GitHub Releases](https://github.com/layer5io/blowhorn-site/releases) on this repository. No release binary is committed here.

Blowhorn is a social media console that takes one message and broadcasts, reposts and amplifies it across every profile and platform your community runs, on autopilot. One message out, many ears in.

## Download

Once the first stable release is public, this link always points at the newest universal macOS build:

```
https://github.com/layer5io/blowhorn-site/releases/latest/download/Blowhorn-mac.dmg
```

Every release carries a `SHA256SUMS.txt`. Check the image before you open it:

```bash
shasum -a 256 -c SHA256SUMS.txt
```

The Chrome extension ships through the Chrome Web Store, not from this repository.

## Where things live

| | |
|---|---|
| Site configuration | [`hugo.toml`](hugo.toml); the pinned toolchain is [`go.mod`](go.mod) (Docsy as a Hugo module), [`package.json`](package.json) (Hugo extended, postcss) and [`.nvmrc`](.nvmrc) (Node.js) |
| Pages | [`content/en/`](content/en/): the home page's front matter, the Trust Center and its privacy and terms pages ([`legal/`](content/en/legal/)), and the [`docs/`](content/en/docs/) section scaffold (landing, quadrant, group, and CLI indexes) in Markdown |
| Templates | [`layouts/`](layouts/): the home page ([`home.html`](layouts/home.html)), the shared shell ([`baseof.html`](layouts/baseof.html)), the Trust Center hub ([`trust-center.html`](layouts/trust-center.html)), the legal pages ([`legal.html`](layouts/legal.html)), the 404 page, the header, footer and icon sprite partials, the `llms.txt` and Markdown outputs, and the Docsy-based docs shell ([`layouts/docs/`](layouts/docs/)) |
| Styles and script | [`assets/css/site.css`](assets/css/site.css) and [`assets/js/download.js`](assets/js/download.js) (the Download section); Hugo minifies and fingerprints both. The docs section's Blowhorn skin over Docsy is [`assets/scss/`](assets/scss/), with its sidebar toggle and offline search in [`assets/js/`](assets/js/) |
| Brand assets | [`static/assets/brand/`](static/assets/brand/), served at `/assets/brand/`: version 1 of the brand kit (logo system, Major Blowhorn, marketing art, `tokens.json`) and the three self-hosted fonts; attribution in [`LICENSES.md`](static/assets/brand/LICENSES.md) |
| How the site deploys and how the domain is wired | [`docs/deploy.md`](docs/deploy.md) |
| How releases are published | [`docs/distribution.md`](docs/distribution.md) |
| Release binaries | [Releases](https://github.com/layer5io/blowhorn-site/releases) on this repository |
| Product source and build pipeline | Private: [`leecalcote/blowhorn`](https://github.com/leecalcote/blowhorn) |

**Reporting problems.** The product repository is private, so use [this repository's issues](https://github.com/layer5io/blowhorn-site/issues) for everything public: site content, a download that will not open, a wrong checksum, or a bug in the app. Maintainers triage app bugs into the product repository. The [Layer5 Slack](https://slack.layer5.io) works too.

## Working on the site

You need Go (Hugo modules), Node.js and npm (the pinned Hugo extended and postcss come from `package.json`), Python 3 and `make`. The build targets follow the shared contract of [layer5io/docs](https://github.com/layer5io/docs/blob/master/Makefile). `make help` lists every target.

```bash
make setup             # npm install: the pinned Hugo extended and postcss
make site              # serve at http://localhost:1313 with live reload
make build-production  # build into public/, what CI deploys
make check             # every check, against a fresh production build
make ci                # exactly what site.yml's check job runs, starting with npm ci
```

Every CI step that runs repository logic is a make target, and the workflow calls that target, so one `make` command reproduces any CI step:

| Target | What it runs | Run by |
|---|---|---|
| `setup-ci` | `npm ci` (the locked dependencies) | `site.yml` |
| `workflow-check` | actionlint on `site.yml`, `publish-dmg.yml` and `sync-docs.yml` | `site.yml` |
| `test-scripts` | unit tests for the check scripts in `.github/scripts/` | `site.yml` |
| `site-check` | one production build, then the four checks below | `site.yml` |
| `validate-html` | html-validate on every built page | `site-check` |
| `check-links` | every local link, image, font and `srcset` reference resolves | `site-check` |
| `check-third-party` | no page, or stylesheet or script it loads, requests another host (except the disclosed GitHub release lookup) | `site-check` |
| `check-urls` | every published URL and anchor still exists | `site-check` |
| `dmg-resolve`, `dmg-download`, `dmg-package`, `dmg-verify`, `dmg-release` | the five steps of publishing a DMG release, each reading its inputs from the environment ([docs/distribution.md](docs/distribution.md#local-checks)) | `publish-dmg.yml` |
| `dmg-check DMG=...` | sanity-check a disk image before publishing | `dmg-package` runs the same script (`check-dmg.sh`) |
| `docs-sync REF=...` | copy the product docs from a `leecalcote/blowhorn` checkout into `content/en/docs/` ([docs/deploy.md](docs/deploy.md#product-docs-sync)) | `sync-docs.yml` |
| `docs-sync-start-checks` | start `site.yml` on the `docs-sync` branch after a sync ([docs/deploy.md](docs/deploy.md#product-docs-sync)) | `sync-docs.yml` |

Each check target builds for production first, so it also runs on its own. `labeler.yml`, `label-commenter.yml` and `slack.yml` only call third-party actions and run no repository logic, so they have no target.

The site follows the brand kit exactly: every colour, type style, spacing, radius and shadow in `assets/css/site.css` is a token from `static/assets/brand/tokens.json`, with light as the default theme and dark following the operating system. Brand SVGs are used as files and never recoloured. The one-to-many hero illustration and the platform marks are inline SVG drawn in `currentColor`.

Nothing on the site loads from another host: no CDN, no web fonts from elsewhere, no analytics. The one request to another host while browsing is the Download section's release lookup on GitHub's API (`assets/js/download.js`). The footer newsletter form posts to Layer5's Mailchimp list only when submitted. The [privacy page](https://blowhorn.ai/privacy.html) discloses both. `make site-check` fails a build that loads anything else from another host. The public URLs (`/`, `/privacy.html`, `/terms.html`, `/assets/brand/...`) and the home page's anchors (`#platforms`, `#how`, `#trust`, `#download`) are linked from outside this repository; the same check fails a build that loses one.

The site also publishes [`/llms.txt`](https://blowhorn.ai/llms.txt), [`/llms-full.txt`](https://blowhorn.ai/llms-full.txt) and a Markdown copy of every page (`/legal/privacy/index.md`), as docs.layer5.io does.

### CI

| Workflow | When | What it does |
|---|---|---|
| [`site.yml`](.github/workflows/site.yml) | Pull requests, pushes to `master`, manual runs | Lints the workflows, runs the check-script unit tests, builds the site with the pinned Hugo, Go and Node.js, runs `make site-check` and uploads the Pages artifact. On `master` it deploys the artifact to GitHub Pages. |
| [`publish-dmg.yml`](.github/workflows/publish-dmg.yml) | Manual, or `repository_dispatch` (`publish-dmg`) from product CI | Downloads a built DMG over HTTPS, checks it, verifies signing and notarization on a macOS runner (required for any public release), then creates the release with versioned assets, the `Blowhorn-mac.dmg` alias and checksums. Drafts by default; never overwrites. |
| [`sync-docs.yml`](.github/workflows/sync-docs.yml) | Manual, or `repository_dispatch` (`sync-docs`) from product CI | Checks out the product docs at the requested ref, opens or updates the `docs-sync` pull request (`docs: sync from <ref>`), and starts the site checks on it itself (`gh workflow run site.yml`); merging deploys once those checks pass. |

<div>&nbsp;</div>

## Join the Layer5 community!

<a name="contributing"></a><a name="community"></a>
Our projects are community-built and welcome collaboration. 👍 Be sure to see the <a href="https://layer5.io/community/newcomers">Layer5 Community Welcome Guide</a> for a tour of resources available to you and jump into our <a href="http://slack.layer5.io">Slack</a>!

<p style="clear:both;">
<a href ="https://layer5.io/community/meshmates"><img alt="MeshMates" src=".github/readme/images/layer5-community-sign.png" style="margin-right:10px; margin-bottom:15px;" width="28%" align="left"/></a>
<h3>Find your MeshMate</h3>

<p>MeshMates are experienced Layer5 community members, who will help you learn your way around, discover live projects and expand your community network. 
Become a <b>Meshtee</b> today!</p>

Find out more on the <a href="https://layer5.io/community">Layer5 community</a>. <br />
<br /><br /><br /><br />
</p>

<div>&nbsp;</div>

<a href="https://slack.layer5.io">
  <picture align="right">
    <source media="(prefers-color-scheme: dark)" srcset=".github/readme/images//slack-dark-128.png"  width="110px" align="right" style="margin-left:10px;margin-top:10px;">
    <source media="(prefers-color-scheme: light)" srcset=".github/readme/images//slack-128.png" width="110px" align="right" style="margin-left:10px;padding-top:5px;">
    <img alt="Slack logo" src=".github/readme/images//slack-128.png" width="110px" align="right" style="margin-left:10px;padding-top:13px;">
  </picture>
</a>

<a href="https://layer5.io/community"><img alt="Layer5 Community" src=".github/readme/images//community.svg" style="margin-right:8px;padding-top:5px;" width="140px" align="left" /></a>

<p>
✔️ <em><strong>Join</strong></em> any or all of the weekly meetings on <a href="https://calendar.google.com/calendar/b/1?cid=bGF5ZXI1LmlvX2VoMmFhOWRwZjFnNDBlbHZvYzc2MmpucGhzQGdyb3VwLmNhbGVuZGFyLmdvb2dsZS5jb20">community calendar</a>.<br />
✔️ <em><strong>Watch</strong></em> community <a href="https://www.youtube.com/playlist?list=PL3A-A6hPO2IMPPqVjuzgqNU5xwnFFn3n0">meeting recordings</a>.<br />
✔️ <em><strong>Access</strong></em> the <a href="https://drive.google.com/drive/u/4/folders/0ABH8aabN4WAKUk9PVA">Community Drive</a> by completing a community <a href="https://layer5.io/newcomer">Member Form</a>.<br />
✔️ <em><strong>Discuss</strong></em> in the <a href="https://discuss.layer5.io">Community Forum</a>.<br />
✔️<em><strong>Explore more</strong></em> in the <a href="https://layer5.io/community/handbook">Community Handbook</a>.<br />
</p>
<p align="center">
<i>Not sure where to start?</i> Grab an open issue with the <a href="https://github.com/issues?q=is%3Aopen+is%3Aissue+archived%3Afalse+repo%3Alayer5io%2Fblowhorn-site+label%3A%22help+wanted%22">help-wanted label</a>.</p>
