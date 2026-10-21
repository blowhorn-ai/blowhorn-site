/* Internal comparison tables (layouts/_partials/cmp-tools.html, emitted by
   the internal-compare and internal-personas shortcodes). Two behaviours:
   - Note tooltips: status cells keep only their symbol; the note that the
     CSV keeps in a "<provider> notes" column (or the caveat after an em
     dash in the cell) rides on the symbol in data-note and shows here on
     hover or keyboard focus, positioned clear of the table's scroll
     regions. Inside the expanded dialog the tooltip moves into the
     dialog so it paints in the dialog's top layer.
   - Maximize: a block's Maximize button clones its table region into the
     dialog; the dialog's own button toggles full screen. */
(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState !== 'loading') {
      fn();
    } else {
      document.addEventListener('DOMContentLoaded', fn);
    }
  }

  ready(function () {
    var tip = document.getElementById('cmp-tip');
    var dialog = document.getElementById('cmp-dialog');
    if (!tip || !dialog) {
      return;
    }
    var body = dialog.querySelector('.cmp-dialog-body');
    var current = null;

    function show(el) {
      var note = el.getAttribute('data-note');
      if (!note) {
        return;
      }
      current = el;
      var host = document.body;
      if (document.fullscreenElement && document.fullscreenElement.contains(el)) {
        host = document.fullscreenElement;
      } else if (dialog.open && dialog.contains(el)) {
        host = dialog;
      }
      if (tip.parentNode !== host) {
        host.appendChild(tip);
      }
      tip.textContent = note;
      tip.hidden = false;
      var r = el.getBoundingClientRect();
      var x = r.left + r.width / 2 - tip.offsetWidth / 2;
      x = Math.min(Math.max(8, x), window.innerWidth - tip.offsetWidth - 8);
      var y = r.top - tip.offsetHeight - 10;
      if (y < 8) {
        y = r.bottom + 10;
      }
      tip.style.left = x + 'px';
      tip.style.top = y + 'px';
    }

    function hide() {
      tip.hidden = true;
      current = null;
    }

    function notedTarget(node) {
      return node && node.closest ? node.closest('[data-note]') : null;
    }

    document.addEventListener('mouseover', function (e) {
      var el = notedTarget(e.target);
      if (el) {
        if (el !== current) {
          show(el);
        }
      } else if (current) {
        hide();
      }
    });
    document.addEventListener('mouseout', function (e) {
      if (current && !current.contains(e.relatedTarget) && notedTarget(e.relatedTarget) !== current) {
        hide();
      }
    });
    document.addEventListener('focusin', function (e) {
      var el = notedTarget(e.target);
      if (el) {
        show(el);
      }
    });
    document.addEventListener('focusout', function () {
      hide();
    });
    document.addEventListener('scroll', hide, true);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        hide();
      }
    });

    document.addEventListener('click', function (e) {
      var maxBtn = e.target.closest ? e.target.closest('[data-cmp-maximize]') : null;
      if (maxBtn) {
        var block = maxBtn.closest('[data-cmp-block]');
        var region = block ? block.querySelector('[data-cmp-region]') : null;
        if (region && dialog.showModal) {
          body.innerHTML = '';
          var clone = region.cloneNode(true);
          clone.removeAttribute('id');
          body.appendChild(clone);
          hide();
          dialog.showModal();
        }
        return;
      }
      if (e.target.closest && e.target.closest('[data-cmp-close]')) {
        dialog.close();
        return;
      }
      if (e.target.closest && e.target.closest('[data-cmp-fs]')) {
        // Full screen targets the dialog's inner wrapper: a <dialog>
        // itself is not a valid full-screen element in Chrome.
        var inner = document.getElementById('cmp-dialog-inner');
        if (document.fullscreenElement) {
          document.exitFullscreen();
        } else if (inner && inner.requestFullscreen) {
          inner.requestFullscreen();
        }
      }
    });
    dialog.addEventListener('click', function (e) {
      if (e.target === dialog) {
        dialog.close();
      }
    });
    dialog.addEventListener('close', function () {
      body.innerHTML = '';
      hide();
      if (document.fullscreenElement) {
        document.exitFullscreen();
      }
    });
  });
})();
