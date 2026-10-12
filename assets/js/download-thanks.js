// Starts the Blowhorn disk image download when /download/thanks/ opens, from
// the page's own "click here" link (#download-fallback), so the two never
// disagree. A reload within a minute does not download a second copy.
(function () {
  "use strict";

  var link = document.getElementById("download-fallback");
  if (!link) {
    return;
  }
  var key = "blowhorn-download-started";
  try {
    var last = Number(window.sessionStorage.getItem(key));
    if (last && Date.now() - last < 60000) {
      return;
    }
    window.sessionStorage.setItem(key, String(Date.now()));
  } catch (e) {
    // Storage blocked: download anyway.
  }
  window.setTimeout(function () {
    window.location.href = link.href;
  }, 400);
})();
