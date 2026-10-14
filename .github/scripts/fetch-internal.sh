#!/usr/bin/env bash
# Copy the internal section from a leecalcote/blowhorn checkout into this
# working tree for `hugo --environment internal`. The copies are gitignored
# and must never be committed: this repository is public.
# Usage: fetch-internal.sh SOURCE_DIR   (a leecalcote/blowhorn checkout)
set -euo pipefail
src="${1:?usage: fetch-internal.sh path/to/leecalcote/blowhorn}"
root="$(cd "$(dirname "$0")/../.." && pwd)"
hugo_src="$src/marketing/strategy/hugo"
test -d "$hugo_src" || { echo "fetch-internal: $hugo_src not found" >&2; exit 1; }
dest="$root/content/en/internal"
# Keep the committed placeholder _index.md; replace everything else.
find "$dest" -mindepth 1 -not -name _index.md -exec rm -rf {} + 2>/dev/null || true
cp -R "$hugo_src/strategy" "$hugo_src/finance" "$dest/"
fin="$src/marketing/strategy/finance"
cp "$fin/blowhorn-breakeven-model.xlsx" "$dest/finance/"
# The generator scripts ride along as downloadable files.
mkdir -p "$dest/finance/build"
cp "$fin"/build/*.py "$fin"/build/*.sh "$fin"/build/*.css "$dest/finance/build/"
mkdir -p "$dest/finance/report"
{ printf -- '---\ntitle: "Break-even report"\nlayout: internal-raw\noutputs: [HTML]\n---\n'; cat "$fin/blowhorn-breakeven.html"; } > "$dest/finance/report/index.html"
cp "$src/docs/capability-comparison/compare-assistants.csv" "$dest/strategy/compare/"
echo "fetch-internal: copied internal section from $src"
