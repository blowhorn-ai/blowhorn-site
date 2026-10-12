// Copy buttons for terminal code cards (layouts/_partials/code-card.html).
// Copies the code text only: "$" prompts are CSS pseudo-elements and never
// part of the text. Pattern from layer5io/docs click-to-copy.js (Apache-2.0).
(function () {
  if (!navigator.clipboard) return;
  document.querySelectorAll('.term').forEach(function (card) {
    var btn = card.querySelector('.term-copy');
    var code = card.querySelector('pre code') || card.querySelector('pre');
    var label = btn && btn.querySelector('.term-copy-text');
    var status = card.querySelector('.term-status');
    if (!btn || !code) return;
    btn.hidden = false;
    var timer;
    btn.addEventListener('click', function () {
      var text = code.textContent.replace(/\s+$/, '') + '\n';
      navigator.clipboard.writeText(text).then(function () {
        btn.classList.add('is-copied');
        label.textContent = 'Copied';
        status.textContent = 'Copied to clipboard';
      }, function () {
        label.textContent = 'Press Cmd+C';
        status.textContent = 'Copy failed. Select the code and press Command C.';
      }).then(function () {
        clearTimeout(timer);
        timer = setTimeout(function () {
          btn.classList.remove('is-copied');
          label.textContent = 'Copy';
          status.textContent = '';
        }, 2200);
      });
    });
  });
})();
