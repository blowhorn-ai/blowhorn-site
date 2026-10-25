#!/usr/bin/env bash
# Merge the docs-sync pull request once its site checks pass, then start
# the master site run that deploys the merged docs.
#
# Why not GitHub's own auto-merge: master has no branch protection, so
# auto-merge has no required checks to wait for and would merge at once —
# before the site run the sync started on the branch has even registered.
# That dispatched run is the only gate, so the merge waits for it here:
# gate on the dispatched site.yml run itself (see below), and merge
# (squash) only when that run succeeds on the pull request's current
# head. A failed run merges nothing: this script stops, and the pull
# request stays open for a human.
#
# Why the second dispatch: the merge is made with github.token, and a
# push to master made by that token never starts push workflows, so
# site.yml would stay silent on the merge and nothing would deploy. A
# workflow_dispatch run started with the same token is allowed, and on
# master it deploys (site.yml's deploy job runs for any event that is not
# a pull request). The same trick as sync-docs-start-checks.sh, one ref
# later. Run it through make (see the docs-sync-merge target);
# sync-docs.yml calls the same target.
#
# Usage: sync-docs-merge.sh [BRANCH]  (default: docs-sync)
#
# Needs GH_TOKEN (github.token in CI) and, outside this repository,
# GH_REPO=owner/repo so gh knows which repository to act in.
set -euo pipefail
branch="${1:-docs-sync}"

read -r pr state head <<< "$(gh pr view "$branch" --json number,state,headRefOid --jq '"\(.number) \(.state) \(.headRefOid)"')"
if [ "$state" != "OPEN" ]; then
  echo "Sync pull request #$pr is $state, not OPEN; nothing to merge."
  exit 0
fi

# Gate on the dispatched site run itself, not on the pull request's
# checks. A workflow_dispatch run attaches to the branch head but does
# NOT appear as a pull request check, so the old wait — watch for the
# site check "Lint, build and check" to show up on the pull request —
# always timed out after 30x10s even on a green branch run (seen live
# three times, 2026-10-23 and 2026-10-25), while a plain check watch
# started too early sees only the instantly-passing DCO check and
# merges past the very gate this script exists to enforce (seen live,
# 2026-10-23). The run is matched to the pull request's current head,
# so a stale green run from an earlier head cannot merge untested docs.
# latest_run prints "<databaseId> <status> <conclusion>" for the newest
# workflow_dispatch site.yml run on this branch at the given head, or
# nothing when no such run has registered yet.
latest_run() {
  # gh's --jq takes a jq expression, not jq's --arg, so the head SHA
  # (hex, straight from gh pr view) is interpolated into the expression.
  gh run list --workflow site.yml --branch "$branch" --event workflow_dispatch \
    --limit 20 --json databaseId,headSha,status,conclusion,createdAt \
    --jq "[.[] | select(.headSha == \"$head\")] | sort_by(.createdAt) | last
     | select(.) | \"\(.databaseId) \(.status) \(.conclusion)\"" 2>/dev/null
}
run_id=""
for _ in $(seq 1 20); do
  run_id=$(latest_run | awk '{print $1}')
  [ -n "$run_id" ] && break
  sleep 30
done
if [ -z "$run_id" ]; then
  echo "No workflow_dispatch site run for pull request #$pr head $head appeared; not merging."
  exit 1
fi
echo "Dispatched site run $run_id for pull request #$pr head $head."
for _ in $(seq 1 60); do
  read -r _ status conclusion <<< "$(latest_run)"
  [ "$status" = "completed" ] && break
  sleep 30
done
if [ "$status" != "completed" ]; then
  echo "Dispatched site run $run_id did not complete; not merging."
  exit 1
fi
if [ "$conclusion" != "success" ]; then
  echo "Dispatched site run $run_id concluded $conclusion; not merging."
  exit 1
fi

# Exits non-zero unless every check on the pull request passes.
# This is a second gate, not the site gate: the site run above already
# passed, so a watch started now cannot merge past it the way an early
# watch could. It covers the checks that do attach, such as DCO.
gh pr checks "$pr" --watch --interval 10

gh pr merge "$pr" --squash

# The token's merge starts no push workflows (see header): start the
# site run on master that deploys the merged docs.
exec gh workflow run site.yml --ref master
