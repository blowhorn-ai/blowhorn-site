/* Platform product pages (layouts/platform-page.html, docs/platform-pages.md).

   Without this file the page is complete: every activity type's intent is listed,
   the local stage shows its three scenes stacked as text (its diagram and replay
   button stay hidden), the action matrix is a plain table and the setups are a
   native scroll-snap row. With it (.is-enhanced on the page):

   - The activity type radios ([data-pp-choice]) swap every [data-pp-for] element
     (the intent and the Activities illustration) and mark the matrix rows bound to
     the type ([data-pp-row]); no row is hidden. The change is announced in
     [data-pp-announce].
   - The local stage ([data-pp-local]) shows one scene at a time. Its scene radios
     ([data-pp-scene-choice]) hide the other text panels ([data-pp-scene-panel]) and
     set data-scene on the stage, which the CSS reads to draw that scene's diagram.
     Each change plays the diagram once (a class restarted by the script, never a
     loop) and announces the scene in [data-pp-stage-announce], once, from the user's
     own choice. The replay button ([data-pp-replay]) plays the diagram again.
     data-pp-run counts the plays, so the page's state is checkable without motion.
   - The setups carousel ([data-pp-carousel]) runs Embla (vendored, stable v8,
     assets/js/vendor/embla-carousel-8.6.0.umd.js) on its viewport ([data-pp-rail]):
     one setup in focus with the next peeking in. Drag and swipe settle on a setup.
     Left and Right, Home and End, the previous and next buttons ([data-pp-prev],
     [data-pp-next]) and the pager dots ([data-pp-dot], beside the arrows) move
     between setups (Up and Down stay the page's). Setups
     out of view are inert, so an offscreen copy button or link cannot take focus.
     The pager thumb ([data-pp-thumb]) and the newly selected setup move with Motion
     (vendored mini build, assets/js/vendor/motion-mini-14.10.0.js, WAAPI, finite).
     Each change is announced once in [data-pp-rail-announce], by its position and
     name. Previous and next use aria-disabled at the ends, never disabled, so a
     focused button keeps focus.
   - Reduced motion (prefers-reduced-motion: reduce) turns off every animation the
     script starts: Embla's duration is 0 (a jump, not a snap), Motion is not called
     and the thumb and setup are set directly. A change to the preference while the
     page is open is applied at once.

   The script makes no request, reads no storage or cookie, talks to no extension
   and inspects no browser session: the stage is an illustration of how the
   extension works, never a live view of anything. No request to another host. The
   vendored libraries are local files with no network use. Motion is never infinite.
   Tested through platform_page_harness.js by check_platform_pages.py
   (make check-platform-pages) and test_platform_pages.py (make test-scripts).
   The real-browser pass (Embla drag and swipe, keys, reduced motion changed while
   open, the no-script row) is recorded in docs/platform-pages.md. */
(function () {
  "use strict";

  function all(root, sel) {
    return Array.prototype.slice.call(root.querySelectorAll(sel));
  }

  function reduced() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }

  function enhance(root) {
    var choices = all(root, "[data-pp-choice]");
    if (!choices.length) return;
    var announce = root.querySelector("[data-pp-announce]");

    function intentOf(id) {
      var text = "";
      all(root, "[data-pp-intent]").forEach(function (el) {
        if (el.getAttribute("data-pp-for") === id) text = el.textContent;
      });
      return text;
    }

    function select(id, say) {
      var known = choices.some(function (input) { return input.value === id; });
      if (!known) return;
      root.setAttribute("data-pp-type", id);
      choices.forEach(function (input) { input.checked = input.value === id; });
      all(root, "[data-pp-for]").forEach(function (el) {
        el.hidden = el.getAttribute("data-pp-for") !== id;
      });
      all(root, "[data-pp-row]").forEach(function (el) {
        el.classList.toggle("is-picked", el.getAttribute("data-pp-row") === id);
      });
      if (announce && say) announce.textContent = say;
    }

    /* Selecting a different radio (pointer, arrow keys or assistive technology)
       fires change. Clicking the radio that is already checked fires no change
       and needs nothing: the page already shows that type. */
    choices.forEach(function (input) {
      input.addEventListener("change", function () {
        if (!input.checked) return;
        select(input.value, intentOf(input.value));
      });
    });

    var initial = "";
    choices.forEach(function (input) { if (input.checked) initial = input.value; });
    select(initial || choices[0].value, "");
    root.classList.add("is-enhanced");
  }

  function enhanceLocal(root) {
    var box = root.querySelector("[data-pp-local]");
    if (!box) return;
    var choices = all(box, "[data-pp-scene-choice]");
    if (!choices.length) return;
    var announce = box.querySelector("[data-pp-stage-announce]");
    var replay = box.querySelector("[data-pp-replay]");
    var runs = 0;

    /* Restarting the diagram: drop the class, force a layout, add it back. The
       animation is declared under .is-playing and runs once. */
    function play() {
      runs += 1;
      box.setAttribute("data-pp-run", String(runs));
      box.classList.remove("is-playing");
      void box.offsetWidth;
      box.classList.add("is-playing");
    }

    function show(id) {
      var known = choices.some(function (input) { return input.value === id; });
      if (!known) return;
      box.setAttribute("data-scene", id);
      choices.forEach(function (input) { input.checked = input.value === id; });
      all(box, "[data-pp-scene-panel]").forEach(function (el) {
        el.hidden = el.getAttribute("data-pp-scene-panel") !== id;
      });
      play();
    }

    /* Only a scene the visitor picks is announced, once, by its title. The
       replay button and the first scene at load say nothing. */
    choices.forEach(function (input) {
      input.addEventListener("change", function () {
        if (!input.checked) return;
        show(input.value);
        if (announce) announce.textContent = (input.getAttribute("data-title") || "") + " is showing.";
      });
    });

    if (replay) {
      replay.addEventListener("click", function () { play(); });
    }

    var initial = "";
    choices.forEach(function (input) { if (input.checked) initial = input.value; });
    show(initial || choices[0].value);
    box.classList.add("is-enhanced");
  }

  function enhanceRail(root) {
    var carousel = root.querySelector("[data-pp-carousel]");
    var viewport = root.querySelector("[data-pp-rail]");
    var controls = root.querySelector("[data-pp-rail-controls]");
    var prev = root.querySelector("[data-pp-prev]");
    var next = root.querySelector("[data-pp-next]");
    var pager = root.querySelector("[data-pp-pager]");
    var thumb = root.querySelector("[data-pp-thumb]");
    var announce = root.querySelector("[data-pp-rail-announce]");
    var slides = viewport ? all(viewport, "[data-pp-slide]") : [];
    var dots = all(root, "[data-pp-dot]");
    /* Without the vendored libraries (or with too few setups to page) the row stays
       the native scroll-snap area that the markup already shows. */
    if (!carousel || !viewport || !controls || !prev || !next || !pager || !thumb || !announce) return;
    if (slides.length < 2 || dots.length !== slides.length) return;
    if (!window.EmblaCarousel || !window.Motion) {
      console.error("platform page: the setups carousel libraries did not load; the setups stay a native row.");
      return;
    }
    var Embla = window.EmblaCarousel;
    var Motion = window.Motion;

    var query = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
    function reduced() { return !!(query && query.matches); }

    function options(off, startIndex) {
      return {
        align: "center",
        containScroll: "trimSnaps",
        loop: false,
        dragFree: false,
        skipSnaps: false,
        startIndex: startIndex,
        duration: off ? 0 : 25
      };
    }

    /* The row is only the carousel while Embla runs. The class that gives Embla its
       viewport goes on before Embla measures the row. If Embla throws, or finds other
       than one stop per setup (so the dots would not match the setups), the class comes
       back off, Embla is torn down and the row is the native one again. Logged, never
       silent. */
    function fallBack(reason) {
      carousel.classList.remove("is-embla");
      console.error("platform page: the setups carousel is off (" + reason + "); the setups stay a native row.");
    }
    carousel.classList.add("is-embla");
    var embla = null;
    try {
      embla = Embla(viewport, options(reduced(), 0));
    } catch (err) {
      fallBack("Embla did not start: " + (err && err.message ? err.message : String(err)));
      return;
    }
    if (embla.scrollSnapList().length !== slides.length) {
      var stops = embla.scrollSnapList().length;
      embla.destroy();
      fallBack("Embla found " + stops + " stops for " + slides.length + " setups");
      return;
    }
    var shown = embla.selectedScrollSnap();
    var thumbAt = shown;
    var thumbAnim = null;
    var cardAnim = null;
    var cardSlide = null;

    /* The pager is shown by sync() before any thumb placement, so the pitch is the
       rendered distance between two dots. */
    function pitch() { return dots[1].offsetLeft - dots[0].offsetLeft; }

    /* Motion's stop() commits the animation's in-flight values into the element's
       inline style and then cancels it. Clearing that inline style hands the setup
       back to its stylesheet state, so an interrupted settle never leaves a setup
       dimmed or raised. */
    function endSettle() {
      if (cardAnim) { cardAnim.stop(); cardAnim = null; }
      if (cardSlide) {
        cardSlide.style.opacity = "";
        cardSlide.style.transform = "";
        cardSlide = null;
      }
    }

    function placeThumb(at) {
      thumb.style.transform = "translateX(" + at * pitch() + "px)";
    }

    /* The pager thumb follows the selected dot: a finite WAAPI move, or a jump when
       the visitor prefers reduced motion. An interrupted move is stopped, then the
       thumb is placed on its final dot, so it always ends where the page says. */
    function moveThumb(at, animate) {
      var from = thumbAt * pitch();
      thumbAt = at;
      if (thumbAnim) { thumbAnim.stop(); thumbAnim = null; }
      placeThumb(at);
      if (animate && !reduced()) {
        thumbAnim = Motion.animate(thumb, {
          transform: ["translateX(" + from + "px)", "translateX(" + at * pitch() + "px)"]
        }, { duration: 0.3, ease: "easeOut" });
      }
    }

    /* The setup that has just come into focus settles in: a short fade and rise,
       once. The previous settle is ended first, so only one setup is ever mid-way.
       Nothing runs under reduced motion. */
    function settle(at) {
      endSettle();
      if (reduced()) return;
      cardSlide = slides[at];
      cardAnim = Motion.animate(cardSlide, {
        opacity: [0.6, 1],
        transform: ["translateY(6px)", "translateY(0px)"]
      }, { duration: 0.32, ease: "easeOut" });
    }

    /* Ends every running transition and leaves each element in its final state. */
    function stopMotion() {
      endSettle();
      if (thumbAnim) { thumbAnim.stop(); thumbAnim = null; }
      placeThumb(thumbAt);
    }

    function syncInView() {
      var visible = embla.slidesInView();
      slides.forEach(function (slide, i) {
        if (visible.indexOf(i) >= 0) slide.removeAttribute("inert");
        else slide.setAttribute("inert", "");
      });
    }

    /* Everything that depends on the position: the ends, the dots, the pager's
       visibility and which setups can take focus. Runs on every select and reInit. */
    function sync() {
      var at = embla.selectedScrollSnap();
      var paged = embla.scrollSnapList().length > 1;
      controls.hidden = !paged;
      pager.hidden = !paged;
      prev.setAttribute("aria-disabled", embla.canScrollPrev() ? "false" : "true");
      next.setAttribute("aria-disabled", embla.canScrollNext() ? "false" : "true");
      dots.forEach(function (dot, i) {
        if (i === at) dot.setAttribute("aria-current", "true");
        else dot.removeAttribute("aria-current");
      });
      slides.forEach(function (slide, i) {
        if (i === at) slide.setAttribute("data-pp-current", "");
        else slide.removeAttribute("data-pp-current");
      });
      syncInView();
    }

    function go(i) {
      var max = embla.scrollSnapList().length - 1;
      embla.scrollTo(Math.max(0, Math.min(max, i)), reduced());
    }

    /* Embla emits select once per change of setup, from a drag, a key, a button or a
       dot. The announcement and the settle belong to that change only. */
    embla.on("select", function () {
      var at = embla.selectedScrollSnap();
      sync();
      moveThumb(at, true);
      if (at === shown) return;
      shown = at;
      settle(at);
      announce.textContent = "Setup " + (at + 1) + " of " + slides.length + ": " + slides[at].getAttribute("data-pp-name") + ".";
    });
    embla.on("slidesInView", syncInView);
    embla.on("reInit", function () { sync(); moveThumb(embla.selectedScrollSnap(), false); });

    prev.addEventListener("click", function () { if (embla.canScrollPrev()) go(embla.selectedScrollSnap() - 1); });
    next.addEventListener("click", function () { if (embla.canScrollNext()) go(embla.selectedScrollSnap() + 1); });
    dots.forEach(function (dot, i) {
      dot.addEventListener("click", function () { go(i); });
    });

    /* Keys only act on the carousel's own controls (the viewport, the buttons and
       the dots), so arrows inside a code card still scroll that code. The row is
       horizontal: Left and Right move one setup, Home and End go to the ends. Up and
       Down are left to the page. */
    root.addEventListener("keydown", function (ev) {
      if (!ev.target || !ev.target.hasAttribute || !ev.target.hasAttribute("data-pp-nav")) return;
      var at = embla.selectedScrollSnap();
      var last = embla.scrollSnapList().length - 1;
      var to = null;
      if (ev.key === "ArrowLeft") to = at - 1;
      else if (ev.key === "ArrowRight") to = at + 1;
      else if (ev.key === "Home") to = 0;
      else if (ev.key === "End") to = last;
      if (to === null) return;
      ev.preventDefault();
      go(to);
    });

    /* A change to the motion preference while the page is open: running motion is
       ended and left in its final state, and Embla keeps its setup while its duration
       follows the preference. */
    function onMotionChange() {
      var off = reduced();
      if (off) stopMotion();
      embla.reInit(options(off, embla.selectedScrollSnap()));
    }
    if (query && query.addEventListener) query.addEventListener("change", onMotionChange);

    sync();
    moveThumb(shown, false);
    carousel.classList.add("is-enhanced");
  }

  function init() {
    all(document, "[data-platform-page]").forEach(function (root) {
      enhance(root);
      enhanceLocal(root);
      enhanceRail(root);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
