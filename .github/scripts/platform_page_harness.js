#!/usr/bin/env node
/* Run assets/js/platform-page.js against a fake DOM built from a BUILT platform
   page and report what the page shows after each step. check_platform_pages.py
   parses the page's <main> into a JSON tree and drives this harness, so the checks
   exercise the generated markup and the real script together, never the script's
   source text.

   Usage: node platform_page_harness.js SCRIPT  < {"tree": <element>, "scenario": {...}}
   Element: {"tag": "div", "attrs": {...}, "children": [<element> | "text"]}
   Scenario: {"reduce": false, "noEmbla": false,
              "steps": [{"choose": "respond"}, {"key": "respond"}, {"scene": "follow"},
                        {"replay": true}, {"click": "next"}, {"click": "prev"},
                        {"dot": 2}, {"keydown": "ArrowRight", "on": "[data-pp-rail]"},
                        {"select": 1}, {"motionChange": true}]}
   "choose" clicks an activity radio and "key" arrows onto it; "scene" clicks a
   scene radio and "replay" presses the replay button. Both radio steps fire change
   only when the checked radio changes, as a browser does.
   The setups carousel runs against stubs of the vendored libraries: EmblaCarousel
   (its option set, index, select, slidesInView, reInit and scrollTo with the jump
   flag, the way the real library reports them) and Motion.animate (every call and
   its keyframes). A Motion stop() commits the animation's in-flight value into the
   element's inline style before it cancels, as the real library does; the stub
   commits the first keyframe. Scenario flags: "emblaThrows" makes the constructor
   throw, "snapMerge" gives Embla one stop too few. "select" is a drag that settles on
   a setup; "dot" clicks a pager dot; "motionChange" flips the reduced-motion
   preference while the page is open.
   Prints one state object per step (the first is the state after load), each with
   the calls the script made during that step in "log". */
"use strict";
const fs = require("fs");
const vm = require("vm");

class ClassList {
  constructor(el) { this.el = el; }
  _get() { return (this.el.attrs.class || "").split(/\s+/).filter(Boolean); }
  _set(list) { this.el.attrs.class = list.join(" "); }
  contains(c) { return this._get().includes(c); }
  add(c) { if (!this.contains(c)) this._set(this._get().concat(c)); }
  remove(c) { this._set(this._get().filter((x) => x !== c)); }
  toggle(c, force) {
    const on = force === undefined ? !this.contains(c) : !!force;
    if (on) this.add(c); else this.remove(c);
    return on;
  }
}

const ATTR_RE = /^\[([a-z][a-z0-9-]*)(?:="([^"]*)")?\]$/;
/* A pager dot's pitch in CSS px (platform-page.css: .pp-dot is 44px square). */
const DOT = 44;

class El {
  constructor(tag, attrs, env) {
    this.tag = tag;
    this.attrs = Object.assign({}, attrs);
    this.children = [];
    this.parent = null;
    this.listeners = {};
    this.env = env;
    this.classList = new ClassList(this);
    this._checked = "checked" in this.attrs;
    this._scrollLeft = 0;
    this._value = null;
    this.files = null;
    this.style = {};
  }
  getAttribute(n) { return n in this.attrs ? this.attrs[n] : null; }
  setAttribute(n, v) { this.attrs[n] = String(v); }
  removeAttribute(n) { delete this.attrs[n]; }
  hasAttribute(n) { return n in this.attrs; }
  get hidden() { return "hidden" in this.attrs; }
  set hidden(v) { if (v) this.attrs.hidden = ""; else delete this.attrs.hidden; }
  get checked() { return this._checked; }
  set checked(v) { this._checked = !!v; }
  /* A textarea's value starts as its text; an input's as its value attribute. */
  get value() {
    if (this._value !== null) return this._value;
    return this.tag === "textarea" ? this.textContent : (this.attrs.value || "");
  }
  set value(v) {
    this._value = String(v);
    if (this.attrs.type === "file" && this._value === "") this.files = null;
  }
  appendChild(child) { child.parent = this; this.children.push(child); return child; }
  get textContent() {
    return this.children.map((c) => (typeof c === "string" ? c : c.textContent)).join("");
  }
  set textContent(v) { this.writes = (this.writes || 0) + 1; this.children = v === "" ? [] : [String(v)]; }
  addEventListener(t, fn) { (this.listeners[t] = this.listeners[t] || []).push(fn); }
  /* Runs this element's listeners, then its ancestors' when the event bubbles
     (keydown does, as in a browser), so a listener on <main> sees a key pressed
     on a setup's viewport. */
  dispatch(t, props) {
    const ev = Object.assign({ type: t, target: this, defaultPrevented: false, preventDefault() { this.defaultPrevented = true; } }, props || {});
    for (let el = this; el && el.listeners; el = el.parent) {
      (el.listeners[t] || []).slice().forEach((fn) => fn(ev));
      if (t !== "keydown") break;
    }
    return ev;
  }
  descendants() {
    const out = [];
    const walk = (el) => el.children.forEach((c) => {
      if (typeof c !== "string") { out.push(c); walk(c); }
    });
    walk(this);
    return out;
  }
  matches(sel) {
    const m = ATTR_RE.exec(sel);
    if (!m) throw new Error("harness: unsupported selector " + sel);
    if (!(m[1] in this.attrs)) return false;
    return m[2] === undefined || this.attrs[m[1]] === m[2];
  }
  querySelectorAll(sel) { return this.descendants().filter((el) => el.matches(sel)); }
  querySelector(sel) { return this.querySelectorAll(sel)[0] || null; }
  focus() { this.env.active = this; }
  scrollIntoView(opts) { this.env.intoView.push((opts && opts.behavior) || "auto"); }

  /* Rail geometry, from the scenario: slides sit side by side from 0. */
  _rail() { return this.env.rail; }
  _slides() { return this.querySelectorAll("[data-pp-slide]"); }
  get clientWidth() { return "data-pp-rail" in this.attrs ? this._rail().width : 0; }
  get scrollWidth() {
    if (!("data-pp-rail" in this.attrs)) return 0;
    const r = this._rail();
    const n = this._slides().length;
    return n * r.slide + Math.max(0, n - 1) * r.gap;
  }
  get scrollLeft() { return this._scrollLeft; }
  set scrollLeft(v) { this._scrollLeft = v; }
  get offsetLeft() {
    if ("data-pp-dot" in this.attrs) return Number(this.attrs["data-pp-dot"]) * DOT;
    if (!("data-pp-slide" in this.attrs)) return 0;
    const r = this.env.rail;
    return this.env.slideIndex(this) * (r.slide + r.gap);
  }
  get offsetWidth() {
    if ("data-pp-dot" in this.attrs) return DOT;
    return "data-pp-slide" in this.attrs ? this.env.rail.slide : 0;
  }
  scrollTo(opts) {
    const max = Math.max(0, this.scrollWidth - this.clientWidth);
    this._scrollLeft = Math.max(0, Math.min(max, opts.left));
    this.env.scrolls.push(opts.behavior || "auto");
    this.dispatch("scroll");
  }
}

function build(node, env, parent) {
  if (typeof node === "string") return node;
  const el = new El(node.tag, node.attrs || {}, env);
  el.parent = parent || null;
  el.children = (node.children || []).map((c) => build(c, env, el));
  return el;
}

function keyOf(el) {
  if (!el) return "";
  const hooks = Object.keys(el.attrs).filter((k) => k.startsWith("data-pp-") || k === "data-platform-page");
  return hooks.join(" ");
}

function state(env, root) {
  const shown = {};
  const hidden = {};
  root.querySelectorAll("[data-pp-for]").forEach((el) => {
    const id = el.getAttribute("data-pp-for");
    const bucket = el.hidden ? hidden : shown;
    bucket[id] = (bucket[id] || 0) + 1;
  });
  const q = (sel) => root.querySelector(sel);
  const rail = q("[data-pp-rail]");
  const local = q("[data-pp-local]");
  const sceneAnnounce = q("[data-pp-stage-announce]");
  return {
    sceneEnhanced: local ? local.classList.contains("is-enhanced") : null,
    scene: local ? local.getAttribute("data-scene") : null,
    scenePanels: root.querySelectorAll("[data-pp-scene-panel]").filter((p) => !p.hidden).map((p) => p.getAttribute("data-pp-scene-panel")),
    sceneChecked: root.querySelectorAll("[data-pp-scene-choice]").filter((r) => r.checked).map((r) => r.value),
    sceneAnnounce: sceneAnnounce ? sceneAnnounce.textContent : null,
    sceneAnnounceWrites: sceneAnnounce ? (sceneAnnounce.writes || 0) : null,
    run: local ? local.getAttribute("data-pp-run") : null,
    playing: local ? local.classList.contains("is-playing") : false,
    enhanced: root.classList.contains("is-enhanced"),
    type: root.getAttribute("data-pp-type"),
    checked: root.querySelectorAll("[data-pp-choice]").filter((r) => r.checked).map((r) => r.value),
    shown,
    hidden,
    picked: root.querySelectorAll("[data-pp-row]").filter((r) => r.classList.contains("is-picked")).map((r) => r.getAttribute("data-action")),
    announce: q("[data-pp-announce]") ? q("[data-pp-announce]").textContent : null,
    announceWrites: q("[data-pp-announce]") ? (q("[data-pp-announce]").writes || 0) : null,
    carousel: q("[data-pp-carousel]") ? q("[data-pp-carousel]").classList.contains("is-embla") : null,
    controlsShown: q("[data-pp-rail-controls]") ? !q("[data-pp-rail-controls]").hidden : false,
    pagerShown: q("[data-pp-pager]") ? !q("[data-pp-pager]").hidden : false,
    railAnnounce: q("[data-pp-rail-announce]") ? q("[data-pp-rail-announce]").textContent : null,
    railAnnounceWrites: q("[data-pp-rail-announce]") ? (q("[data-pp-rail-announce]").writes || 0) : null,
    prevDisabled: q("[data-pp-prev]") ? q("[data-pp-prev]").getAttribute("aria-disabled") : null,
    nextDisabled: q("[data-pp-next]") ? q("[data-pp-next]").getAttribute("aria-disabled") : null,
    prevDisabledAttr: q("[data-pp-prev]") ? q("[data-pp-prev]").hasAttribute("disabled") : null,
    dotCurrent: root.querySelectorAll("[data-pp-dot]").map((d, i) => (d.getAttribute("aria-current") === "true" ? i : -1)).filter((i) => i >= 0),
    inert: root.querySelectorAll("[data-pp-slide]").filter((s) => s.hasAttribute("inert")).map((s) => s.getAttribute("data-pp-name")),
    /* The setup in focus, from the authoritative state: the dot marked aria-current, and its slide. */
    current: root.querySelectorAll("[data-pp-dot]").filter((d) => d.getAttribute("aria-current") === "true").map((d) => root.querySelectorAll("[data-pp-slide]")[Number(d.getAttribute("data-pp-dot"))]).filter(Boolean).map((s) => s.getAttribute("data-pp-name")),
    thumb: q("[data-pp-thumb]") ? q("[data-pp-thumb]").style.transform || null : null,
    slideStyles: root.querySelectorAll("[data-pp-slide]").map((s) => ({ opacity: s.style.opacity || "", transform: s.style.transform || "" })),
    railScrollLeft: rail ? rail.scrollLeft : null,
    scrolls: env.scrolls.slice(),
    embla: env.embla ? { index: env.embla.index, options: env.embla.options } : null,
    log: env.log.splice(0),
    errors: env.errors.splice(0),
    focus: keyOf(env.active),
  };
}

/* A click on a radio, as a browser runs it: click fires with the radio already
   checked, then input and change fire only if the checked radio changed. Clicking
   (or pressing Space on) the radio that is already checked fires click alone. */
function selectRadio(radios, radio) {
  const was = radio.checked;
  if (!was) radios.forEach((r) => { r.checked = r === radio; });
  radio.dispatch("click");
  if (!was) {
    radio.dispatch("input");
    radio.dispatch("change");
  }
}

/* The vendored libraries, as stubs. Geometry is not modelled: the stub Embla shows
   the setup in focus with its neighbours peeking in (its slidesInView), and reports every
   change of setup the way the real library does: select at the start of the move,
   then slidesInView. A move with the jump flag, or a duration of 0, is a jump. */
function emblaStub(env) {
  return function EmblaCarousel(viewport, options) {
    const container = viewport.children.find((c) => typeof c !== "string");
    const n = container ? container.children.filter((c) => typeof c !== "string").length : 0;
    if (env.emblaThrows) throw new Error("stub constructor failure");
    const inst = {
      index: options.startIndex || 0,
      options: Object.assign({ loop: false, duration: 25 }, options),
      listeners: {},
    };
    env.embla = inst;
    env.emblaInit = Object.assign({}, options);
    const emit = (evt) => (inst.listeners[evt] || []).forEach((fn) => fn());
    const visible = () => [inst.index - 1, inst.index, inst.index + 1].filter((i) => i >= 0 && i < n);
    inst.on = (evt, fn) => { (inst.listeners[evt] = inst.listeners[evt] || []).push(fn); };
    inst.selectedScrollSnap = () => inst.index;
    inst.scrollSnapList = () => Array.from({ length: env.snapMerge ? n - 1 : n }, (_, i) => i);
    inst.destroy = () => { env.log.push("embla.destroy"); };
    inst.canScrollPrev = () => inst.index > 0;
    inst.canScrollNext = () => inst.index < n - 1;
    inst.slidesInView = () => visible();
    inst.scrollTo = (i, jump) => {
      const to = Math.max(0, Math.min(n - 1, i));
      if (to === inst.index) return;
      const instant = !!jump || inst.options.duration === 0;
      env.log.push("embla.scrollTo " + to + (instant ? " jump" : " animated"));
      inst.index = to;
      emit("select");
      emit("slidesInView");
    };
    inst.scrollPrev = (jump) => inst.scrollTo(inst.index - 1, jump);
    inst.scrollNext = (jump) => inst.scrollTo(inst.index + 1, jump);
    /* reInit merges its options into the instance; the index stays where it was
       unless startIndex names another (the real library starts again there). */
    inst.reInit = (opts) => {
      inst.options = Object.assign({}, inst.options, opts || {});
      if (opts && opts.startIndex !== undefined) inst.index = opts.startIndex;
      env.log.push("embla.reInit duration " + inst.options.duration + " index " + inst.index);
      emit("reInit");
      emit("slidesInView");
    };
    return inst;
  };
}

function motionStub(env) {
  return {
    animate(el, keyframes, options) {
      const name = el.getAttribute("data-pp-name") || (el.getAttribute("data-pp-thumb") !== null ? "thumb" : el.tag);
      env.log.push("motion.animate " + name + " " + JSON.stringify(keyframes) + " " + options.duration);
      return {
        stop() {
          env.log.push("motion.stop " + name);
          /* commitStyles: the in-flight value stays in the inline style. */
          Object.keys(keyframes).forEach((key) => {
            const frames = keyframes[key];
            el.style[key] = Array.isArray(frames) ? frames[0] : frames;
          });
        },
      };
    },
  };
}

function main() {
  const script = process.argv[2];
  const input = JSON.parse(fs.readFileSync(0, "utf8"));
  const sc = input.scenario || {};
  const env = {
    rail: sc.rail || { width: 1000, slide: 484, gap: 32 },
    scrolls: [],
    winListeners: {},
    intoView: [],
    active: null,
    log: [],
    reduce: !!sc.reduce,
    emblaThrows: !!sc.emblaThrows,
    snapMerge: !!sc.snapMerge,
    errors: [],
    mqlListeners: [],
    embla: null,
    slideIndex(el) { return env.slides.indexOf(el); },
  };
  const root = build(input.tree, env, null);
  env.slides = root.querySelectorAll("[data-pp-slide]");
  const doc = new El("#document", {}, env);
  doc.children = [root];
  root.parent = doc;
  doc.readyState = "complete";
  Object.defineProperty(doc, "activeElement", { get: () => env.active });
  doc.createElement = (tag) => new El(tag, {}, env);
  const mql = {
    get matches() { return env.reduce; },
    addEventListener(type, fn) { if (type === "change") env.mqlListeners.push(fn); },
  };
  const win = {
    matchMedia: (query) => (query.indexOf("reduce") >= 0 ? mql : { matches: false, addEventListener() {} }),
    requestAnimationFrame: (fn) => fn(),
    addEventListener(type, fn) { (env.winListeners[type] = env.winListeners[type] || []).push(fn); },
  };
  if (!sc.noEmbla) {
    win.EmblaCarousel = emblaStub(env);
    win.Motion = motionStub(env);
  }
  /* console.error is captured (the page reports a failed library load there), and
     everything else goes to the process's stderr, never stdout. */
  const logger = {
    log: (...a) => process.stderr.write(a.join(" ") + "\n"),
    warn: (...a) => process.stderr.write(a.join(" ") + "\n"),
    error: (...a) => env.errors.push(a.join(" ")),
  };
  const ctx = { window: win, document: doc, Array, console: logger };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(script, "utf8"), ctx, { filename: script });

  const states = [state(env, root)];
  (sc.steps || []).forEach((step) => {
    if (step.choose) {
      const radios = root.querySelectorAll("[data-pp-choice]");
      const radio = radios.find((r) => r.value === step.choose);
      if (!radio) throw new Error("harness: no radio for " + step.choose);
      selectRadio(radios, radio);
    } else if (step.key) {
      /* Arrow keys move focus and selection to the next radio: the same events as
         a click on an unchecked radio, with focus on it. */
      const radios = root.querySelectorAll("[data-pp-choice]");
      const radio = radios.find((r) => r.value === step.key);
      if (!radio) throw new Error("harness: no radio for " + step.key);
      radio.focus();
      selectRadio(radios, radio);
    } else if (step.scene) {
      /* A scene radio, as a click or an arrow key: the same events as a radio. */
      const radios = root.querySelectorAll("[data-pp-scene-choice]");
      const radio = radios.find((r) => r.value === step.scene);
      if (!radio) throw new Error("harness: no scene radio for " + step.scene);
      radio.focus();
      selectRadio(radios, radio);
    } else if (step.replay) {
      const button = root.querySelector("[data-pp-replay]");
      if (!button) throw new Error("harness: no replay button");
      button.focus();
      button.dispatch("click");
    } else if (step.keydown) {
      const target = root.querySelector(step.on || "[data-pp-rail]");
      if (!target) throw new Error("harness: no key target " + step.on);
      target.focus();
      const ev = target.dispatch("keydown", { key: step.keydown, target });
      env.log.push("key " + step.keydown + (ev.defaultPrevented ? " prevented" : " passed"));
    } else if (step.dot !== undefined) {
      const dot = root.querySelector('[data-pp-dot="' + step.dot + '"]');
      if (!dot) throw new Error("harness: no dot " + step.dot);
      dot.focus();
      dot.dispatch("click");
    } else if (step.select !== undefined) {
      /* A drag settles on a setup: the library moves, then the script hears it. */
      if (!env.embla) throw new Error("harness: no carousel to drag");
      env.embla.scrollTo(step.select, false);
    } else if (step.motionChange !== undefined) {
      env.reduce = !!step.motionChange;
      env.mqlListeners.forEach((fn) => fn({ matches: env.reduce }));
    } else if (step.click) {
      const button = root.querySelector(step.click === "prev" ? "[data-pp-prev]" : "[data-pp-next]");
      if (!button) throw new Error("harness: no " + step.click + " button");
      button.focus();
      button.dispatch("click");
    } else {
      throw new Error("harness: unknown step " + JSON.stringify(step));
    }
    states.push(state(env, root));
  });
  process.stdout.write(JSON.stringify(states));
}

main();
