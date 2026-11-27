// Interactive MCP Client Configuration Generator
// Handles switching between MCP clients (Cursor, Claude Code, VS Code, Claude Desktop, Windsurf, Zed, Gemini CLI)
// and server modes (Hosted Server HTTP vs Local Engine stdio), with keyboard navigation and localStorage persistence.
(function () {
  "use strict";

  var STORAGE_MODE_KEY = "blowhorn-mcp-mode";
  var STORAGE_CLIENT_KEY = "blowhorn-mcp-client";

  function initGenerator(root) {
    if (!root) return;
    root.classList.add("is-enhanced");

    var modeRadios = root.querySelectorAll('input[name="mcp-mode"]');
    var clientTabs = Array.prototype.slice.call(root.querySelectorAll("[data-mcp-client]"));
    var clientPanels = Array.prototype.slice.call(root.querySelectorAll("[data-panel-client]"));

    var currentMode = "hosted";
    var currentClient = clientTabs.length ? clientTabs[0].getAttribute("data-mcp-client") : "claude-code";

    try {
      var savedMode = window.localStorage.getItem(STORAGE_MODE_KEY);
      if (savedMode === "hosted" || savedMode === "local") currentMode = savedMode;
      var savedClient = window.localStorage.getItem(STORAGE_CLIENT_KEY);
      if (savedClient && clientTabs.some(function (tab) { return tab.getAttribute("data-mcp-client") === savedClient; })) {
        currentClient = savedClient;
      }
    } catch (e) {}

    function update() {
      modeRadios.forEach(function (radio) {
        radio.checked = radio.value === currentMode;
        var parentLabel = radio.closest(".mcp-mode-label");
        if (parentLabel) parentLabel.classList.toggle("is-active", radio.checked);
      });

      clientTabs.forEach(function (tab) {
        var on = tab.getAttribute("data-mcp-client") === currentClient;
        tab.classList.toggle("is-on", on);
        tab.setAttribute("aria-selected", on ? "true" : "false");
        tab.setAttribute("tabindex", on ? "0" : "-1");
      });

      clientPanels.forEach(function (panel) {
        var isClient = panel.getAttribute("data-panel-client") === currentClient;
        panel.hidden = !isClient;
        if (isClient) {
          panel.querySelectorAll("[data-pane-mode]").forEach(function (pane) {
            pane.hidden = pane.getAttribute("data-pane-mode") !== currentMode;
          });
        }
      });
    }

    modeRadios.forEach(function (radio) {
      radio.addEventListener("change", function () {
        if (radio.checked) {
          currentMode = radio.value;
          try {
            window.localStorage.setItem(STORAGE_MODE_KEY, currentMode);
          } catch (e) {}
          update();
        }
      });
    });

    clientTabs.forEach(function (tab, index) {
      tab.addEventListener("click", function (ev) {
        ev.preventDefault();
        currentClient = tab.getAttribute("data-mcp-client");
        try {
          window.localStorage.setItem(STORAGE_CLIENT_KEY, currentClient);
        } catch (e) {}
        update();
      });

      tab.addEventListener("keydown", function (ev) {
        var next = index;
        if (ev.key === "ArrowRight" || ev.key === "ArrowDown") next = (index + 1) % clientTabs.length;
        else if (ev.key === "ArrowLeft" || ev.key === "ArrowUp") next = (index - 1 + clientTabs.length) % clientTabs.length;
        else if (ev.key === "Home") next = 0;
        else if (ev.key === "End") next = clientTabs.length - 1;
        else return;

        ev.preventDefault();
        clientTabs[next].focus();
        currentClient = clientTabs[next].getAttribute("data-mcp-client");
        try {
          window.localStorage.setItem(STORAGE_CLIENT_KEY, currentClient);
        } catch (e) {}
        update();
      });
    });

    update();
  }

  function setup() {
    document.querySelectorAll("[data-mcp-generator]").forEach(initGenerator);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }
})();
