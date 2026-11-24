#!/usr/bin/env bash
# Create the GitHub Release from dist/; refuses to overwrite an existing tag.
#
# Always creates a draft first, attaching the DMG and SHA256SUMS.txt. When
# DRAFT is not true, a stable release then waits for
# blowhorn-cli-X.Y.Z-macos-universal.tar.gz and its .sha256 (uploaded by
# blowhorn-ai/blowhorn during that draft window) and only then publishes with
# `gh release edit --draft=false`. A prerelease publishes without waiting for
# a tarball. When DRAFT is true, the release stays a draft. If the tarball
# never arrives, this fails and leaves the draft unpublished, so the tag
# never becomes an immutable published release without those assets.
#
# Env: GH_TOKEN, GH_REPO, VERSION (vX.Y.Z), PRERELEASE, DRAFT, GITHUB_SHA,
# optional GITHUB_STEP_SUMMARY, optional CLI_TARBALL_WAIT (seconds, default
# 1800), optional CLI_TARBALL_POLL (seconds, default 30).
# Run through make (see the dmg-* targets); publish-dmg.yml calls the same targets.
set -euo pipefail
if gh release view "$VERSION" >/dev/null 2>&1; then
  echo "::error::release $VERSION already exists; refusing to overwrite"
  exit 1
fi
versioned=(dist/Blowhorn-*-mac-*.dmg)
{
  if [[ -s dist/notes.md ]]; then cat dist/notes.md; echo; echo; fi
  echo "## Download"
  echo
  echo "- macOS: \`$(basename "${versioned[0]}")\`"
  echo "- Download: https://github.com/${GH_REPO}/releases/download/${VERSION}/$(basename "${versioned[0]}")"
  echo
  echo "## SHA-256"
  echo
  echo '```'
  cat dist/SHA256SUMS.txt
  echo '```'
} >release-notes.md
flags=(--title "Blowhorn ${VERSION}" --notes-file release-notes.md --target "${GITHUB_SHA}" --draft)
if [[ "$PRERELEASE" == "true" ]]; then
  flags+=(--prerelease --latest=false)
else
  flags+=(--latest)
fi
gh release create "$VERSION" "${flags[@]}" dist/*.dmg dist/SHA256SUMS.txt

summarize() {
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    echo "### Release ${VERSION} created (draft=${DRAFT}, prerelease=${PRERELEASE})" >>"$GITHUB_STEP_SUMMARY"
    if [[ "$DRAFT" != "true" && "$PRERELEASE" != "true" ]]; then
      echo "The pin job sets data/download.json to ${VERSION#v} and redeploys blowhorn.ai." >>"$GITHUB_STEP_SUMMARY"
    fi
  fi
}

if [[ "$DRAFT" == "true" ]]; then
  summarize
  exit 0
fi

if [[ "$PRERELEASE" == "true" ]]; then
  gh release edit "$VERSION" --draft=false
  summarize
  exit 0
fi

bare="${VERSION#v}"
tarball="blowhorn-cli-${bare}-macos-universal.tar.gz"
shafile="${tarball}.sha256"
WAIT="${CLI_TARBALL_WAIT:-1800}"
POLL="${CLI_TARBALL_POLL:-30}"
if ! [[ "$WAIT" =~ ^[0-9]+$ ]]; then
  echo "::error::CLI_TARBALL_WAIT must be seconds (got '$WAIT')"
  exit 1
fi
if ! [[ "$POLL" =~ ^[1-9][0-9]*$ ]]; then
  echo "::error::CLI_TARBALL_POLL must be a positive integer (got '$POLL')"
  exit 1
fi

draft_has_cli_tarball() {
  local out
  out="$(gh release view "$VERSION" --json isDraft,assets \
    --jq "select(.isDraft == true) | [.assets[].name] | (index(\"${tarball}\") != null and index(\"${shafile}\") != null)" 2>/dev/null || true)"
  [[ "$out" == "true" ]]
}

waited=0
until draft_has_cli_tarball; do
  if [[ "$waited" -ge "$WAIT" ]]; then
    echo "::error::draft ${VERSION} has no ${tarball} (and ${shafile}) after ${WAIT}s; leaving it a draft so it is not published immutable without the CLI assets. The product repo uploads them with tools/scripts/release/publish-cli-formula.sh."
    exit 1
  fi
  echo "waiting for ${tarball} on draft ${VERSION} (${waited}s of ${WAIT}s)"
  sleep "$POLL"
  waited=$((waited + POLL))
done

gh release edit "$VERSION" --draft=false
summarize
