/* Card variants after a filter (DESIGN.md, "Cards"). A grid that a filter can
   thin out prints its variant cycle as data-card-cycle (from
   layouts/_partials/card-cycle.html). Hiding cards would put two of the same
   variant side by side, so after every filter the visible cards are dealt the
   cycle again, in order. Bundled ahead of resources.js and action-filter.js,
   which call it. */
(function () {
  "use strict";

  window.blowhornCardCycle = function (root) {
    var grids = root.matches && root.matches("[data-card-cycle]") ? [root] : root.querySelectorAll("[data-card-cycle]");
    Array.prototype.forEach.call(grids, function (grid) {
      var cycle = (grid.getAttribute("data-card-cycle") || "").split(/\s+/).filter(Boolean);
      if (cycle.length < 2) return;
      var selector = cycle.map(function (name) { return "." + name; }).join(", ");
      var k = 0;
      Array.prototype.forEach.call(grid.querySelectorAll(selector), function (card) {
        var hiddenBy = card.closest("[hidden]");
        if (hiddenBy && grid.contains(hiddenBy)) return;
        cycle.forEach(function (name) { card.classList.remove(name); });
        card.classList.add(cycle[k % cycle.length]);
        k += 1;
      });
    });
  };
})();
