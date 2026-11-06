#!/usr/bin/env node
// Real-browser checks for the platform usage carousel (docs/platform-pages.md,
// "Real-browser pass"). Not part of `make check`: it needs a Chromium and the
// playwright-core package, so it runs from `make check-platform-carousel`.
//
//   npm install --no-save playwright-core        (once, does not change package.json)
//   CHROME_PATH=/path/to/chrome make check-platform-carousel
//
// It serves the built site (BUILD_DIR, default public/) on a random local port and
// drives it through Chromium. CHROME_PATH is optional: without it Playwright uses the
// browser it installed for playwright-core. SHOTS_DIR (default: a temporary folder)
// receives the screenshots and results.json. Exit status 0 only if every check passes.
import { chromium } from "playwright-core";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "..", "..");
const BUILD = path.resolve(process.argv[2] || path.join(repo, "public"));
const ROUTE = "/preview/platforms/x/";
const SHOTS = path.resolve(process.env.SHOTS_DIR || path.join(os.tmpdir(), "platform-carousel-browser"));
const CHROME = process.env.CHROME_PATH || undefined;

const results = [];
function check(name, ok, detail = "") {
  results.push({ name, ok: !!ok, detail: String(detail) });
  console.log(`${ok ? "PASS" : "FAIL"} ${name}${detail && !ok ? "  -> " + String(detail).slice(0, 400) : ""}`);
}

const TYPES = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
  ".webp": "image/webp", ".woff2": "font/woff2", ".xml": "application/xml", ".txt": "text/plain; charset=utf-8",
};

function serve(root) {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      let p = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
      if (p.endsWith("/")) p += "index.html";
      const file = path.join(root, p);
      if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
      fs.readFile(file, (err, data) => {
        if (err) { res.writeHead(404).end("not found"); return; }
        res.writeHead(200, { "content-type": TYPES[path.extname(file)] || "application/octet-stream" });
        res.end(data);
      });
    });
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

async function open(browser, base, opts, { decline = true } = {}) {
  const context = await browser.newContext({
    viewport: opts.viewport,
    colorScheme: opts.scheme || "light",
    reducedMotion: opts.reduce ? "reduce" : "no-preference",
    javaScriptEnabled: opts.js !== false,
    hasTouch: !!opts.touch,
    isMobile: !!opts.mobile,
    deviceScaleFactor: 1,
  });
  await context.grantPermissions(["clipboard-read", "clipboard-write"], { origin: base });
  const page = await context.newPage();
  page.errors = [];
  page.requests = new Set();
  page.on("pageerror", (e) => page.errors.push("pageerror: " + e.message));
  page.on("console", (m) => { if (m.type() === "error") page.errors.push("console: " + m.text()); });
  page.on("request", (r) => { try { page.requests.add(new URL(r.url()).origin); } catch (e) { /* data: and blob: */ } });
  if (opts.beforeLoad) await page.addInitScript(opts.beforeLoad);
  await page.goto(base + ROUTE, { waitUntil: "load" });
  if (decline && opts.js !== false) {
    const btn = page.locator('button[data-consent="denied"]');
    if (await btn.count()) await btn.first().click();
  }
  await page.waitForTimeout(400);
  return { context, page };
}

// The carousel's state as the reader sees it. "running" counts the carousel's own
// running animations; "globalRunning" counts the whole page (the footer pulse included).
const state = (page) => page.evaluate(() => {
  const q = (s) => document.querySelector(s);
  const all = (s) => Array.from(document.querySelectorAll(s));
  const track = q("[data-pp-track]");
  const vp = q("[data-pp-rail]");
  const slides = all("[data-pp-slide]");
  const ids = all("[data-pp-slide]").map((s) => s.getAttribute("data-pp-name"));
  return {
    index: all("[data-pp-dot]").findIndex((d) => d.getAttribute("aria-current") === "true"),
    transform: track ? getComputedStyle(track).transform : null,
    announce: q("[data-pp-rail-announce]").textContent,
    inert: slides.map((s) => s.hasAttribute("inert")),
    prev: q("[data-pp-prev]").getAttribute("aria-disabled"),
    next: q("[data-pp-next]").getAttribute("aria-disabled"),
    controlsHidden: q("[data-pp-rail-controls]").hidden,
    pagerHidden: q("[data-pp-pager]").hidden,
    isEmbla: q("[data-pp-carousel]").classList.contains("is-embla"),
    running: q("[data-pp-usage]").getAnimations({ subtree: true }).filter((a) => a.playState === "running").length,
    globalRunning: document.getAnimations().filter((a) => a.playState === "running").length,
    slides: slides.map((s, i) => ({
      name: ids[i],
      opacity: getComputedStyle(s).opacity,
      transform: getComputedStyle(s).transform,
      inlineOpacity: s.style.opacity,
      inlineTransform: s.style.transform,
    })),
    thumbComputed: q("[data-pp-thumb]") ? getComputedStyle(q("[data-pp-thumb]")).transform : null,
    thumbInline: q("[data-pp-thumb]") ? q("[data-pp-thumb]").style.transform : null,
    activeTag: document.activeElement ? (document.activeElement.getAttribute("data-pp-dot") ?? document.activeElement.getAttribute("data-pp-prev") ?? document.activeElement.getAttribute("data-pp-next") ?? document.activeElement.getAttribute("data-pp-rail") ?? document.activeElement.tagName) : null,
    doc: { scrollW: document.documentElement.scrollWidth, innerW: window.innerWidth },
    slideRects: slides.map((s) => { const r = s.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right)]; }),
    vpRect: (() => { const r = vp.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right)]; })(),
  };
});

const identity = (m) => m === "none" || m === "matrix(1, 0, 0, 1, 0, 0)";
// At rest: computed opacity 1 and identity transform. The inline style is either empty
// (an interrupted settle was handed back) or the settle's own final values, which a
// finished Motion animation leaves in place and which equal the stylesheet's values.
const inlineRest = (s) => (s.inlineOpacity === "" || s.inlineOpacity === "1") && (s.inlineTransform === "" || s.inlineTransform === "translateY(0px)");
const restedSlides = (st) => st.slides.every((s) => s.opacity === "1" && identity(s.transform) && inlineRest(s));

async function run(browser, base) {
  const report = {};
  fs.mkdirSync(SHOTS, { recursive: true });

  // ---- Desktop, dark: first setup in focus, the next peeking in.
  {
    const { context, page } = await open(browser, base, { viewport: { width: 1440, height: 900 }, scheme: "dark" });
    const s = await state(page);
    check("desktop: Embla owns the row", s.isEmbla);
    check("desktop: controls and pager shown", !s.controlsHidden && !s.pagerHidden);
    check("desktop: first setup in focus at load", s.index === 0, s.index);
    check("desktop: setup 3 is inert at load", s.inert[2] === true && s.inert[0] === false, JSON.stringify(s.inert));
    check("desktop: no page overflow at 1440", s.doc.scrollW <= s.doc.innerW, JSON.stringify(s.doc));
    check("desktop: neighbour peeks in from the right", s.slideRects[1][0] < s.vpRect[1] && s.slideRects[1][0] > s.vpRect[0] + 300, JSON.stringify(s.slideRects) + " vp " + JSON.stringify(s.vpRect));
    const sec = page.locator("[data-pp-usage]");
    await sec.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    await sec.screenshot({ path: path.join(SHOTS, "desktop-dark-usage.png") });

    await page.locator("[data-pp-rail]").focus();
    await page.keyboard.press("ArrowRight");
    await page.waitForTimeout(600);
    let t = await state(page);
    check("keys: ArrowRight moves to setup 2", t.index === 1, t.index);
    check("keys: announce says setup 2 of 3", /^Setup 2 of 3: CLI\.$/.test(t.announce), t.announce);
    check("keys: at the middle every setup is at least a peek, so none is inert", t.inert.every((x) => x === false), JSON.stringify(t.inert));
    await page.keyboard.press("End");
    await page.waitForTimeout(600);
    t = await state(page);
    check("keys: End goes to setup 3", t.index === 2, t.index);
    check("keys: next disabled at the end, prev enabled", t.next === "true" && t.prev === "false", `${t.prev} ${t.next}`);
    await page.keyboard.press("ArrowRight");
    await page.waitForTimeout(200);
    t = await state(page);
    check("keys: ArrowRight at the end holds", t.index === 2 && t.announce === "Setup 3 of 3: Agent skill.", t.announce);
    await page.keyboard.press("Home");
    await page.waitForTimeout(600);
    t = await state(page);
    check("keys: Home goes to setup 1", t.index === 0, t.index);

    // Up and Down belong to the page: the setup stays, the page scrolls, and the key is not prevented.
    await page.evaluate(() => { window.__prevented = null; document.addEventListener("keydown", (e) => { window.__prevented = e.defaultPrevented; }); });
    await page.locator("[data-pp-rail]").focus();
    const y0 = await page.evaluate(() => window.scrollY);
    await page.keyboard.press("ArrowDown");
    await page.waitForTimeout(150);
    const down = await state(page);
    const dprev = await page.evaluate(() => window.__prevented);
    const y1 = await page.evaluate(() => window.scrollY);
    check("keys: ArrowDown leaves the setup alone and is not prevented", down.index === 0 && dprev === false, `index=${down.index} prevented=${dprev}`);
    check("keys: ArrowDown scrolls the page", y1 > y0, `${y0} -> ${y1}`);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(100);

    // Tab order: from the viewport, Tab must not land in an inert setup.
    await page.locator("[data-pp-rail]").focus();
    const landed = [];
    for (let i = 0; i < 12; i++) {
      await page.keyboard.press("Tab");
      landed.push(await page.evaluate(() => {
        const el = document.activeElement;
        const sl = el && el.closest && el.closest("[data-pp-slide]");
        return sl ? (sl.hasAttribute("inert") ? "INERT" : sl.getAttribute("data-pp-name")) : (el ? el.tagName + ":" + (el.getAttribute("data-pp-dot") ?? "") : null);
      }));
    }
    check("tab order: never lands in an inert setup", !landed.includes("INERT"), JSON.stringify(landed));

    // Pager click: finite motion runs, then the carousel is at rest.
    await page.locator('[data-pp-dot="2"]').click();
    await page.waitForTimeout(80);
    const mid = await state(page);
    check("pager: a dot click runs finite motion", mid.running > 0, mid.running);
    await page.waitForTimeout(1500);
    t = await state(page);
    check("pager: dot 3 selected and announced", t.index === 2 && t.announce === "Setup 3 of 3: Agent skill.", `${t.index} ${t.announce}`);
    check("pager: no carousel animation left running", t.running === 0, t.running);
    check("pager: every setup rests at opacity 1 with no inline style", restedSlides(t), JSON.stringify(t.slides));

    // Rapid moves: two presses less than 100 ms apart. The first settle is still running
    // when the second move starts; after both, no setup is left dimmed or raised.
    await page.locator('[data-pp-dot="0"]').click();
    await page.waitForTimeout(1200);
    await page.locator("[data-pp-rail]").focus();
    const r0 = Date.now();
    await page.keyboard.press("ArrowRight");
    const midFirst = await state(page);
    await page.keyboard.press("ArrowRight");
    const gap = Date.now() - r0;
    check("rapid: the first settle is still running when the second move starts", midFirst.slides[1].opacity !== "1" && midFirst.index === 1, `opacity=${midFirst.slides[1].opacity}`);
    check("rapid: both presses land within 100 ms", gap < 100, `${gap} ms`);
    await page.waitForTimeout(1200);
    t = await state(page);
    check("rapid: landed on setup 3", t.index === 2, t.index);
    check("rapid: every setup rests at opacity 1, identity transform, no inline style", restedSlides(t), JSON.stringify(t.slides));
    check("rapid: the thumb rests on dot 3", t.thumbComputed === "matrix(1, 0, 0, 1, 88, 0)" && t.thumbInline === "translateX(88px)", `${t.thumbComputed} ${t.thumbInline}`);
    check("rapid: no carousel animation left running", t.running === 0, t.running);

    // Copy: the visible setup's copy button copies its code.
    await page.locator('[data-pp-dot="0"]').click();
    await page.waitForTimeout(1200);
    const copy = page.locator('[data-pp-slide][data-pp-name="MCP"] .term-copy').first();
    await copy.click();
    await page.waitForTimeout(200);
    const clip = await page.evaluate(() => navigator.clipboard.readText());
    check("copy: the setup's copy button copies its code", clip.includes('"mcpServers"') && clip.includes("blowhorn-mcp"), clip.slice(0, 120));
    const srcHref = await page.locator('[data-pp-slide][data-pp-name="MCP"] .pp-use-src a').getAttribute("href");
    check("source link present on setup 1", !!srcHref && srcHref.includes("connect-mcp-client"), srcHref);

    // Mouse drag to the second setup.
    const vpBox = await page.locator("[data-pp-rail]").boundingBox();
    await page.mouse.move(vpBox.x + vpBox.width * 0.7, vpBox.y + 40);
    await page.mouse.down();
    for (let i = 1; i <= 12; i++) await page.mouse.move(vpBox.x + vpBox.width * 0.7 - i * 30, vpBox.y + 40);
    await page.mouse.up();
    await page.waitForTimeout(800);
    t = await state(page);
    check("drag: a left drag settles on setup 2", t.index === 1, t.index);
    check("drag: announces setup 2", /^Setup 2 of 3/.test(t.announce), t.announce);

    // Reduced motion changed while a settle is running.
    await page.locator('[data-pp-dot="0"]').click();
    await page.waitForTimeout(1200);
    await page.locator("[data-pp-rail]").focus();
    await page.keyboard.press("ArrowRight");
    await page.waitForTimeout(90);
    const settling = await state(page);
    check("reduced mid-settle: the settle is running when the preference changes", settling.slides[1].opacity !== "1", settling.slides[1].opacity);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.waitForTimeout(120);
    t = await state(page);
    check("reduced mid-settle: the interrupted setup is handed back at rest", t.slides[1].opacity === "1" && identity(t.slides[1].transform) && inlineRest(t.slides[1]), JSON.stringify(t.slides[1]));
    check("reduced mid-settle: every setup at rest", restedSlides(t), JSON.stringify(t.slides));
    check("reduced mid-settle: the thumb is on its dot", t.thumbComputed === "matrix(1, 0, 0, 1, 44, 0)" && t.thumbInline === "translateX(44px)", `${t.thumbComputed} ${t.thumbInline}`);
    check("reduced mid-settle: nothing in the carousel still runs", t.running === 0, t.running);

    // Reduced motion changed while open: every move is a jump.
    await page.locator('[data-pp-dot="0"]').click();
    await page.waitForTimeout(60);
    const jump1 = await state(page);
    check("reduced (live change): a dot jumps with no animation", jump1.index === 0 && jump1.running === 0 && jump1.globalRunning === 0, `index=${jump1.index} running=${jump1.running} global=${jump1.globalRunning}`);
    await page.locator("[data-pp-next]").click();
    const r1 = await state(page);
    await page.waitForTimeout(60);
    const r2 = await state(page);
    check("reduced (live change): the next button jumps", r1.index === 1 && r1.transform === r2.transform && r2.running === 0, `${r1.index} ${r1.transform} ${r2.transform}`);
    check("reduced (live change): no animation runs anywhere on the page", r2.globalRunning === 0, `globalRunning=${r2.globalRunning}`);
    await page.emulateMedia({ reducedMotion: "no-preference" });
    await page.waitForTimeout(50);
    await page.locator("[data-pp-next]").click();
    await page.waitForTimeout(40);
    const back = await state(page);
    check("motion returns when the preference is turned off", back.running > 0 && back.index === 2, `running=${back.running} index=${back.index}`);
    await page.waitForTimeout(1000);

    // Resize keeps the setup in focus; reduced motion still jumps after Embla's own reInit.
    await page.locator('[data-pp-dot="1"]').click();
    await page.waitForTimeout(700);
    await page.setViewportSize({ width: 1000, height: 900 });
    await page.waitForTimeout(400);
    const resized = await state(page);
    check("resize: the setup in focus is kept", resized.index === 1, resized.index);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.waitForTimeout(50);
    await page.setViewportSize({ width: 820, height: 900 });
    await page.waitForTimeout(300);
    await page.locator("[data-pp-prev]").click();
    const q0 = await state(page);
    await page.waitForTimeout(60);
    const q1 = await state(page);
    check("resize + reduced: a button still jumps after Embla's own reInit", q0.index === 0 && q0.transform === q1.transform && q1.running === 0 && q1.globalRunning === 0, `${q0.index} ${q0.transform} ${q1.transform} running=${q1.running} global=${q1.globalRunning}`);
    await page.emulateMedia({ reducedMotion: "no-preference" });
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.waitForTimeout(300);

    const focused = (await state(page)).index;
    const focusBox = await page.locator("[data-pp-slide]").nth(focused).boundingBox();
    const vb = await page.locator("[data-pp-rail]").boundingBox();
    check("layout: a setup in focus sits inside the viewport", focusBox.x >= vb.x - 1 && focusBox.x + focusBox.width <= vb.x + vb.width + 1, JSON.stringify({ focusBox, vb }));

    const net = [...page.requests];
    check("network: only this origin is requested", net.every((o) => o === base), JSON.stringify(net));
    check("console: no errors on the desktop run", page.errors.length === 0, JSON.stringify(page.errors));
    await context.close();
  }

  // ---- Desktop, light
  {
    const { context, page } = await open(browser, base, { viewport: { width: 1440, height: 900 }, scheme: "light" });
    const sec = page.locator("[data-pp-usage]");
    await sec.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    await sec.screenshot({ path: path.join(SHOTS, "desktop-light-usage.png") });
    check("desktop light: carousel enhanced", (await state(page)).isEmbla);
    await context.close();
  }

  // ---- Phone dark: a swipe moves one setup.
  {
    const { context, page } = await open(browser, base, { viewport: { width: 390, height: 844 }, scheme: "dark", touch: true, mobile: true });
    const s = await state(page);
    check("phone: no page overflow at 390", s.doc.scrollW <= s.doc.innerW, JSON.stringify(s.doc));
    const sec = page.locator("[data-pp-usage]");
    await sec.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    await sec.screenshot({ path: path.join(SHOTS, "phone-dark-usage.png") });
    // Touch coordinates are viewport coordinates: bring the row on screen first.
    await page.locator("[data-pp-rail]").scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    const vb = await page.locator("[data-pp-rail]").boundingBox();
    const cx = vb.x + vb.width * 0.8, cy = vb.y + 60;
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: cx, y: cy, id: 1 }] });
    for (let i = 1; i <= 24; i++) await cdp.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: cx - i * 14, y: cy + (i % 2), id: 1 }] });
    await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await page.waitForTimeout(900);
    const t = await state(page);
    check("phone swipe: a left swipe settles on setup 2", t.index === 1, JSON.stringify({ index: t.index, transform: t.transform }));
    check("phone: no overflow after swipe", t.doc.scrollW <= t.doc.innerW, JSON.stringify(t.doc));
    await context.close();
  }

  // ---- Embla that throws on start: native row, controls hidden, one logged error.
  {
    const { context, page } = await open(browser, base, {
      viewport: { width: 1440, height: 900 }, scheme: "light",
      beforeLoad: () => {
        Object.defineProperty(window, "EmblaCarousel", { configurable: true, get() { return function () { throw new Error("forced start failure"); }; }, set() {} });
      },
    });
    const s = await state(page);
    check("embla throws: the row is native again", !s.isEmbla && s.controlsHidden && s.pagerHidden, JSON.stringify({ isEmbla: s.isEmbla, controlsHidden: s.controlsHidden, pagerHidden: s.pagerHidden }));
    check("embla throws: the failure is logged, not silent", page.errors.some((e) => e.includes("Embla did not start: forced start failure")), JSON.stringify(page.errors));
    await context.close();
  }

  // ---- 320 px: no page overflow.
  {
    const { context, page } = await open(browser, base, { viewport: { width: 320, height: 640 }, scheme: "light", touch: true, mobile: true });
    const s = await state(page);
    check("320: no page overflow", s.doc.scrollW <= s.doc.innerW, JSON.stringify(s.doc));
    await page.locator("[data-pp-usage]").screenshot({ path: path.join(SHOTS, "320-light-usage.png") });
    await context.close();
  }

  // ---- Width and scheme matrix (docs/deploy.md: 320, 390, 820, 1440; light and dark).
  for (const width of [320, 390, 820, 1440]) {
    for (const scheme of ["light", "dark"]) {
      const { context, page } = await open(browser, base, { viewport: { width, height: 900 }, scheme, touch: width < 900, mobile: width < 900 });
      const s = await state(page);
      check(`matrix ${width} ${scheme}: no horizontal overflow`, s.doc.scrollW <= s.doc.innerW, JSON.stringify(s.doc));
      check(`matrix ${width} ${scheme}: carousel enhanced and no console errors`, s.isEmbla && page.errors.length === 0, JSON.stringify(page.errors));
      await page.locator("[data-pp-usage]").screenshot({ path: path.join(SHOTS, `matrix-${width}-${scheme}-usage.png`) });
      await context.close();
    }
  }

  // ---- No JavaScript: native row, all three setups reachable by scrolling, no controls.
  {
    const { context, page } = await open(browser, base, { viewport: { width: 1440, height: 900 }, scheme: "light", js: false });
    const s = await page.evaluate(() => {
      const rail = document.querySelector("[data-pp-rail]");
      return {
        overflowX: getComputedStyle(rail).overflowX,
        scrollable: rail.scrollWidth > rail.clientWidth,
        controlsHidden: document.querySelector("[data-pp-rail-controls]").hidden,
        pagerHidden: document.querySelector("[data-pp-pager]").hidden,
        copyButtons: document.querySelectorAll("[data-pp-slide] .term-copy").length,
        slides: document.querySelectorAll("[data-pp-slide]").length,
        inertAttrs: document.querySelectorAll("[inert]").length,
        isEmbla: document.querySelector("[data-pp-carousel]").classList.contains("is-embla"),
      };
    });
    check("no-js: native scroll row", s.overflowX === "auto" && s.scrollable, JSON.stringify(s));
    check("no-js: controls and pager stay hidden", s.controlsHidden && s.pagerHidden, JSON.stringify(s));
    check("no-js: all setups and their copy buttons present", s.slides === 3 && s.copyButtons === 3, JSON.stringify(s));
    check("no-js: nothing made inert, no Embla", s.inertAttrs === 0 && !s.isEmbla, JSON.stringify(s));
    await page.locator("[data-pp-usage]").scrollIntoViewIfNeeded();
    await page.locator("[data-pp-usage]").screenshot({ path: path.join(SHOTS, "no-js-usage.png") });
    await context.close();
  }
  return report;
}

async function main() {
  if (!fs.existsSync(path.join(BUILD, "preview", "platforms", "x", "index.html"))) {
    console.error(`no built platform page under ${BUILD}; run make site-build first`);
    process.exit(2);
  }
  const server = await serve(BUILD);
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({ headless: true, executablePath: CHROME });
  try {
    await run(browser, base);
  } finally {
    await browser.close();
    server.close();
  }
  const failed = results.filter((r) => !r.ok);
  fs.writeFileSync(path.join(SHOTS, "results.json"), JSON.stringify(results, null, 2) + "\n");
  console.log(`\n${results.length - failed.length}/${results.length} passed; shots and results in ${SHOTS}`);
  process.exit(failed.length ? 1 : 0);
}

main().catch((e) => { console.error("RUN ERROR", e); process.exit(2); });
