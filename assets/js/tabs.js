/* WAI-ARIA tabs. Without this file every pane stays visible (stacked) and
   the tablist is in-page links. With it: one pane, arrow keys, and a shared
   localStorage key so picking CLI on one set switches every set in the group. */
(function () {
  var STORAGE_KEY = "blowhorn-tab-surface";

  function panelsOf(root) {
    return Array.prototype.slice.call(root.querySelectorAll("[data-tab-panel]"));
  }

  function tabsOf(root) {
    return Array.prototype.slice.call(root.querySelectorAll("[data-tab]"));
  }

  function select(root, id, persist) {
    var tabs = tabsOf(root);
    var panels = panelsOf(root);
    var match = false;
    panels.forEach(function (panel) {
      if (panel.getAttribute("data-tab-panel") === id) match = true;
    });
    if (!match) id = panels.length ? panels[0].getAttribute("data-tab-panel") : id;
    tabs.forEach(function (tab) {
      var on = tab.getAttribute("data-tab") === id;
      tab.classList.toggle("is-on", on);
      tab.setAttribute("aria-selected", on ? "true" : "false");
      tab.setAttribute("tabindex", on ? "0" : "-1");
      if (on) tab.setAttribute("aria-current", "true");
      else tab.removeAttribute("aria-current");
    });
    panels.forEach(function (panel) {
      var on = panel.getAttribute("data-tab-panel") === id;
      panel.hidden = !on;
    });
    if (persist) {
      var group = root.getAttribute("data-tabs-group");
      if (group) {
        try {
          window.localStorage.setItem(STORAGE_KEY + ":" + group, id);
        } catch (err) {}
        document.querySelectorAll('[data-tabs-group="' + group + '"]').forEach(function (other) {
          if (other !== root) select(other, id, false);
        });
      }
    }
  }

  function saved(group) {
    if (!group) return "";
    try {
      return window.localStorage.getItem(STORAGE_KEY + ":" + group) || "";
    } catch (err) {
      return "";
    }
  }

  function enhance(root) {
    var tabs = tabsOf(root);
    var panels = panelsOf(root);
    if (!tabs.length || !panels.length) return;
    root.classList.add("is-enhanced");
    var list = root.querySelector(".tabs-list");
    if (list) list.setAttribute("role", "tablist");
    tabs.forEach(function (tab, index) {
      var id = tab.getAttribute("data-tab");
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-controls", root.getAttribute("data-tabs-id") + "-" + id);
      tab.addEventListener("click", function (ev) {
        ev.preventDefault();
        select(root, id, true);
      });
      tab.addEventListener("keydown", function (ev) {
        var next = index;
        if (ev.key === "ArrowRight" || ev.key === "ArrowDown") next = (index + 1) % tabs.length;
        else if (ev.key === "ArrowLeft" || ev.key === "ArrowUp") next = (index - 1 + tabs.length) % tabs.length;
        else if (ev.key === "Home") next = 0;
        else if (ev.key === "End") next = tabs.length - 1;
        else return;
        ev.preventDefault();
        tabs[next].focus();
        select(root, tabs[next].getAttribute("data-tab"), true);
      });
    });
    panels.forEach(function (panel) {
      panel.setAttribute("role", "tabpanel");
      var id = panel.getAttribute("data-tab-panel");
      var tab = root.querySelector('[data-tab="' + id + '"]');
      if (tab && tab.id) panel.setAttribute("aria-labelledby", tab.id);
    });
    var group = root.getAttribute("data-tabs-group");
    var initial = saved(group);
    var hash = (window.location.hash || "").replace(/^#/, "");
    var prefix = root.getAttribute("data-tabs-id") || "";
    if (hash && prefix && hash.indexOf(prefix + "-") === 0) {
      initial = hash.slice(prefix.length + 1);
    }
    select(root, initial || tabs[0].getAttribute("data-tab"), false);
  }

  document.querySelectorAll("[data-tabs]").forEach(enhance);
})();
