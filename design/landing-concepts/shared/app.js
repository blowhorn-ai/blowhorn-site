/* Shared behaviour for every concept: theme preview, reveal-on-scroll,
   the app mock's delivery run, the repost wave, and the compose explorer. */
(function () {
  var root = document.documentElement;
  var q = new URLSearchParams(location.search).get("theme");
  if (q && /^(signal|full-volume|open-field)$/.test(q)) root.setAttribute("data-theme", q);
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // reveal
  var targets = document.querySelectorAll(".shead, .plat, .step, .role, .fact, .quote, .pricing__card, .cta__inner, .major__grid, .xcard");
  targets.forEach(function (el, i) { el.classList.add("reveal"); el.style.transitionDelay = ((i % 4) * 70) + "ms"; });
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
  }, { rootMargin: "0px 0px -8% 0px" });
  targets.forEach(function (el) { io.observe(el); });
  document.querySelectorAll(".wave__list").forEach(function (l) {
    l.querySelectorAll("li").forEach(function (li, i) { li.style.setProperty("--i", i); });
    io.observe(l);
    new IntersectionObserver(function (es, o) { es.forEach(function (e) { if (e.isIntersecting) { l.classList.add("is-in"); o.disconnect(); } }); }).observe(l);
  });

  // app mock: a delivery run, one network after another
  function setPill(p, state, text) {
    p.classList.remove("is-queued", "is-pending");
    if (state) p.classList.add(state);
    var t = p.querySelector(".pill__text"); if (t) t.textContent = text;
  }
  document.querySelectorAll('[data-component="app-mock"]').forEach(function (app) {
    if (reduce) return;
    var pills = app.querySelectorAll("[data-status]");
    var summary = app.querySelector("[data-summary]");
    pills.forEach(function (p) { setPill(p, "is-queued", "Queued"); });
    if (summary) setPill(summary, "is-pending", "Going out");
    var started = false;
    new IntersectionObserver(function (es, o) {
      es.forEach(function (e) {
        if (!e.isIntersecting || started) return;
        started = true; o.disconnect();
        pills.forEach(function (p, i) {
          setTimeout(function () { setPill(p, "is-pending", "Posting as you"); }, 400 + i * 520);
          setTimeout(function () { setPill(p, null, "Went out"); if (i === pills.length - 1 && summary) setPill(summary, null, "Went out"); }, 1000 + i * 520);
        });
      });
    }, { threshold: 0.2 }).observe(app);
  });

  // explorer: one message, each network's fit
  var input = document.querySelector("[data-x-input]");
  if (input) {
    var rules = {
      linkedin: { max: 3000, fit: function (s) { return s; } },
      x: { max: 280, fit: function (s) { return s; } },
      reddit: { max: 300, fit: function (s) { return "Title: " + firstSentence(s) + "\n\n" + s.slice(firstSentence(s).length).trim(); }, count: function (s) { return firstSentence(s).length; } },
      hn: { max: 80, fit: function (s) { return "Title: " + firstSentence(s).replace(/[.!]$/, ""); }, count: function (s) { return firstSentence(s).replace(/[.!]$/, "").length; } },
      slack: { max: 4000, fit: function (s) { return s; } },
      bluesky: { max: 300, fit: function (s) { return s; } }
    };
    function firstSentence(s) { var m = s.match(/^(.+?[.!?])(\s|$)/); return (m ? m[1] : s).trim(); }
    function render() {
      var s = input.value.trim() || "Type your announcement above.";
      Object.keys(rules).forEach(function (k) {
        var card = document.querySelector('[data-x-card="' + k + '"]'); if (!card) return;
        var r = rules[k], n = r.count ? r.count(s) : r.fit(s).length;
        card.querySelector("[data-x-text]").textContent = r.fit(s);
        var c = card.querySelector("[data-x-count]");
        c.textContent = n + " / " + r.max; c.classList.toggle("is-over", n > r.max);
      });
    }
    input.addEventListener("input", render);
    document.querySelectorAll("[data-x-platform]").forEach(function (cb) {
      cb.addEventListener("change", function () {
        var card = document.querySelector('[data-x-card="' + cb.dataset.xPlatform + '"]'); if (card) card.hidden = !cb.checked;
      });
    });
    render();
  }
})();
