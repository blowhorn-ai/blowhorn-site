// Copy to clipboard for anything a reader might run.
// 1. Terminal code cards (layouts/_partials/code-card.html): copies the code
//    only. "$" prompts (.term-ps) are dropped; sample-output cards have no
//    button at all.
// 2. Inline `blowhorn ...` commands in prose get a small copy button.
// Pattern after layer5io/docs click-to-copy.js (Apache-2.0).
(function () {
  if (!navigator.clipboard) return;

  var ICON = '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" focusable="false"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h8"/></svg>';

  function textOf(node) {
    var clone = node.cloneNode(true);
    clone.querySelectorAll('.term-ps').forEach(function (n) { n.remove(); });
    return clone.textContent.replace(/\s+$/, '') + '\n';
  }

  function wire(btn, getText, label, status) {
    var timer;
    btn.addEventListener('click', function () {
      navigator.clipboard.writeText(getText()).then(function () {
        btn.classList.add('is-copied');
        if (label) label.textContent = 'Copied';
        status.textContent = 'Copied';
      }, function () {
        status.textContent = 'Copy failed. Select the text and press Command C.';
      }).then(function () {
        clearTimeout(timer);
        timer = setTimeout(function () {
          btn.classList.remove('is-copied');
          if (label) label.textContent = 'Copy';
          status.textContent = '';
        }, 2200);
      });
    });
  }

  document.querySelectorAll('.term').forEach(function (card) {
    var btn = card.querySelector('.term-copy');
    var code = card.querySelector('pre code') || card.querySelector('pre');
    var status = card.querySelector('.term-status');
    if (!btn || !code || !status) return;
    btn.hidden = false;
    wire(btn, function () { return textOf(code); }, btn.querySelector('.term-copy-text'), status);
  });

  var status = document.createElement('span');
  status.className = 'visually-hidden';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  var used = false;
  document.querySelectorAll('main :not(pre) > code, .td-content :not(pre) > code').forEach(function (code) {
    if (code.dataset.copyWired) return;
    code.dataset.copyWired = '1';
    var cmd = code.textContent.trim();
    if (!/^blowhorn [a-z]/.test(cmd) || /[<>]|\.\.\./.test(cmd)) return;
    if (code.closest('a, h1, h2, h3, h4, h5, h6, button, summary, .term')) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'code-copy-inline';
    btn.setAttribute('aria-label', 'Copy command: ' + cmd);
    btn.innerHTML = ICON;
    code.insertAdjacentElement('afterend', btn);
    wire(btn, function () { return cmd; }, null, status);
    used = true;
  });
  if (used) document.body.appendChild(status);
})();
