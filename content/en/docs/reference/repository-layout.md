---
title: "Repository layout"
---
# Repository layout

Where things live in the checkout.

The repository root now keeps only primary entry points, core packages, workspace data, and top-level docs. Supporting assets are grouped by function:

- `blowhorn/store/` - the only code that speaks SQL, and the one place the organization scope is applied: the `Store` protocol, one repository module per domain (`profiles`, `content`, `schedule`, `ledgers`, `runs`, `credentials`), `runtime.py` (the one seam every command obtains its store through), `connection.py`, `settings.py` and `tunnel.py`, the `PostgresStore` backend and `open_store` (`postgres.py`), the payload vetting both backends share (`rows.py`), `fake.py` (the hermetic in-memory backend the test suite runs against), the `blowhorn store` probe (`probe.py`) and its `--import` (`importer.py`), and `schema.py`, the declarative mirror of `blowhorn/migrations/`.
- `blowhorn/migrations/` - the timestamped `*.up.sql` / `*.down.sql` pairs for the `blowhorn` database, applied forward-only by `scripts/store/apply-schema.py` (`make store-schema-apply`).
- `scripts/store/` holds the two store maintainer scripts behind their Makefile targets: the schema runner above, and `migrate-from-sheet.py` (`make store-migrate`), the one-time move off Google Sheets. The migration has run; the script, its target and the Sheet reader it imports (`blowhorn/content_sheet.py`) stay only for its one remaining step and are deleted together once it has run - see [Migrate from Google Sheets to the store](../how-to/migrate-to-the-store.md).
- `tests/integration/` holds the tests that need a throwaway Postgres, gated on `BLOWHORN_TEST_DATABASE_URL` and skipped in CI; see [Run the tests](../how-to/run-the-tests.md).
- `docs/design/` stores design notes, proposals, and Playwright recordings used for feature design.
- `scripts/debug/` stores manual auth probes and browser recording utilities.
- `scripts/reporting/` stores one-off reporting utilities such as HTML analytics generation.
- `scripts/cron/` stores scheduled task wrappers such as analytics collection.
- `scripts/macos/` stores macOS-specific assets: the launchd definition `blowhorn service install` writes (`ai.blowhorn.service.plist.template`) and its entrypoint `Blowhorn` (named so System Settings › Allow in the Background does not fall back to "python").
- `scripts/node/` stores standalone Node/Puppeteer probes.
- `brand/` stores the Blowhorn brand kit (logo files, tokens, voice, Major Blowhorn), and `scripts/brand/` the generator behind `make brand-build` - see [Brand assets reference](/docs/reference/brand-assets/).
- `desktop/` stores the Electron menu-bar app (the popover, the console, the Setup screen); it is packaged as a universal DMG attached to each `desktop-vX.Y.Z` GitHub release (there is no package manager in the path - the repository is private), and it never bundles the Python CLI.
- `analytics/` stores repository-level LinkedIn analytics exports, shared CSV history, and the generated HTML dashboard.
- `cache/debug/` stores generated debug artifacts instead of writing them into the repository root. `scripts/debug/linkedin_login_inspect.py` writes its JSON and HTML under `cache/debug/linkedin_login_inspect/`. `scripts/debug/_linkedin_login_inspect/` is ignored so an older dump cannot be committed.
- `cache/diagnostics/<profile>/` stores what a LinkedIn login that could not decide saves: a screenshot and the page's address (`li-login-<timestamp>-<reason>.png` / `.url`). `cache/` is git-ignored, so no profile needs an ignore entry of its own. Treat the files as sensitive - they show a real account's login or challenge page - and never commit or share them.
