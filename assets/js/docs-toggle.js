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
