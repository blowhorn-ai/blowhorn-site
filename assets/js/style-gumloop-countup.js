/* Gumloop direct: count the hero metrics up from 0 on load, copied from
   gumloop.com's count-up metrics. No dependencies. The final value is
   already in the markup, so readers without script, and readers who ask
   for reduced motion, see the finished number at once. */
(function () {
  var els = document.querySelectorAll("[data-gumloop-count]");
  if (!els.length) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  els.forEach(function (el) {
    var target = parseInt(el.getAttribute("data-gumloop-count"), 10);
    if (isNaN(target)) return;
    if (reduce) {
      el.textContent = String(target);
      return;
    }
    var start = null;
    var dur = 1200;
    function tick(now) {
      if (start === null) start = now;
      var p = Math.min((now - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = String(Math.round(target * eased));
      if (p < 1) requestAnimationFrame(tick);
    }
    el.textContent = "0";
    requestAnimationFrame(tick);
  });
})();
