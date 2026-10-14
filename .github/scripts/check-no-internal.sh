#!/usr/bin/env bash
# Fail when a public build contains the /internal/ section or links to it.
# Usage: check-no-internal.sh [BUILD_DIR]
set -euo pipefail
dir="${1:-public}"
test -d "$dir" || { echo "check-no-internal: $dir not found" >&2; exit 1; }
if [ -e "$dir/internal" ]; then
  echo "check-no-internal: $dir/internal exists; the internal segment leaked into the public build" >&2
  exit 1
fi
if grep -rlE '(href|src)="[^"]*/internal/|blowhorn\.ai/internal/' "$dir" >/dev/null 2>&1; then
  echo "check-no-internal: public output references /internal/:" >&2
  grep -rlE '(href|src)="[^"]*/internal/|blowhorn\.ai/internal/' "$dir" >&2
  exit 1
fi
echo "check-no-internal: $dir has no internal pages"
