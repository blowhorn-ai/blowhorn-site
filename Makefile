# Copyright Layer5, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

include .github/build/Makefile.show-help.mk

#-----------------------------------------------------------------------------
# blowhorn.ai is a Hugo site with Docsy as a Hugo module, built like
# layer5io/docs. You need Go (Hugo modules), Node.js and npm (the pinned
# hugo-extended and postcss come from package.json), Python 3 (checks) and make.
#
# MAIN TARGETS (the shared target contract of layer5io/docs: same names,
# prerequisites and npm scripts; see https://github.com/layer5io/docs/blob/master/Makefile)
#
#   setup              Install site dependencies (npm install).
#   build              Build locally with draft, future, and expired content.
#   build-preview      Build for a deploy preview (uses BASE_URL or DEPLOY_PRIME_URL).
#   build-production   Build for production. Pass BASE_URL=... to set the base URL.
#   site               Public build (no /internal/) into public/ (as CI deploys).
#   serve              Serve locally once, file watcher off (no live reload).
#   check-links        Check every local link, image and font in the built site.
#   check-deps         Verify required commands and local dependencies.
#   check-go           Verify Go is installed (required by Hugo Modules).
#
# BLOWHORN TARGETS (every CI step that runs repository logic is one of these;
# the workflows call the target, so `make <target>` reproduces that step)
#
#   setup-ci           Install the exact locked dependencies (npm ci), as CI does.
#   validate-html      Production build, then html-validate on every page.
#   check-third-party  Production build, then fail on any request to another host.
#   check-urls         Production build, then fail on a lost public URL or anchor.
#   site-check         Production build once, then validate-html, check-links,
#                      check-third-party and check-urls (site.yml).
#   check-no-internal  Fail if the production build contains /internal/.
#   site-internal      Internal build (hugo --environment internal, mounting
#                      BLOWHORN_DIR, default ../blowhorn) into public-internal/.
#   preview, preview-internal
#                      Live-reload servers for the two builds.
#   test-scripts       Unit tests for the check scripts in .github/scripts/.
#   workflow-check     actionlint on this repository's workflows.
#   check              site-check, test-scripts and workflow-check.
#   ci                 setup-ci, then everything site.yml's check job runs.
#   dmg-check          Sanity-check a disk image: make dmg-check DMG=path/to/file.dmg
#   dmg-resolve, dmg-download, dmg-package, dmg-verify, dmg-release
#                      The steps of publish-dmg.yml (see docs/distribution.md).
#   docs-sync          Sync the user docs from a leecalcote/blowhorn checkout
#                      into content/en/docs/: make docs-sync REF=<tag|branch|sha>
#                      (see docs/deploy.md).
#   docs-sync-base     Check out the docs-sync branch on the open sync PR's
#                      head, or on origin/master when none is open.
#   docs-sync-start-checks
#                      Start the site checks on the docs-sync branch after a
#                      sync: gh workflow run site.yml (see docs/deploy.md).
#   help               List every target with its description.
#   clean              Remove the build output, Hugo's cache and downloaded tools.
#-----------------------------------------------------------------------------
# Fixed: the npm build and link-check scripts and site.yml all use public/.
override BUILD_DIR := public
HTML_VALIDATE_VERSION ?= 9.5.5
ACTIONLINT_VERSION ?= 1.7.7
BIN_DIR ?= .bin
# actionlint from PATH when installed; otherwise a pinned copy is downloaded into $(BIN_DIR).
ACTIONLINT ?= $(shell command -v actionlint 2>/dev/null)
# Workflows owned by this repo. Template workflows (labeler and friends) are left as-is.
WORKFLOWS ?= .github/workflows/site.yml .github/workflows/publish-dmg.yml .github/workflows/sync-docs.yml
# A leecalcote/blowhorn checkout for `make docs-sync` (the sync-docs.yml
# workflow checks the product repo out at this path).
SOURCE_DIR ?= product
# The private leecalcote/blowhorn clone that config/internal/hugo.toml mounts
# (module import github.com/leecalcote/blowhorn, replaced with this directory).
BLOWHORN_DIR ?= ../blowhorn
BLOWHORN_ABS = $(abspath $(BLOWHORN_DIR))
BLOWHORN_MODULE := github.com/leecalcote/blowhorn
DOCS_DIR ?= content/en/docs
# Branch the sync-docs.yml workflow pushes and opens its pull request from.
SYNC_BRANCH ?= docs-sync

# ---------------------------------------------------------------------------
# MAINTENANCE
# ---------------------------------------------------------------------------

## Verify required commands and local dependencies are present.
check-deps:
	@echo "Checking if 'npm' is installed and 'hugo' is available via node_modules (installed by 'make setup')..."
	@command -v npm > /dev/null || { echo "Error: 'npm' not found. Please install Node.js and npm."; exit 1; }
	@test -x node_modules/.bin/hugo || { echo "Error: Hugo binary not found in node_modules. Please run 'make setup' first."; exit 1; }
	@echo "Dependencies check passed."

## Verify Go is installed locally.
check-go:
	@echo "Checking if Go is installed..."
	@command -v go > /dev/null || { echo "Go is not installed. Please install it before proceeding."; exit 1; }
	@echo "Go is installed."

## Check every local link, image, font and srcset reference in a production build.
check-links: build-production
	npm run check:links

## List every target with its description.
help: show-help

# ---------------------------------------------------------------------------
# LOCAL BUILDS
# ---------------------------------------------------------------------------

## Install blowhorn.ai dependencies (the pinned Hugo extended and postcss) on your local machine.
setup:
	npm install

## Install the exact locked dependencies from package-lock.json (npm ci), as CI does.
setup-ci:
	npm ci

## Build the site locally with draft and future content enabled.
build: check-go check-deps
	npm run build

## Build the site for a deploy preview.
build-preview: check-go check-deps
	npm run build:preview

## Build blowhorn.ai for production with optional base URL (what CI deploys).
build-production: check-go check-deps
	set -e; \
	if [ -n "$(BASE_URL)" ]; then \
		base_url="$(BASE_URL)"; \
		base_url="$${base_url%/}/"; \
		npm run build:production -- --baseURL "$$base_url"; \
	else \
		npm run build:production; \
	fi

## Build the public site (no /internal/) into public/, as CI deploys it.
site: build-production

## Build the internal site (public pages plus /internal/ from the leecalcote/blowhorn clone at BLOWHORN_DIR, default ../blowhorn) into public-internal/.
site-internal: check-go check-deps check-blowhorn
	HUGO_MODULE_REPLACEMENTS="$(BLOWHORN_MODULE) -> $(BLOWHORN_ABS)" npm run build:internal

## Serve the public site at http://localhost:1313 with live reload (draft and future content enabled).
preview: check-go check-deps
	npm run site

## Serve the internal site at http://localhost:1313 with live reload, rendered in memory so public/ is never touched.
preview-internal: check-go check-deps check-blowhorn
	HUGO_MODULE_REPLACEMENTS="$(BLOWHORN_MODULE) -> $(BLOWHORN_ABS)" npm run _hugo -- server --environment internal --renderToMemory

## Fail unless BLOWHORN_DIR is a leecalcote/blowhorn clone with the internal sources.
check-blowhorn:
	@test -d "$(BLOWHORN_ABS)/marketing/strategy/hugo/strategy" || { echo "Error: no leecalcote/blowhorn clone at BLOWHORN_DIR=$(BLOWHORN_DIR) ($(BLOWHORN_ABS)). Clone it beside this repository (git clone https://github.com/leecalcote/blowhorn ../blowhorn) or pass BLOWHORN_DIR=path/to/blowhorn."; exit 1; }


## Build and serve the site once with the file-watcher off (no live reload).
serve: check-go check-deps
	npm run serve

# ---------------------------------------------------------------------------
# CHECKS
# ---------------------------------------------------------------------------

## Build for production, then run html-validate on every page.
validate-html: build-production
	npx --yes html-validate@$(HTML_VALIDATE_VERSION) "$(BUILD_DIR)/**/*.html"

## Build for production, then fail if a page, or a stylesheet or script it loads, requests another host.
check-third-party: build-production
	python3 .github/scripts/check-third-party.py $(BUILD_DIR)

## Build for production, then fail if a published URL or anchor is gone.
check-urls: build-production
	python3 .github/scripts/check-site-contract.py $(BUILD_DIR)

## Build for production once, then validate-html, check-links, check-third-party and check-urls (what site.yml runs).
site-check: validate-html check-links check-third-party check-urls check-no-internal

## Build for production, then fail if the /internal/ section leaked into it.
check-no-internal: build-production
	.github/scripts/check-no-internal.sh $(BUILD_DIR)

## Alias of site-internal.
build-internal: site-internal

## Run the unit tests for the check scripts in .github/scripts/.
test-scripts:
	python3 -m unittest discover -s .github/scripts -p 'test_*.py'

## Lint this repo's GitHub Actions workflows with actionlint.
workflow-check:
ifeq ($(ACTIONLINT),)
	@test -x $(BIN_DIR)/actionlint || (mkdir -p $(BIN_DIR) && cd $(BIN_DIR) && \
		curl -fsSL https://raw.githubusercontent.com/rhysd/actionlint/v$(ACTIONLINT_VERSION)/scripts/download-actionlint.bash | \
		bash -s -- $(ACTIONLINT_VERSION) .)
	$(BIN_DIR)/actionlint -color $(WORKFLOWS)
else
	$(ACTIONLINT) -color $(WORKFLOWS)
endif

## Run every check: site-check, test-scripts and workflow-check.
check: site-check test-scripts workflow-check

## Reproduce site.yml's check job: setup-ci, workflow-check, test-scripts and site-check, in that order.
ci:
	$(MAKE) setup-ci
	$(MAKE) workflow-check
	$(MAKE) test-scripts
	$(MAKE) site-check

## Sanity-check a local disk image before publishing: make dmg-check DMG=path/to/Blowhorn.dmg
dmg-check:
	@test -n "$(DMG)" || (echo "usage: make dmg-check DMG=path/to/file.dmg"; exit 1)
	.github/scripts/check-dmg.sh "$(DMG)"

## Sync the user docs from a leecalcote/blowhorn checkout at $(SOURCE_DIR) into $(DOCS_DIR): make docs-sync REF=<tag|branch|sha> (see docs/deploy.md).
docs-sync:
	@test -n "$(REF)" || (echo "usage: make docs-sync REF=<tag|branch|sha of leecalcote/blowhorn> [SOURCE_DIR=path/to/checkout]"; exit 1)
	python3 .github/scripts/sync-docs.py "$(SOURCE_DIR)" "$(DOCS_DIR)" --ref "$(REF)"

## Check out the docs-sync branch on the open sync PR's head, or on origin/master when none is open (what sync-docs.yml runs before the sync).
docs-sync-base:
	.github/scripts/sync-docs-base-branch.sh "$(SYNC_BRANCH)"

## Start the site checks on the docs-sync branch after a sync: gh workflow run site.yml (what sync-docs.yml runs after opening the sync PR).
docs-sync-start-checks:
	.github/scripts/sync-docs-start-checks.sh "$(SYNC_BRANCH)"

# publish-dmg.yml steps. Each reads its inputs from the environment, as the
# workflow sets them; see the script headers in .github/scripts/publish-dmg/.

## publish-dmg step 1: validate IN_VERSION, IN_URL, IN_ARCH, IN_DRAFT, IN_NOTARIZED, IN_NOTES into GITHUB_OUTPUT.
dmg-resolve:
	.github/scripts/publish-dmg/resolve.sh

## publish-dmg step 2: download DMG_URL to dist/source.dmg over HTTPS (DMG_SOURCE_TOKEN only to GitHub hosts).
dmg-download:
	.github/scripts/publish-dmg/download.sh

## publish-dmg step 3: check dist/source.dmg, name it for VERSION and ARCH, write SHA256SUMS.txt.
dmg-package:
	.github/scripts/publish-dmg/package.sh

## publish-dmg step 4 (macOS): verify integrity, signature, Gatekeeper and stapled notarization of dist/*.dmg.
dmg-verify:
	.github/scripts/publish-dmg/verify-macos.sh

## publish-dmg step 5: create the GitHub Release VERSION from dist/ (never overwrites).
dmg-release:
	.github/scripts/publish-dmg/release.sh

## Remove the build output, Hugo's resource cache and downloaded tools.
clean:
	npm run clean
	rm -rf $(BUILD_DIR) $(BIN_DIR)

.PHONY: \
	setup \
	build \
	build-preview \
	build-production \
	site \
	serve \
	check-links \
	check-deps \
	check-go \
	help \
	setup-ci \
	validate-html \
	check-third-party \
	check-urls \
	site-check \
	check-no-internal \
	build-internal \
	site-internal \
	preview \
	preview-internal \
	check-blowhorn \
	test-scripts \
	workflow-check \
	check \
	ci \
	dmg-check \
	dmg-resolve \
	dmg-download \
	dmg-package \
	dmg-verify \
	dmg-release \
	docs-sync \
	docs-sync-base \
	docs-sync-start-checks \
	clean
