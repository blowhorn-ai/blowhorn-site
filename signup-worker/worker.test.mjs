// node --test signup-worker/worker.test.mjs: the signup API stores, dedupes,
// unsubscribes and rate-limits, with an in-memory fake for the db adapter.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import worker, {
  createHandler,
  createScheduledHandler,
  d1Db,
  THANKS_URL,
  safeBackLink,
  escHtml,
  safeHtml,
  pageResponse,
  MAX_BODY_BYTES,
} from './src/worker.js';

function fakeDb() {
  const rows = new Map();
  const byToken = new Map();
  const hits = new Map();
  const key = (email, kind, topic) => `${email}|${kind}|${topic ?? ''}`;
  return {
    rows,
    byToken,
    hits,
    async getSignup(email, kind, topic) {
      return rows.get(key(email, kind, topic)) || null;
    },
    async insertSignup(row) {
      const full = { ...row, unsubscribed_at: null };
      rows.set(key(row.email, row.kind, row.topic), full);
      byToken.set(row.token, full);
    },
    async updateSignup(row) {
      const full = rows.get(key(row.email, row.kind, row.topic));
      full.remark = row.remark;
      full.source_page = row.source_page;
      full.unsubscribed_at = null;
    },
    async rateHit(ip, window) {
      const k = `${ip}|${window}`;
      const next = (hits.get(k) || 0) + 1;
      hits.set(k, next);
      return next;
    },
    async pruneRateLimits(cutoff) {
      for (const [k] of hits) {
        const parts = k.split('|');
        const win = Number(parts[1]);
        if (win < cutoff) {
          hits.delete(k);
        }
      }
    },
    async getByToken(token) {
      return byToken.get(token) || null;
    },
    async markUnsubscribed(token) {
      const row = byToken.get(token);
      if (row) row.unsubscribed_at = '2026-10-27T00:00:00.000Z';
    },
    supportRows: [],
    async insertSupportMessage(row) {
      const full = { ...row, id: this.supportRows.length + 1, forwarded_at: null };
      this.supportRows.push(full);
      return full.id;
    },
    async markSupportForwarded(id) {
      const row = this.supportRows.find((r) => r.id === id);
      if (row) row.forwarded_at = '2026-11-20T00:00:00.000Z';
    },
  };
}

function post(path, body, headers = {}) {
  return new Request(`https://api.blowhorn.ai${path}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', ...headers },
    body: JSON.stringify(body),
  });
}

function formPost(path, fields) {
  const params = new URLSearchParams(fields);
  return new Request(`https://api.blowhorn.ai${path}`, {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: params.toString(),
  });
}

test('waitlist signup stores one row, lowercased and trimmed', async () => {
  const db = fakeDb();
  const res = await createHandler(db)(
    post('/api/waitlist', { email: '  Alex@Example.com ', topic: 'tiktok', remark: 'shorts', source_page: '/docs/reference/platforms/tiktok/' }),
  );
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true });
  const row = await db.getSignup('alex@example.com', 'waitlist', 'tiktok');
  assert.equal(row.remark, 'shorts');
  assert.equal(row.topic, 'tiktok');
  assert.equal(row.source_page, '/docs/reference/platforms/tiktok/');
  assert.ok(row.token.length >= 32);
});

test('newsletter signup has no topic and never touches the waitlist', async () => {
  const db = fakeDb();
  const handle = createHandler(db);
  await handle(post('/api/subscribe', { email: 'alex@example.com' }));
  const row = await db.getSignup('alex@example.com', 'newsletter', null);
  assert.equal(row.kind, 'newsletter');
  assert.equal(row.topic, null);
  assert.equal(await db.getSignup('alex@example.com', 'waitlist', null), null);
});

test('signing up twice refreshes the remark instead of adding a row', async () => {
  const db = fakeDb();
  const handle = createHandler(db);
  await handle(post('/api/waitlist', { email: 'a@b.co', topic: 'tiktok', remark: 'first' }));
  await handle(post('/api/waitlist', { email: 'a@b.co', topic: 'tiktok', remark: 'second' }));
  assert.equal(db.rows.size, 1);
  assert.equal((await db.getSignup('a@b.co', 'waitlist', 'tiktok')).remark, 'second');
});

test('re-signup after unsubscribe clears the unsubscribe', async () => {
  const db = fakeDb();
  const handle = createHandler(db);
  await handle(post('/api/waitlist', { email: 'a@b.co', topic: 'tiktok' }));
  const row = await db.getSignup('a@b.co', 'waitlist', 'tiktok');
  await handle(formPost('/api/unsubscribe', { token: row.token }));
  assert.ok((await db.getSignup('a@b.co', 'waitlist', 'tiktok')).unsubscribed_at);
  await handle(post('/api/waitlist', { email: 'a@b.co', topic: 'tiktok' }));
  assert.equal((await db.getSignup('a@b.co', 'waitlist', 'tiktok')).unsubscribed_at, null);
});

test('invalid email, bad topic and long remark are 400s and store nothing', async () => {
  const db = fakeDb();
  const handle = createHandler(db);
  for (const body of [
    { email: 'not-an-email', topic: 'tiktok' },
    { email: 'a@b.co', topic: 'TikTok!' },
    { email: 'a@b.co', topic: 'tiktok', remark: 'x'.repeat(501) },
  ]) {
    const res = await handle(post('/api/waitlist', body));
    assert.equal(res.status, 400);
    assert.equal((await res.json()).ok, false);
  }
  assert.equal(db.rows.size, 0);
});

test('honeypot answers success without storing', async () => {
  const db = fakeDb();
  const res = await createHandler(db)(
    post('/api/waitlist', { email: 'bot@spam.test', topic: 'tiktok', website: 'http://spam' }),
  );
  assert.equal(res.status, 200);
  assert.equal(db.rows.size, 0);
});

test('form posts redirect to the thanks page on success', async () => {
  const db = fakeDb();
  const res = await createHandler(db)(
    formPost('/api/waitlist', { email: 'a@b.co', topic: 'tiktok' }),
  );
  assert.equal(res.status, 303);
  assert.equal(res.headers.get('location'), THANKS_URL);
});

test('unsubscribe without a token says the link is incomplete', async () => {
  const db = fakeDb();
  const res = await createHandler(db)(new Request('https://api.blowhorn.ai/api/unsubscribe'));
  assert.equal(res.status, 400);
  const text = await res.text();
  assert.match(text, /incomplete/);
  assert.doesNotMatch(text, /You are unsubscribed/);
});

test('unsubscribe with an unknown token says the link is not recognized', async () => {
  const db = fakeDb();
  const res = await createHandler(db)(new Request('https://api.blowhorn.ai/api/unsubscribe?token=nope'));
  assert.equal(res.status, 404);
  const text = await res.text();
  assert.match(text, /not recognized/);
  assert.doesNotMatch(text, /You are unsubscribed/);
});

test('31st request in a minute is rate limited', async () => {
  const db = fakeDb();
  const handle = createHandler(db);
  let last;
  for (let i = 0; i < 31; i++) {
    last = await handle(post('/api/subscribe', { email: `u${i}@b.co` }, { 'cf-connecting-ip': '203.0.113.7' }));
  }
  assert.equal(last.status, 429);
});

test('unknown paths are 404 without touching the store', async () => {
  const db = fakeDb();
  const res = await createHandler(db)(new Request('https://api.blowhorn.ai/api/nope'));
  assert.equal(res.status, 404);
  assert.equal(db.rows.size, 0);
});

test('GET /api/unsubscribe renders confirmation without mutating state', async () => {
  const db = fakeDb();
  const handle = createHandler(db);
  await handle(post('/api/waitlist', { email: 'user@example.com', topic: 'tiktok' }));
  const row = await db.getSignup('user@example.com', 'waitlist', 'tiktok');

  const res = await handle(new Request(`https://api.blowhorn.ai/api/unsubscribe?token=${row.token}`));
  assert.equal(res.status, 200);
  const text = await res.text();
  assert.match(text, /Confirm unsubscribe/);

  const refreshed = await db.getByToken(row.token);
  assert.equal(refreshed.unsubscribed_at, null);
});

test('POST /api/unsubscribe marks the subscriber as unsubscribed', async () => {
  const db = fakeDb();
  const handle = createHandler(db);
  await handle(post('/api/waitlist', { email: 'user@example.com', topic: 'tiktok' }));
  const row = await db.getSignup('user@example.com', 'waitlist', 'tiktok');

  const res = await handle(formPost('/api/unsubscribe', { token: row.token }));
  assert.equal(res.status, 200);
  const text = await res.text();
  assert.match(text, /You are unsubscribed/);

  const refreshed = await db.getByToken(row.token);
  assert.ok(refreshed.unsubscribed_at);
});

test('POST /api/unsubscribe with missing or unknown token returns 400 or 404', async () => {
  const db = fakeDb();
  const handle = createHandler(db);

  const resMissing = await handle(new Request('https://api.blowhorn.ai/api/unsubscribe', { method: 'POST' }));
  assert.equal(resMissing.status, 400);
  assert.match(await resMissing.text(), /incomplete/);

  const resUnknown = await handle(formPost('/api/unsubscribe', { token: 'nope' }));
  assert.equal(resUnknown.status, 404);
  assert.match(await resUnknown.text(), /not recognized/);
});

test('POST /api/unsubscribe is safe to repeat', async () => {
  const db = fakeDb();
  const handle = createHandler(db);
  await handle(post('/api/waitlist', { email: 'user@example.com', topic: 'tiktok' }));
  const row = await db.getSignup('user@example.com', 'waitlist', 'tiktok');

  const first = await handle(formPost('/api/unsubscribe', { token: row.token }));
  assert.equal(first.status, 200);

  const second = await handle(formPost('/api/unsubscribe', { token: row.token }));
  assert.equal(second.status, 200);
  assert.match(await second.text(), /You are unsubscribed/);
});

test('GET /api/unsubscribe on an already unsubscribed token shows unsubscribed', async () => {
  const db = fakeDb();
  const handle = createHandler(db);
  await handle(post('/api/waitlist', { email: 'user@example.com', topic: 'tiktok' }));
  const row = await db.getSignup('user@example.com', 'waitlist', 'tiktok');
  await handle(formPost('/api/unsubscribe', { token: row.token }));

  const res = await handle(new Request(`https://api.blowhorn.ai/api/unsubscribe?token=${row.token}`));
  assert.equal(res.status, 200);
  const text = await res.text();
  assert.match(text, /You are unsubscribed/);
});

test('GET /api/unsubscribe with missing or unknown token returns 400 or 404', async () => {
  const db = fakeDb();
  const handle = createHandler(db);

  const resMissing = await handle(new Request('https://api.blowhorn.ai/api/unsubscribe'));
  assert.equal(resMissing.status, 400);
  assert.match(await resMissing.text(), /incomplete/);

  const resUnknown = await handle(new Request('https://api.blowhorn.ai/api/unsubscribe?token=nope'));
  assert.equal(resUnknown.status, 404);
  assert.match(await resUnknown.text(), /not recognized/);
});

test('safeBackLink accepts clean relative paths and rejects attribute-breaking or external inputs', () => {
  assert.equal(safeBackLink('/pricing/'), 'https://blowhorn.ai/pricing/');
  assert.equal(safeBackLink('/docs/reference/platforms/x/'), 'https://blowhorn.ai/docs/reference/platforms/x/');
  assert.equal(safeBackLink('//evil.com'), 'https://blowhorn.ai');
  assert.equal(safeBackLink('/\\evil.com'), 'https://blowhorn.ai');
  assert.equal(safeBackLink('/" onmouseover="alert(1)'), 'https://blowhorn.ai');
  assert.equal(safeBackLink("/' onmouseover='alert(1)"), 'https://blowhorn.ai');
  assert.equal(safeBackLink('/path with spaces'), 'https://blowhorn.ai');
  assert.equal(safeBackLink('/path<script>'), 'https://blowhorn.ai');
  assert.equal(safeBackLink('https://evil.com'), 'https://blowhorn.ai');
  assert.equal(safeBackLink(null), 'https://blowhorn.ai');
  assert.equal(safeBackLink(undefined), 'https://blowhorn.ai');
});

test('form post error escapes HTML and protects Go back link from attribute injection', async () => {
  const db = fakeDb();
  const handle = createHandler(db);

  // Clean path produces correct link
  const resClean = await handle(formPost('/api/waitlist', {
    email: 'bad-email',
    topic: 'tiktok',
    source_page: '/docs/reference/',
  }));
  assert.equal(resClean.status, 400);
  const textClean = await resClean.text();
  assert.match(textClean, /<a href="https:\/\/blowhorn\.ai\/docs\/reference\/">Go back<\/a>/);

  // Malicious path cannot break out of href attribute
  const resMalicious = await handle(formPost('/api/waitlist', {
    email: 'bad-email',
    topic: 'tiktok',
    source_page: '/" onmouseover="alert(1)',
  }));
  assert.equal(resMalicious.status, 400);
  const textMalicious = await resMalicious.text();
  assert.doesNotMatch(textMalicious, /onmouseover/);
  assert.match(textMalicious, /<a href="https:\/\/blowhorn\.ai">Go back<\/a>/);
});

test('pageResponse structurally escapes title and plain body, preserving safeHtml', async () => {
  const req = new Request('https://api.blowhorn.ai/api/test');

  // Plain strings in title and body are escaped by default
  const resPlain = pageResponse(req, 400, 'Alert <script>', 'Error & "quotes"');
  const textPlain = await resPlain.text();
  assert.match(textPlain, /<title>Alert &lt;script&gt;<\/title>/);
  assert.match(textPlain, /<h1>Alert &lt;script&gt;<\/h1>/);
  assert.match(textPlain, /<p>Error &amp; &quot;quotes&quot;<\/p>/);

  // safeHtml wrapper is preserved for trusted markup
  const resHtml = pageResponse(req, 200, 'Clean Title', safeHtml('<b>formatted</b>'));
  const textHtml = await resHtml.text();
  assert.match(textHtml, /<title>Clean Title<\/title>/);
  assert.match(textHtml, /<p><b>formatted<\/b><\/p>/);
});

test('rate limiter failure on GET /api/unsubscribe returns HTML error page', async () => {
  const db = fakeDb();
  db.rateHit = async () => {
    throw new Error('D1 connection failure');
  };
  const handle = createHandler(db);

  const res = await handle(new Request('https://api.blowhorn.ai/api/unsubscribe?token=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'));
  assert.equal(res.status, 500);
  assert.equal(res.headers.get('content-type'), 'text/html; charset=utf-8');
  const text = await res.text();
  assert.match(text, /Something went wrong/);
  assert.match(text, /Try again shortly/);
  assert.doesNotMatch(text, /{"ok":false/);
});

test('rate limiter failure on other requests retains existing response behavior', async () => {
  const db = fakeDb();
  db.rateHit = async () => {
    throw new Error('D1 connection failure');
  };
  const handle = createHandler(db);

  // Normal JSON signup request returns JSON 500
  const jsonRes = await handle(post('/api/subscribe', { email: 'user@example.com' }));
  assert.equal(jsonRes.status, 500);
  assert.equal(jsonRes.headers.get('content-type'), 'application/json; charset=utf-8');
  assert.deepEqual(await jsonRes.json(), { ok: false, error: 'Something went wrong.' });

  // Unsubscribe POST form request returns HTML 500 form error page
  const formRes = await handle(formPost('/api/unsubscribe', { token: '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef' }));
  assert.equal(formRes.status, 500);
  assert.equal(formRes.headers.get('content-type'), 'text/html; charset=utf-8');
  const formText = await formRes.text();
  assert.match(formText, /Something went wrong/);
  assert.match(formText, /Go back/);
});

test('signup responses include security headers for MIME, frame and referrer protection', async () => {
  const handler = createHandler(fakeDb());

  // JSON API response
  const jsonRes = await handler(post('/api/newsletter', {
    email: 'valid@example.com',
  }));
  assert.equal(jsonRes.headers.get('x-content-type-options'), 'nosniff');
  assert.equal(jsonRes.headers.get('x-frame-options'), 'DENY');
  assert.equal(jsonRes.headers.get('referrer-policy'), 'strict-origin-when-cross-origin');

  // HTML page response (e.g. 400 error page)
  const errRes = await handler(formPost('/api/newsletter', {
    email: 'invalid-email',
  }));
  assert.equal(errRes.headers.get('x-content-type-options'), 'nosniff');
  assert.equal(errRes.headers.get('x-frame-options'), 'DENY');
  assert.equal(errRes.headers.get('referrer-policy'), 'strict-origin-when-cross-origin');

  // 404 response
  const notFoundRes = await handler(new Request('https://api.blowhorn.ai/unknown'));
  assert.equal(notFoundRes.headers.get('x-content-type-options'), 'nosniff');
  assert.equal(notFoundRes.headers.get('x-frame-options'), 'DENY');
  assert.equal(notFoundRes.headers.get('referrer-policy'), 'strict-origin-when-cross-origin');

  // OPTIONS preflight response
  const optionsRes = await handler(new Request('https://api.blowhorn.ai/api/waitlist', { method: 'OPTIONS' }));
  assert.equal(optionsRes.headers.get('x-content-type-options'), 'nosniff');
  assert.equal(optionsRes.headers.get('x-frame-options'), 'DENY');
  assert.equal(optionsRes.headers.get('referrer-policy'), 'strict-origin-when-cross-origin');
});

test('rateHit does not delete expired rate limits during normal request handling', async () => {
  const db = fakeDb();
  // Manually pre-seed expired buckets in fakeDb
  db.hits.set('203.0.113.10|100', 5);
  db.hits.set('203.0.113.10|101', 12);

  const handle = createHandler(db);
  // Execute a normal request in a later minute window
  const res = await handle(post('/api/subscribe', { email: 'fresh@example.com' }, { 'cf-connecting-ip': '203.0.113.10' }));
  assert.equal(res.status, 200);

  // Past buckets must still exist because rateHit no longer executes cleanup
  assert.equal(db.hits.get('203.0.113.10|100'), 5);
  assert.equal(db.hits.get('203.0.113.10|101'), 12);
});

test('scheduled cleanup prunes expired buckets while preserving active and future buckets', async () => {
  const db = fakeDb();
  const scheduledTime = 60000000; // window 1000 exactly
  const currentWindow = Math.floor(scheduledTime / 60000); // 1000

  // Pre-seed hits across past, current, and future windows
  db.hits.set(`192.0.2.1|${currentWindow - 2}`, 10);
  db.hits.set(`192.0.2.1|${currentWindow - 1}`, 15);
  db.hits.set(`192.0.2.1|${currentWindow}`, 8);
  db.hits.set(`192.0.2.1|${currentWindow + 1}`, 3);

  const scheduledHandler = createScheduledHandler(db);
  await scheduledHandler({ scheduledTime });

  // Expired buckets (window < currentWindow) must be deleted
  assert.equal(db.hits.has(`192.0.2.1|${currentWindow - 2}`), false);
  assert.equal(db.hits.has(`192.0.2.1|${currentWindow - 1}`), false);

  // Active bucket (window === currentWindow) must survive
  assert.equal(db.hits.get(`192.0.2.1|${currentWindow}`), 8);

  // Future bucket (window > currentWindow) must survive
  assert.equal(db.hits.get(`192.0.2.1|${currentWindow + 1}`), 3);
});

test('scheduled cleanup falls back to clock when event scheduledTime is missing or invalid', async () => {
  const db = fakeDb();
  const simulatedNow = 120000000; // window 2000
  const currentWindow = Math.floor(simulatedNow / 60000); // 2000

  db.hits.set(`192.0.2.2|${currentWindow - 1}`, 4);
  db.hits.set(`192.0.2.2|${currentWindow}`, 7);

  const scheduledHandler = createScheduledHandler(db, () => simulatedNow);
  // Pass empty event without scheduledTime
  await scheduledHandler({});

  assert.equal(db.hits.has(`192.0.2.2|${currentWindow - 1}`), false);
  assert.equal(db.hits.get(`192.0.2.2|${currentWindow}`), 7);
});

test('worker.scheduled delegates to createScheduledHandler and binds env.SIGNUPS_DB', async () => {
  let prunedCutoff = null;
  const mockD1 = {
    prepare(sql) {
      return {
        bind(cutoff) {
          return {
            async run() {
              prunedCutoff = cutoff;
              return { success: true };
            },
          };
        },
      };
    },
  };

  const env = { SIGNUPS_DB: mockD1 };
  const scheduledTime = 180000000; // window 3000
  await worker.scheduled({ scheduledTime }, env);

  assert.equal(prunedCutoff, 3000);
});

test('scheduled cleanup failure does not compromise normal request handling', async () => {
  const failingDb = fakeDb();
  failingDb.pruneRateLimits = async () => {
    throw new Error('D1 transient failure');
  };

  const scheduledHandler = createScheduledHandler(failingDb);
  await assert.rejects(
    async () => {
      await scheduledHandler({ scheduledTime: Date.now() });
    },
    /D1 transient failure/,
  );

  // Normal request handling remains fully operational
  const handle = createHandler(failingDb);
  const res = await handle(post('/api/subscribe', { email: 'user@example.com' }));
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true });
});

test('real SQLite schema: migrations apply, window index is used, and d1Db pruning preserves active bucket', async () => {
  const sqlite = new DatabaseSync(':memory:');
  const __dirname = dirname(fileURLToPath(import.meta.url));
  const m1 = readFileSync(join(__dirname, 'migrations', '0001_init.sql'), 'utf8');
  const m2 = readFileSync(join(__dirname, 'migrations', '0002_rate_limits_window_idx.sql'), 'utf8');

  sqlite.exec(m1);
  sqlite.exec(m2);

  // Verify that DELETE query uses the secondary index on window
  const queryPlan = sqlite.prepare('EXPLAIN QUERY PLAN DELETE FROM rate_limits WHERE window < 1000').all();
  const planDetail = queryPlan.map((step) => step.detail).join(' ');
  assert.match(planDetail, /USING INDEX idx_rate_limits_window/);

  // Wrap DatabaseSync into the D1 interface expected by d1Db
  const d1Shim = {
    prepare(sql) {
      const stmt = sqlite.prepare(sql);
      return {
        bind(...params) {
          return {
            first() {
              return stmt.get(...params) || null;
            },
            run() {
              stmt.run(...params);
              return { success: true };
            },
            all() {
              return { results: stmt.all(...params) };
            },
          };
        },
      };
    },
  };

  const db = d1Db(d1Shim);
  const currentWindow = 500;

  // Record rate limits for expired, active, and future windows
  await db.rateHit('192.0.2.1', currentWindow - 2);
  await db.rateHit('192.0.2.1', currentWindow - 1);
  await db.rateHit('192.0.2.1', currentWindow);
  await db.rateHit('192.0.2.1', currentWindow); // count = 2
  await db.rateHit('192.0.2.1', currentWindow + 1);

  // Prune with cutoff equal to currentWindow
  await db.pruneRateLimits(currentWindow);

  const remaining = sqlite.prepare('SELECT window, count FROM rate_limits ORDER BY window ASC').all();
  assert.equal(remaining.length, 2);

  // Active bucket must survive with intact count
  assert.equal(remaining[0].window, currentWindow);
  assert.equal(remaining[0].count, 2);

  // Future bucket must survive
  assert.equal(remaining[1].window, currentWindow + 1);
  assert.equal(remaining[1].count, 1);
});

test('oversized Content-Length on JSON POST returns 413 and stores nothing', async () => {
  const db = fakeDb();
  const handler = createHandler(db);
  const req = new Request('https://api.blowhorn.ai/api/waitlist', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'content-length': '15000',
    },
    body: JSON.stringify({ email: 'oversized@example.com', topic: 'shorts' }),
  });
  const res = await handler(req);
  assert.equal(res.status, 413);
  assert.equal(res.headers.get('x-content-type-options'), 'nosniff');
  assert.equal(res.headers.get('x-frame-options'), 'DENY');
  assert.equal(res.headers.get('referrer-policy'), 'strict-origin-when-cross-origin');
  const data = await res.json();
  assert.equal(data.ok, false);
  assert.equal(data.error, 'Payload too large.');
  assert.equal(db.rows.size, 0);
});

test('oversized Content-Length on form POST returns 413 HTML error page and preserves safeBackLink', async () => {
  const db = fakeDb();
  const handler = createHandler(db);
  const params = new URLSearchParams({ email: 'oversized@example.com', source_page: '/coming-soon/' });
  const req = new Request('https://api.blowhorn.ai/api/waitlist', {
    method: 'POST',
    headers: {
      'content-type': 'application/x-www-form-urlencoded',
      'content-length': '15000',
    },
    body: params.toString(),
  });
  const res = await handler(req);
  assert.equal(res.status, 413);
  assert.equal(res.headers.get('content-type'), 'text/html; charset=utf-8');
  assert.equal(res.headers.get('x-content-type-options'), 'nosniff');
  assert.equal(res.headers.get('x-frame-options'), 'DENY');
  const html = await res.text();
  assert.match(html, /<title>Payload too large<\/title>/);
  assert.match(html, /Payload too large\./);
  assert.match(html, /<a href="https:\/\/blowhorn\.ai">Go back<\/a>/);
  assert.equal(db.rows.size, 0);
});

test('oversized raw body without Content-Length header returns 413', async () => {
  const db = fakeDb();
  const handler = createHandler(db);
  const oversizedData = 'x'.repeat(MAX_BODY_BYTES + 1);
  const req = new Request('https://api.blowhorn.ai/api/subscribe', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email: 'valid@example.com', remark: oversizedData }),
  });
  const res = await handler(req);
  assert.equal(res.status, 413);
  const data = await res.json();
  assert.equal(data.ok, false);
  assert.equal(data.error, 'Payload too large.');
  assert.equal(db.rows.size, 0);
});

test('boundary payload at exactly MAX_BODY_BYTES passes size check to validation', async () => {
  const db = fakeDb();
  const handler = createHandler(db);

  // Exact boundary: payload length equals MAX_BODY_BYTES
  const base = JSON.stringify({ email: 'test@example.com', remark: '' });
  const padLen = MAX_BODY_BYTES - new TextEncoder().encode(base).length;
  const atLimitBody = JSON.stringify({ email: 'test@example.com', remark: 'a'.repeat(padLen) });
  assert.equal(new TextEncoder().encode(atLimitBody).length, MAX_BODY_BYTES);

  const reqAtLimit = new Request('https://api.blowhorn.ai/api/subscribe', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: atLimitBody,
  });
  const resAtLimit = await handler(reqAtLimit);
  // Passes size check (not 413), fails field validation because remark is > 500 chars (400)
  assert.equal(resAtLimit.status, 400);
  const dataAtLimit = await resAtLimit.json();
  assert.match(dataAtLimit.error, /remark is too long/);

  // One byte over MAX_BODY_BYTES: rejected immediately by size check with 413
  const overLimitBody = atLimitBody + ' ';
  assert.equal(new TextEncoder().encode(overLimitBody).length, MAX_BODY_BYTES + 1);
  const reqOverLimit = new Request('https://api.blowhorn.ai/api/subscribe', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: overLimitBody,
  });
  const resOverLimit = await handler(reqOverLimit);
  assert.equal(resOverLimit.status, 413);
  const dataOverLimit = await resOverLimit.json();
  assert.equal(dataOverLimit.error, 'Payload too large.');
});

test('JSON array, primitive or malformed body returns 400 without crashing', async () => {
  const db = fakeDb();
  const handler = createHandler(db);

  // Array body
  const resArray = await handler(new Request('https://api.blowhorn.ai/api/subscribe', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(['not', 'an', 'object']),
  }));
  assert.equal(resArray.status, 400);
  const dataArray = await resArray.json();
  assert.equal(dataArray.error, 'Could not read the signup.');

  // Primitive string body
  const resString = await handler(new Request('https://api.blowhorn.ai/api/subscribe', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify('plain string'),
  }));
  assert.equal(resString.status, 400);

  // Malformed JSON syntax
  const resMalformed = await handler(new Request('https://api.blowhorn.ai/api/subscribe', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: '{invalid json',
  }));
  assert.equal(resMalformed.status, 400);
});

test('oversized payload on POST /api/unsubscribe returns 413', async () => {
  const db = fakeDb();
  const handler = createHandler(db);
  const req = new Request('https://api.blowhorn.ai/api/unsubscribe', {
    method: 'POST',
    headers: {
      'content-type': 'application/x-www-form-urlencoded',
      'content-length': '15000',
    },
    body: new URLSearchParams({ token: 'testtoken' }).toString(),
  });
  const res = await handler(req);
  assert.equal(res.status, 413);
});

test('valid multipart form submission is parsed and redirects', async () => {
  const db = fakeDb();
  const handler = createHandler(db);
  const fd = new FormData();
  fd.append('email', 'multipart@example.com');
  fd.append('topic', 'tiktok');
  fd.append('remark', 'testing multipart');
  const req = new Request('https://api.blowhorn.ai/api/waitlist', {
    method: 'POST',
    body: fd,
  });
  const res = await handler(req);
  assert.equal(res.status, 303);
  const row = await db.getSignup('multipart@example.com', 'waitlist', 'tiktok');
  assert.ok(row);
  assert.equal(row.remark, 'testing multipart');
});

test('oversized chunked multipart/form-data returns 413', async () => {
  const db = fakeDb();
  const handler = createHandler(db);
  const fd = new FormData();
  fd.append('email', 'oversized-multipart@example.com');
  fd.append('remark', 'x'.repeat(MAX_BODY_BYTES + 1));
  const rawReq = new Request('https://api.blowhorn.ai/api/waitlist', {
    method: 'POST',
    body: fd,
  });
  const text = await rawReq.text();
  // Strip content-length to simulate a chunked transfer
  const headers = new Headers(rawReq.headers);
  headers.delete('content-length');
  const req = new Request('https://api.blowhorn.ai/api/waitlist', {
    method: 'POST',
    headers,
    body: text,
  });
  const res = await handler(req);
  assert.equal(res.status, 413);
  assert.equal(res.headers.get('content-type'), 'text/html; charset=utf-8');
  const html = await res.text();
  assert.match(html, /Payload too large/);
  assert.equal(db.rows.size, 0);
});

function supportBody(overrides = {}) {
  return {
    name: 'Ada Lovelace',
    email: 'ada@example.com',
    subject: 'Cannot sign in',
    message: 'The app refuses my profile.',
    details: 'blowhorn login\nexit code 3',
    source_page: '/support/',
    ...overrides,
  };
}

test('support message stores one row and forwards to the queue', async () => {
  const db = fakeDb();
  const calls = [];
  const forward = {
    url: 'https://cloud.example.test/api/marketing/forms/blowhorn-support',
    fetchImpl: async (url, init) => {
      calls.push({ url, body: JSON.parse(init.body) });
      return { ok: true };
    },
  };
  const res = await createHandler(db, { forward })(post('/api/support', supportBody()));
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true });
  assert.equal(db.supportRows.length, 1);
  const row = db.supportRows[0];
  assert.equal(row.name, 'Ada Lovelace');
  assert.equal(row.email, 'ada@example.com');
  assert.equal(row.subject, 'Cannot sign in');
  assert.equal(row.details, 'blowhorn login\nexit code 3');
  assert.equal(row.source_page, '/support/');
  assert.ok(row.forwarded_at);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, forward.url);
  assert.equal(calls[0].body.email, 'ada@example.com');
  assert.equal(calls[0].body.name, 'Ada Lovelace');
  assert.equal(calls[0].body.subject, '[Blowhorn support] Cannot sign in');
  assert.match(calls[0].body.message, /The app refuses my profile\./);
  assert.match(calls[0].body.message, /exit code 3/);
  assert.deepEqual(Object.keys(calls[0].body).sort(), ['email', 'message', 'name', 'subject']);
});

test('support form post redirects to the support thanks page', async () => {
  const db = fakeDb();
  const res = await createHandler(db)(formPost('/api/support', supportBody()));
  assert.equal(res.status, 303);
  assert.equal(res.headers.get('location'), 'https://blowhorn.ai/support/thanks/');
  assert.equal(db.supportRows.length, 1);
});

test('support validation rejects missing and over-long fields', async () => {
  const db = fakeDb();
  const handle = createHandler(db);
  for (const body of [
    supportBody({ name: '' }),
    supportBody({ name: 'x'.repeat(101) }),
    supportBody({ email: 'not-an-email' }),
    supportBody({ subject: '' }),
    supportBody({ subject: 'x'.repeat(200) }),
    supportBody({ subject: 'x'.repeat(201) }),
    supportBody({ message: '' }),
    supportBody({ message: 'x'.repeat(5001) }),
    supportBody({ details: 'x'.repeat(5001) }),
  ]) {
    const res = await handle(post('/api/support', body));
    assert.equal(res.status, 400);
    assert.equal((await res.json()).ok, false);
  }
  assert.equal(db.supportRows.length, 0);
});

test('support honeypot answers success without storing or forwarding', async () => {
  const db = fakeDb();
  let called = 0;
  const forward = {
    url: 'https://cloud.example.test/api/marketing/forms/blowhorn-support',
    fetchImpl: async () => {
      called += 1;
      return { ok: true };
    },
  };
  const res = await createHandler(db, { forward })(
    post('/api/support', supportBody({ website: 'http://spam' })),
  );
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true });
  assert.equal(db.supportRows.length, 0);
  assert.equal(called, 0);
  const formRes = await createHandler(db, { forward })(
    formPost('/api/support', supportBody({ website: 'http://spam' })),
  );
  assert.equal(formRes.status, 303);
  assert.equal(db.supportRows.length, 0);
});

test('a failed forward keeps the row and leaves forwarded_at null', async () => {
  const db = fakeDb();
  const forward = {
    url: 'https://cloud.example.test/api/marketing/forms/blowhorn-support',
    fetchImpl: async () => ({ ok: false, status: 401 }),
  };
  const res = await createHandler(db, { forward })(post('/api/support', supportBody()));
  assert.equal(res.status, 200);
  assert.equal(db.supportRows.length, 1);
  assert.equal(db.supportRows[0].forwarded_at, null);
  const throwing = {
    url: 'https://cloud.example.test/api/marketing/forms/blowhorn-support',
    fetchImpl: async () => {
      throw new Error('network down');
    },
  };
  const res2 = await createHandler(db, { forward: throwing })(
    post('/api/support', supportBody({ email: 'b@example.com' })),
  );
  assert.equal(res2.status, 200);
  assert.equal(db.supportRows.length, 2);
  assert.equal(db.supportRows[1].forwarded_at, null);
});

test('no forward configured stores only', async () => {
  const db = fakeDb();
  const res = await createHandler(db, { forward: null })(post('/api/support', supportBody()));
  assert.equal(res.status, 200);
  assert.equal(db.supportRows.length, 1);
  assert.equal(db.supportRows[0].forwarded_at, null);
});

test('the forward sends the full name as typed', async () => {
  const db = fakeDb();
  const calls = [];
  const forward = {
    url: 'https://cloud.example.test/api/marketing/forms/blowhorn-support',
    fetchImpl: async (url, init) => {
      calls.push(JSON.parse(init.body));
      return { ok: false, status: 400 };
    },
  };
  await createHandler(db, { forward })(post('/api/support', supportBody({ name: 'Madonna' })));
  assert.equal(calls[0].name, 'Madonna');
  assert.deepEqual(Object.keys(calls[0]).sort(), ['email', 'message', 'name', 'subject']);
  assert.equal(db.supportRows[0].forwarded_at, null);
});

test('support shares the per-IP rate limit', async () => {
  const db = fakeDb();
  const handle = createHandler(db);
  let last;
  for (let i = 0; i < 31; i += 1) {
    last = await handle(post('/api/support', supportBody(), { 'cf-connecting-ip': '203.0.113.9' }));
  }
  assert.equal(last.status, 429);
  assert.equal(db.supportRows.length, 30);
});
