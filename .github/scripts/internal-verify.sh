#!/usr/bin/env bash
# Fail unless unauthenticated requests to the internal hostname are stopped by
# Cloudflare Access: every probe must answer with a redirect to the Access
# login on <team>.cloudflareaccess.com, never a 2xx. A 403 from the Worker's
# own token check also fails this: it means Access is not in front.
# Usage: internal-verify.sh [HOST]   (TEAM_DOMAIN optional: when set, the
# redirect must go to that team domain). Prints status codes only, never a body.
# Exit 1: a probe was not stopped by Access. Exit 2: a probe got a 2xx.
set -euo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
host="${1:-$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["hostname"])' "$root/internal-worker/access.json")}"
# The root, the section, a known deep link, an asset, a guessed URL, and a
# path-normalization trick. Nothing here names an internal page beyond what
# this public repository already documents.
paths=(/ /index.html /internal/ /internal/finance/report/ /favicon.ico /internal/does-not-exist/ /%2e%2e/internal/ /internal/index.xml)
fail=0
served=0
for p in "${paths[@]}"; do
  # curl still prints the -w line when it fails (000), so never append to it.
  out="$(curl -sS --path-as-is -o /dev/null --max-time 20 -w '%{http_code} %{redirect_url}' "https://$host$p" 2>/dev/null)" || true
  [ -n "$out" ] || out="000 "
  code="${out%% *}"
  loc="${out#* }"
  loc_host="$(printf '%s' "$loc" | sed -E 's#^https?://([^/]+).*#\1#')"
  verdict=FAIL
  case "$code" in
    301|302|303|307|308)
      if [[ "$loc_host" == *.cloudflareaccess.com ]] && { [ -z "${TEAM_DOMAIN:-}" ] || [ "$loc_host" = "$TEAM_DOMAIN" ]; }; then verdict=ok; fi ;;
  esac
  printf '%-5s %s %s -> %s\n' "$verdict" "$code" "$p" "${loc_host:-no redirect}"
  [ "$verdict" = ok ] || fail=1
  case "$code" in 2*) served=1 ;; esac
done
if [ "$served" -ne 0 ]; then
  echo "internal-verify: $host answered an unauthenticated request with 2xx" >&2
  exit 2
fi
if [ "$fail" -ne 0 ]; then
  echo "internal-verify: an unauthenticated request was not stopped by Cloudflare Access on $host" >&2
  exit 1
fi
echo "internal-verify: every unauthenticated probe of $host was stopped by Access"
