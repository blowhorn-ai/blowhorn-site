#!/usr/bin/env bash
# Regenerate the product's CLI reference pages before the docs sync copies them.
#
# The pages in a blowhorn checkout's docs/reference/cli/ (and the
# command table in docs/reference/cli.md) are generated from its CLI schema
# bundles. A ref that has the Rust generator (engine/rust/xtask/src/docs.rs) runs
# `tools/bin/xtask.sh docs cli-reference`; an older ref runs the Python
# release/scripts/cli_reference/build.py. Running it here, at the ref being
# synced, means a page that was not regenerated before its commit can never be
# published stale. A ref from before any generator existed keeps the pages it has.
#
# Usage: docs-cli-reference.sh [SOURCE_DIR]  (default: product)
#
# The Rust generator needs the product's pinned toolchain installed (sync-docs.yml
# installs it from engine/rust/rust-toolchain.toml); the Python one needs typer
# and PyYAML on PYTHON (default python3).
set -euo pipefail
source_dir="${1:-product}"
python="${PYTHON:-python3}"
xtask="$source_dir/tools/bin/xtask.sh"
rust_generator="$source_dir/engine/rust/xtask/src/docs.rs"
build="$source_dir/release/scripts/cli_reference/build.py"
if [ -f "$rust_generator" ] && [ -x "$xtask" ]; then
  exec "$xtask" docs cli-reference
fi
if [ -f "$build" ]; then
  exec "$python" "$build"
fi
echo "docs-cli-reference: no generator at this ref; syncing the pages it has"
