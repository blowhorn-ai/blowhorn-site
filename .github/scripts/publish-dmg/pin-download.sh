#!/usr/bin/env bash
# After a public desktop release, pin blowhorn.ai's downloads to it: set
# data/download.json to VERSION on master, push, and start site.yml so the
# site redeploys (a push made with github.token starts no workflow).
#
# Every download URL on the site is built from data/download.json, never from
# /releases/latest, because blowhorn-axi releases on this repository can hold
# GitHub's Latest. A draft or a prerelease changes nothing, and so does a
# version that is not newer than the one already pinned, so a rerun or a late
# re-publish of an older release never moves the site backwards.
#
# Run in a checkout of master that can push to origin.
# Inputs (environment): VERSION (v1.2.3, as resolve.sh validated it), DRAFT and
# PRERELEASE (true|false), GH_TOKEN (github.token in CI).
set -euo pipefail
: "${VERSION:?VERSION is required}"
if [ "${DRAFT:-true}" != "false" ] || [ "${PRERELEASE:-true}" != "false" ]; then
  echo "pin-download: draft or prerelease; data/download.json unchanged"
  exit 0
fi
want="${VERSION#v}"
file=data/download.json

for attempt in 1 2 3; do
  git fetch -q origin master
  git checkout -q -B master origin/master
  have=$(jq -r .version "$file")
  if [ "$have" = "$want" ]; then
    echo "pin-download: $file already pins $want"
    exit 0
  fi
  if [ "$(printf '%s\n%s\n' "$have" "$want" | sort -V | tail -n1)" = "$have" ]; then
    echo "pin-download: $file pins $have, newer than $want; unchanged"
    exit 0
  fi
  printf '{"$schema":"../schemas/download.schema.json","version":"%s"}' "$want" >"$file"
  git add "$file"
  git commit -q -s -m "Pin blowhorn.ai downloads to v$want" -m "publish-dmg.yml published v$want, so data/download.json moves from $have to $want."
  if git push -q origin HEAD:master; then
    echo "pin-download: $file $have -> $want pushed"
    exec gh workflow run site.yml --ref master
  fi
  echo "pin-download: push rejected (attempt $attempt); refetching"
done
echo "::error::pin-download: could not push the $file bump to $want"
exit 1
