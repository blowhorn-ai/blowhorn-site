/* The /demo/ simulation. Client-side only: the queue lives in this page,
   nothing is posted, and nothing leaves the browser. The tabs component
   (assets/js/tabs.js, bundled with this file) owns the formation picker;
   this file watches which tab it selects. */
(function () {
  "use strict";

  var SENDERS = {
    "muster": ["Desk rig", "Laptop", "Studio box"],
    "battalion-map": ["Desk rig (HQ)", "Laptop (Unit 02)", "Studio box (Unit 03)"],
    "one-thunder": ["You", "Designer", "Engineer"],
    "call-to-arms": ["Enlist", "Muster", "Rally", "Thunder"]
  };
  var SLOT_MINUTES = 90;
  var STEP_MS = 650;

  var tabsRoot = document.querySelector('[data-tabs-id="demo-machine"]');
  var queueList = document.querySelector("[data-demo-queue]");
  var emptyNote = document.querySelector("[data-demo-empty]");
  var scheduleBody = document.querySelector("[data-demo-schedule]");
  var runButton = document.querySelector("[data-demo-run]");
  var resetButton = document.querySelector("[data-demo-reset]");
  var summary = document.querySelector("[data-demo-summary]");
  var form = document.querySelector("[data-demo-form]");
  var pickName = document.querySelector("[data-demo-pick-name]");
  var pickLine = document.querySelector("[data-demo-pick-line]");
  if (!tabsRoot || !queueList || !scheduleBody || !runButton || !resetButton) return;

  var initialSchedule = scheduleBody.innerHTML;
  var queue = [];
  var timers = [];
  var running = false;

  function selectedFormation() {
    var on = tabsRoot.querySelector("[data-tab].is-on");
    if (on) return on.getAttribute("data-tab");
    var first = tabsRoot.querySelector("[data-tab]");
    return first ? first.getAttribute("data-tab") : "muster";
  }

  function formationName(id) {
    var pane = document.getElementById("demo-machine-" + id);
    if (!pane) return id;
    var h = pane.querySelector("h3");
    return h ? h.textContent : id;
  }

  function formationHeadline(id) {
    var pane = document.getElementById("demo-machine-" + id);
    if (!pane) return "";
    var p = pane.querySelector("p");
    return p ? p.textContent : "";
  }

  function senders() {
    return SENDERS[selectedFormation()] || SENDERS.muster;
  }

  function slotTime(index) {
    var start = new Date();
    start.setDate(start.getDate() + 1);
    start.setHours(9, 0, 0, 0);
    var at = new Date(start.getTime() + index * SLOT_MINUTES * 60000);
    return new Intl.DateTimeFormat("en-US", {
      weekday: "short", hour: "numeric", minute: "2-digit"
    }).format(at);
  }

  function keyOf(platform, text) {
    return platform + "\n" + text;
  }

  function sampleButton(key) {
    var buttons = document.querySelectorAll("[data-demo-add]");
    for (var i = 0; i < buttons.length; i++) {
      if (keyOf(buttons[i].getAttribute("data-demo-platform"), buttons[i].getAttribute("data-demo-text")) === key) {
        return buttons[i];
      }
    }
    return null;
  }

  function renderQueue() {
    queueList.innerHTML = "";
    queue.forEach(function (item) {
      var li = document.createElement("li");
      var label = document.createElement("span");
      label.textContent = item.platform + ": " + item.text;
      var remove = document.createElement("button");
      remove.type = "button";
      remove.textContent = "Remove";
      remove.setAttribute("data-demo-remove", keyOf(item.platform, item.text));
      li.appendChild(label);
      li.appendChild(document.createTextNode(" "));
      li.appendChild(remove);
      queueList.appendChild(li);
    });
    if (emptyNote) emptyNote.hidden = queue.length > 0;
  }

  function renderSchedule() {
    scheduleBody.innerHTML = "";
    if (!queue.length) {
      scheduleBody.innerHTML = initialSchedule;
      return;
    }
    var from = senders();
    queue.forEach(function (item, i) {
      var row = document.createElement("tr");
      var time = document.createElement("td");
      time.textContent = slotTime(i);
      var platform = document.createElement("td");
      platform.textContent = item.platform;
      var post = document.createElement("td");
      post.textContent = item.text;
      var sender = document.createElement("td");
      sender.textContent = from[i % from.length];
      var status = document.createElement("td");
      status.textContent = "Queued";
      status.setAttribute("data-demo-status", String(i));
      row.appendChild(time);
      row.appendChild(platform);
      row.appendChild(post);
      row.appendChild(sender);
      row.appendChild(status);
      scheduleBody.appendChild(row);
    });
  }

  function addToQueue(platform, text) {
    var item = { platform: platform, text: text };
    var key = keyOf(platform, text);
    if (queue.some(function (q) { return keyOf(q.platform, q.text) === key; })) return;
    queue.push(item);
    var button = sampleButton(key);
    if (button) {
      button.disabled = true;
      button.textContent = "Added to queue";
    }
    renderQueue();
    renderSchedule();
  }

  function removeFromQueue(key) {
    queue = queue.filter(function (q) { return keyOf(q.platform, q.text) !== key; });
    var button = sampleButton(key);
    if (button) {
      button.disabled = false;
      button.textContent = "Add to queue";
    }
    renderQueue();
    renderSchedule();
  }

  function clearTimers() {
    timers.forEach(function (t) { window.clearTimeout(t); });
    timers = [];
  }

  function runSimulation() {
    if (running) return;
    if (!queue.length) {
      if (summary) summary.textContent = "Add at least one post to your queue first.";
      return;
    }
    running = true;
    runButton.disabled = true;
    if (summary) summary.textContent = "";
    var rows = queue.length;
    for (var i = 0; i < rows; i++) {
      (function (index) {
        timers.push(window.setTimeout(function () {
          var cell = scheduleBody.querySelector('[data-demo-status="' + index + '"]');
          if (cell) cell.textContent = "Posting…";
        }, index * STEP_MS));
        timers.push(window.setTimeout(function () {
          var cell = scheduleBody.querySelector('[data-demo-status="' + index + '"]');
          if (cell) cell.textContent = "Posted";
        }, index * STEP_MS + Math.floor(STEP_MS / 2)));
      })(i);
    }
    timers.push(window.setTimeout(function () {
      running = false;
      runButton.disabled = false;
      var platforms = {};
      queue.forEach(function (q) { platforms[q.platform] = true; });
      var nPlatforms = Object.keys(platforms).length;
      if (summary) {
        summary.textContent = "Posted " + queue.length + (queue.length === 1 ? " post" : " posts") +
          " across " + nPlatforms + (nPlatforms === 1 ? " platform" : " platforms") +
          " as " + formationName(selectedFormation()) +
          ". This was a simulation: nothing was sent, and nothing left your browser.";
      }
    }, rows * STEP_MS));
  }

  function resetDemo() {
    clearTimers();
    running = false;
    runButton.disabled = false;
    queue = [];
    document.querySelectorAll("[data-demo-add]").forEach(function (button) {
      button.disabled = false;
      button.textContent = "Add to queue";
    });
    if (form) form.reset();
    if (summary) summary.textContent = "";
    renderQueue();
    renderSchedule();
  }

  function syncFormation() {
    var id = selectedFormation();
    if (pickName) pickName.textContent = formationName(id);
    if (pickLine) pickLine.textContent = formationHeadline(id);
    if (queue.length) renderSchedule();
  }

  document.querySelectorAll("[data-demo-add]").forEach(function (button) {
    button.addEventListener("click", function () {
      addToQueue(button.getAttribute("data-demo-platform"), button.getAttribute("data-demo-text"));
    });
  });

  queueList.addEventListener("click", function (event) {
    var key = event.target && event.target.getAttribute ? event.target.getAttribute("data-demo-remove") : null;
    if (key) removeFromQueue(key);
  });

  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var text = document.getElementById("demo-custom-text");
      var platform = document.getElementById("demo-custom-platform");
      if (!text || !platform) return;
      var value = text.value.trim();
      if (!value) {
        if (summary) summary.textContent = "Write the post first, then add it to the queue.";
        return;
      }
      addToQueue(platform.value, value);
      text.value = "";
      text.focus();
    });
  }

  runButton.addEventListener("click", runSimulation);
  resetButton.addEventListener("click", resetDemo);

  if (window.MutationObserver) {
    var observer = new MutationObserver(function () { syncFormation(); });
    observer.observe(tabsRoot, { attributes: true, subtree: true, attributeFilter: ["class", "aria-selected"] });
  }
  tabsRoot.addEventListener("click", function () {
    window.setTimeout(syncFormation, 0);
  });

  syncFormation();
})();
