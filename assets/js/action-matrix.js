/* Action matrix at /integrations/actions/. Without this file each cell keeps
   its title tooltip and visually hidden label. With it: one shared tooltip
   follows hover and keyboard focus (Escape closes it), and the hovered
   cell's row and column light up. Text comes from the cell's data-tip
   attributes, rendered from data/actions.json and data/platforms/. */
(function () {
  document.querySelectorAll("[data-action-matrix]").forEach(function (root) {
    var tip = root.querySelector(".matrix-tip");
    var table = root.querySelector("table");
    if (!tip || !table) return;
    var tipTitle = tip.querySelector(".matrix-tip-title");
    var tipBody = tip.querySelector(".matrix-tip-body");
    var heads = Array.prototype.slice.call(table.querySelectorAll(".matrix-heads > *"));
    var current = null;
    root.classList.add("is-enhanced");

    function column(index, on) {
      if (heads[index]) heads[index].classList.toggle("is-hot", on);
      table.querySelectorAll(".matrix-row").forEach(function (row) {
        var cell = row.cells[index];
        if (cell) cell.classList.toggle("is-hot-col", on);
      });
    }

    function place(el) {
      var r = el.getBoundingClientRect();
      tip.style.left = "0px";
      tip.style.top = "0px";
      var w = tip.offsetWidth;
      var h = tip.offsetHeight;
      var gap = 10;
      var x = r.left + r.width / 2 - w / 2;
      x = Math.max(8, Math.min(x, window.innerWidth - w - 8));
      var y = r.top - h - gap;
      tip.classList.toggle("is-below", y < 8);
      if (y < 8) y = r.bottom + gap;
      tip.style.left = Math.round(x) + "px";
      tip.style.top = Math.round(y) + "px";
    }

    function show(el) {
      if (current && current !== el) hide();
      current = el;
      tipTitle.textContent = el.getAttribute("data-tip-title") || "";
      tipBody.textContent = el.getAttribute("data-tip") || "";
      tip.hidden = false;
      el.setAttribute("aria-describedby", tip.id);
      place(el);
      var td = el.closest("td");
      if (td) {
        td.parentNode.classList.add("is-hot");
        column(td.cellIndex, true);
      }
    }

    function hide() {
      if (!current) return;
      var td = current.closest("td");
      if (td) {
        td.parentNode.classList.remove("is-hot");
        column(td.cellIndex, false);
      }
      current.removeAttribute("aria-describedby");
      current = null;
      tip.hidden = true;
    }

    root.querySelectorAll("[data-tip]").forEach(function (el) {
      el.removeAttribute("title");
      el.addEventListener("mouseenter", function () { show(el); });
      el.addEventListener("mouseleave", hide);
      el.addEventListener("focus", function () { show(el); });
      el.addEventListener("blur", hide);
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") hide();
    });
    window.addEventListener("scroll", function () { if (current) place(current); }, { passive: true });
    var scroller = root.querySelector(".matrix-scroll");
    if (scroller) scroller.addEventListener("scroll", function () { if (current) place(current); }, { passive: true });
  });
})();
