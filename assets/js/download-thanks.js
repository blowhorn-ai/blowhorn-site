// Starts the Blowhorn disk image download when /download/thanks/ opens, from
// the page's own "click here" link (#download-fallback), so the two never
// disagree. A reload of this page does not download a second copy; a new
// visit from the download button always does.
(function () {
  "use strict";

  var link = document.getElementById("download-fallback");
  if (!link) {
    return;
  }
  var nav = window.performance && performance.getEntriesByType && performance.getEntriesByType("navigation")[0];
  if (nav && nav.type === "reload") {
    return;
  }
  window.setTimeout(function () {
    window.location.href = link.href;
  }, 400);
})();
