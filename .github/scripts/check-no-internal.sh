#!/usr/bin/env bash
# Fail when a public build, or this repository's tracked files, carry the
# internal section. Usage: check-no-internal.sh [BUILD_DIR]
set -euo pipefail
dir="${1:-public}"
root="$(cd "$(dirname "$0")/../.." && pwd)"
test -d "$dir" || { echo "check-no-internal: $dir not found" >&2; exit 1; }
fail=0
if [ -e "$dir/internal" ]; then
  echo "check-no-internal: $dir/internal exists; the internal segment leaked into the public build" >&2
  fail=1
fi
# Links to /internal/ and the names of the internal files.
pattern='(href|src)="[^"]*/internal/|blowhorn\.ai/internal/|blowhorn-breakeven|compare-assistants|crowd-amplification|gtm-strategy|product-entitlement-requirements|marketing/strategy'
if hits="$(grep -rlE "$pattern" "$dir")"; then
  echo "check-no-internal: public output references internal material:" >&2
  echo "$hits" >&2
  fail=1
fi
# Nothing fetched for the internal build may be tracked by git.
if git -C "$root" rev-parse --git-dir >/dev/null 2>&1; then
  tracked="$(git -C "$root" ls-files content/en/internal | grep -v '^content/en/internal/_index.md$' || true)"
  if [ -n "$tracked" ]; then
    echo "check-no-internal: internal files are committed to this public repository:" >&2
    echo "$tracked" >&2
    fail=1
  fi
fi
[ "$fail" -eq 0 ] && echo "check-no-internal: $dir and the repository carry no internal material"
exit "$fail"
