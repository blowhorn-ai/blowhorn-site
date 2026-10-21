// Serves the internal site (public-internal/) only to requests that carry a
// valid Cloudflare Access token for this application. Access already sits in
// front of the hostname; this check means a missing or misconfigured Access
// application fails closed instead of exposing the site. Every request runs
// this code first (assets.run_worker_first), assets included. The root
// path serves the /internal/ table of contents.
//
// Deploy-time vars (set by .github/scripts/internal-deploy.sh):
//   TEAM_DOMAIN     <team>.cloudflareaccess.com (the Access auth domain)
//   POLICY_AUD      the Access application's audience tag
//   ALLOWED_EMAILS  comma-separated allow list (internal-worker/access.json)

const CERTS_TTL_MS = 10 * 60 * 1000;
let certsCache = { url: '', keys: null, fetchedAt: 0 };

const DENY_HEADERS = {
  'content-type': 'text/plain; charset=utf-8',
  'cache-control': 'no-store',
  'x-robots-tag': 'noindex, nofollow',
};

function deny(status = 403) {
  return new Response(status === 403 ? 'Forbidden\n' : 'Unavailable\n', { status, headers: DENY_HEADERS });
}

function b64urlToBytes(s) {
  const pad = s.length % 4 === 0 ? '' : '='.repeat(4 - (s.length % 4));
  const bin = atob(s.replace(/-/g, '+').replace(/_/g, '/') + pad);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function decodeJson(part) {
  return JSON.parse(new TextDecoder().decode(b64urlToBytes(part)));
}

async function accessKeys(teamDomain, fetchImpl) {
  const url = `https://${teamDomain}/cdn-cgi/access/certs`;
  const now = Date.now();
  if (certsCache.url === url && certsCache.keys && now - certsCache.fetchedAt < CERTS_TTL_MS) {
    return certsCache.keys;
  }
  const res = await fetchImpl(url);
  if (!res.ok) throw new Error('certs unavailable');
  const body = await res.json();
  certsCache = { url, keys: body.keys || [], fetchedAt: now };
  return certsCache.keys;
}

export function resetCertsCache() {
  certsCache = { url: '', keys: null, fetchedAt: 0 };
}

function tokenFrom(request) {
  const header = request.headers.get('cf-access-jwt-assertion');
  if (header) return header;
  const cookie = request.headers.get('cookie') || '';
  const m = cookie.match(/(?:^|;\s*)CF_Authorization=([^;]+)/);
  return m ? m[1] : '';
}

// Returns the verified claims, or null.
export async function verifyAccessToken(token, env, fetchImpl = fetch, nowSec = Math.floor(Date.now() / 1000)) {
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  let header;
  let claims;
  try {
    header = decodeJson(parts[0]);
    claims = decodeJson(parts[1]);
  } catch {
    return null;
  }
  if (header.alg !== 'RS256' || !header.kid) return null;
  const keys = await accessKeys(env.TEAM_DOMAIN, fetchImpl);
  const jwk = keys.find((k) => k.kid === header.kid);
  if (!jwk) return null;
  const key = await crypto.subtle.importKey(
    'jwk',
    { kty: jwk.kty, n: jwk.n, e: jwk.e, alg: 'RS256', ext: true },
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
    false,
    ['verify'],
  );
  const ok = await crypto.subtle.verify(
    'RSASSA-PKCS1-v1_5',
    key,
    b64urlToBytes(parts[2]),
    new TextEncoder().encode(`${parts[0]}.${parts[1]}`),
  );
  if (!ok) return null;
  const aud = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  if (!aud.includes(env.POLICY_AUD)) return null;
  if (claims.iss !== `https://${env.TEAM_DOMAIN}`) return null;
  if (typeof claims.exp !== 'number' || claims.exp <= nowSec) return null;
  if (typeof claims.nbf === 'number' && claims.nbf > nowSec + 60) return null;
  const allowed = String(env.ALLOWED_EMAILS || '')
    .split(',')
    .map((e) => e.trim().toLowerCase())
    .filter(Boolean);
  const email = String(claims.email || '').toLowerCase();
  if (!email || !allowed.includes(email)) return null;
  return claims;
}

export async function handle(request, env, fetchImpl = fetch) {
  if (!env.TEAM_DOMAIN || !env.POLICY_AUD || !env.ALLOWED_EMAILS) return deny(503);
  const token = tokenFrom(request);
  if (!token) return deny();
  let claims = null;
  try {
    claims = await verifyAccessToken(token, env, fetchImpl);
  } catch {
    return deny(503);
  }
  if (!claims) return deny();
  // The root serves the generated table of contents (/internal/), not the
  // build's local-preview redirect page.
  const url = new URL(request.url);
  const assetRequest = url.pathname === '/' || url.pathname === '/index.html'
    ? new Request(new URL('/internal/', url), request)
    : request;
  const res = await env.ASSETS.fetch(assetRequest);
  const out = new Response(res.body, res);
  out.headers.set('cache-control', 'private, no-store');
  out.headers.set('x-robots-tag', 'noindex, nofollow');
  return out;
}

export default {
  fetch(request, env) {
    return handle(request, env);
  },
};
