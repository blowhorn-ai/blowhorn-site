// Brand page: the copy buttons beside each colour value. The values are plain,
// selectable text; the buttons only appear when the Clipboard API is there.
(function () {
  "use strict";

  if (!navigator.clipboard || !window.isSecureContext) {
    return;
  }
  var status = document.querySelector("[data-copy-status]");
  var buttons = document.querySelectorAll("button[data-copy]");
  Array.prototype.forEach.call(buttons, function (button) {
    button.hidden = false;
    button.addEventListener("click", function () {
      var value = button.getAttribute("data-copy");
      navigator.clipboard.writeText(value).then(function () {
        button.textContent = "Copied";
        button.classList.add("is-copied");
        if (status) {
          status.textContent = value + " copied";
        }
        window.setTimeout(function () {
          button.textContent = "Copy";
          button.classList.remove("is-copied");
        }, 1600);
      });
    });
  });
})();
