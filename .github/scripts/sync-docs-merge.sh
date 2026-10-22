#!/usr/bin/env bash
# Wait for the site checks on the docs-sync branch, then merge its pull
# request with administrator rights (gh pr merge --admin), so a docs sync
# deploys without a manual merge. Nothing is merged unless site.yml passed.
#
# Usage: sync-docs-merge.sh [BRANCH]  (default: docs-sync)
#
# Needs GH_TOKEN: a token allowed to bypass branch protection (the
# SYNC_MERGE_TOKEN secret in CI; github.token cannot use --admin) and, outside
# this repository, GH_REPO=owner/repo. Run it through make (docs-sync-merge).
set -euo pipefail
branch="${1:-docs-sync}"

pr="$(gh pr list --head "$branch" --base master --state open --json number --jq '.[0].number // empty')"
if [ -z "$pr" ]; then
  echo "No open pull request for $branch; nothing to merge."
  exit 0
fi

sha="$(gh pr view "$pr" --json headRefOid --jq .headRefOid)"
run=""
for _ in $(seq 1 30); do
  run="$(gh run list --workflow site.yml --branch "$branch" --commit "$sha" \
    --limit 1 --json databaseId --jq '.[0].databaseId // empty')"
  [ -n "$run" ] && break
  sleep 10
done
if [ -z "$run" ]; then
  echo "site.yml did not start on $sha; not merging." >&2
  exit 1
fi

gh run watch "$run" --exit-status
gh pr merge "$pr" --squash --admin --delete-branch --match-head-commit "$sha"
