// Sidebar toggle for /docs/ pages. Bootstrap's collapse plugin is not
// shipped (its bundle names documentation hosts, which the privacy page
// forbids), so the Docsy toggle button is wired here: one class,
// no dependency. The skin shows #td-section-nav when it carries .show
// on narrow viewports, and always on wide ones.
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
    var button = document.querySelector('.td-sidebar__toggle');
    var nav = document.getElementById('td-section-nav');
    if (!button || !nav) {
      return;
    }
    button.addEventListener('click', function () {
      var open = nav.classList.toggle('show');
      button.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  // Table of contents collapse (layouts/_partials/toc.html): the toggle
  // in the TOC header collapses the whole TOC column to a rail so the
  // content takes the width; the choice persists across docs pages.
  ready(function () {
    var wrap = document.querySelector('.docs-wrap');
    var btn = document.querySelector('[data-toc-toggle]');
    if (!wrap || !btn) {
      return;
    }
    var label = btn.querySelector('.td-toc-toggle__label');
    var collapsed = false;
    try {
      collapsed = window.localStorage.getItem('blowhorn-toc-collapsed') === '1';
    } catch (e) { /* private mode: session-only state is fine */ }
    function apply(state) {
      wrap.classList.toggle('toc-collapsed', state);
      btn.setAttribute('aria-expanded', state ? 'false' : 'true');
      if (label) {
        label.textContent = state ? 'Show table of contents' : 'Hide table of contents';
      }
    }
    apply(collapsed);
    btn.addEventListener('click', function () {
      collapsed = !collapsed;
      try {
        window.localStorage.setItem('blowhorn-toc-collapsed', collapsed ? '1' : '0');
      } catch (e) { /* the toggle still works for this page */ }
      apply(collapsed);
    });
  });

  // Collapsible sections in the sidebar tree (layouts/_partials/sidebar-tree.html):
  // each chevron button shows or hides the list it controls.
  ready(function () {
    var folds = document.querySelectorAll('.td-sidebar-fold');
    Array.prototype.forEach.call(folds, function (fold) {
      fold.addEventListener('click', function () {
        var list = document.getElementById(fold.getAttribute('aria-controls'));
        if (!list) {
          return;
        }
        var open = fold.getAttribute('aria-expanded') !== 'true';
        fold.setAttribute('aria-expanded', open ? 'true' : 'false');
        list.hidden = !open;
      });
    });
  });
})();
