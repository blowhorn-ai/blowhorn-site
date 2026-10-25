#!/usr/bin/env bash
# Start the site checks on the docs-sync branch.
#
# Pushes and pull requests made with github.token never start pull_request
# or push workflows, so site.yml would otherwise stay silent on the sync
# pull request. A workflow_dispatch run started with that same token is
# allowed, and it attaches to the branch head — but it does NOT show as
# the PR's check, so sync-docs-merge.sh gates on the run itself, not on
# the pull request's checks. Run it through make (see the
# docs-sync-start-checks target); sync-docs.yml calls the same target.
#
# Usage: sync-docs-start-checks.sh [BRANCH]  (default: docs-sync)
#
# Needs GH_TOKEN (github.token in CI) and, outside this repository,
# GH_REPO=owner/repo so gh knows which repository to dispatch in.
set -euo pipefail
branch="${1:-docs-sync}"
exec gh workflow run site.yml --ref "$branch"
