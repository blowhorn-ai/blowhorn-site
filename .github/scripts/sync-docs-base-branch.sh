#!/usr/bin/env bash
# Check out the docs-sync branch on the latest published state.
#
# Builds on the open sync pull request's branch, or on origin/master when
# there is none: a docs-sync branch left behind by a merged or closed PR is
# stale. `gh pr list --head` matches the branch name only, so fork PRs from
# a branch of the same name are dropped. The open PR's number (empty when
# none) goes to GITHUB_OUTPUT as open_pr, or to stdout outside Actions. Run
# it through make (see the docs-sync-base target); sync-docs.yml calls the
# same target.
#
# Usage: sync-docs-base-branch.sh [BRANCH]  (default: docs-sync)
#
# Switches the current checkout to BRANCH. Needs GH_TOKEN (github.token in
# CI) and an `origin` remote.
set -euo pipefail
branch="${1:-docs-sync}"
open_pr="$(gh pr list --head "$branch" --base master --state open \
  --json number,isCrossRepository \
  --jq 'map(select(.isCrossRepository | not))[0].number // empty')"
echo "open_pr=$open_pr" >> "${GITHUB_OUTPUT:-/dev/stdout}"
git fetch origin "$branch" 2>/dev/null || true
if [ -n "$open_pr" ] && git rev-parse --verify --quiet "origin/$branch" >/dev/null; then
  git checkout -B "$branch" "origin/$branch"
else
  git fetch origin master
  git checkout -B "$branch" origin/master
fi
