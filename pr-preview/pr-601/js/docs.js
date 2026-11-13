/* Offline search for the /docs/ section.
 *
 * From Docsy v0.14.3 assets/js/offline-search.js (Apache-2.0), itself
 * adapted from code by Matt Walters. Two changes from upstream:
 * - the attribution comment no longer names a blog URL, because a shipped
 *   script may not reference another host (see the privacy page);
 * - results render in an inline box under the search field instead of a
 *   Bootstrap popover, because Bootstrap's JavaScript is not shipped
 *   (same reason). The index, the query, and the result entries are
 *   unchanged.
 */

(function ($) {
  'use strict';

  $(document).ready(function () {
    const $searchInput = $('.td-search input');

    //
    // Register handler
    //

    $searchInput.on('change', (event) => {
      render($(event.target));

      // Hide keyboard on mobile browser
      $searchInput.blur();
    });

    // Prevent reloading page by enter key on sidebar search.
    $searchInput.closest('form').on('submit', () => {
      return false;
    });

    //
    // Lunr
    //

    let idx = null; // Lunr index
    const resultDetails = new Map(); // Will hold the data for the search results (titles and summaries)

    // Set up for an Ajax call to request the JSON data file that is created by Hugo's build process
    $.ajax($searchInput.data('offline-search-index-json-src')).then((data) => {
      idx = lunr(function () {
        this.ref('ref');

        // If you added more searchable fields to the search index, list them here.
        // Here you can specify searchable fields to the search index - e.g. individual toxonomies for you project
        // With "boost" you can add weighting for specific (default weighting without boost: 1)
        this.field('title', { boost: 5 });
        this.field('categories', { boost: 3 });
        this.field('tags', { boost: 3 });
        // this.field('projects', { boost: 3 }); // example for an individual toxonomy called projects
        this.field('description', { boost: 2 });
        this.field('body');

        data.forEach((doc) => {
          this.add(doc);

          resultDetails.set(doc.ref, {
            title: doc.title,
            excerpt: doc.excerpt,
          });
        });
      });

      $searchInput.trigger('change');
    });

    const render = ($targetSearchInput) => {
      //
      // Dispose existing results
      //

      $('.td-offline-search-results').remove();

      //
      // Search
      //

      if (idx === null) {
        return;
      }

      const searchQuery = $targetSearchInput.val();
      if (searchQuery === '') {
        return;
      }

      const results = idx
        .query((q) => {
          const tokens = lunr.tokenizer(searchQuery.toLowerCase());
          tokens.forEach((token) => {
            const queryString = token.toString();
            q.term(queryString, {
              boost: 100,
            });
            q.term(queryString, {
              wildcard:
                lunr.Query.wildcard.LEADING | lunr.Query.wildcard.TRAILING,
              boost: 10,
            });
            q.term(queryString, {
              editDistance: 2,
            });
          });
        })
        .slice(0, $targetSearchInput.data('offline-search-max-results'));

      //
      // Make result html
      //

      const $box = $('<div>').addClass('td-offline-search-results');

      $box.append(
        $('<div>')
          .css({
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1em',
          })
          .append(
            $('<span>').text('Search results').css({ fontWeight: 'bold' })
          )
          .append(
            $('<button>')
              .attr({ type: 'button', 'aria-label': 'Close search results' })
              .addClass('td-offline-search-results__close')
              .text('\u00d7')
              .on('click', () => {
                $targetSearchInput.val('');
                $box.remove();
              })
          )
      );

      const $searchResultBody = $('<div>').css({
        maxHeight: `calc(100vh - ${
          $targetSearchInput.offset().top - $(window).scrollTop() + 180
        }px)`,
        overflowY: 'auto',
      });
      $box.append($searchResultBody);

      if (results.length === 0) {
        $searchResultBody.append(
          $('<p>').text(`No results found for query "${searchQuery}"`)
        );
      } else {
        results.forEach((r) => {
          const doc = resultDetails.get(r.ref);
          const href =
            $searchInput.data('offline-search-base-href') +
            r.ref.replace(/^\//, '');

          const $entry = $('<div>').addClass('mt-4');

          $entry.append(
            $('<small>').addClass('d-block text-body-secondary').text(r.ref)
          );

          $entry.append(
            $('<a>')
              .addClass('d-block')
              .css({
                fontSize: '1.2rem',
              })
              .attr('href', href)
              .text(doc.title)
          );

          $entry.append($('<p>').text(doc.excerpt));

          $searchResultBody.append($entry);
        });
      }

      $targetSearchInput.after($box);
    };
  });
})(jQuery);

;
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

;
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

;
/* WAI-ARIA tabs. Without this file every pane stays visible (stacked) and
   the tablist is in-page links. With it: one pane, arrow keys, and a shared
   localStorage key so picking CLI on one set switches every set in the group. */
(function () {
  var STORAGE_KEY = "blowhorn-tab-surface";

  function panelsOf(root) {
    return Array.prototype.slice.call(root.querySelectorAll("[data-tab-panel]"));
  }

  function tabsOf(root) {
    return Array.prototype.slice.call(root.querySelectorAll("[data-tab]"));
  }

  function select(root, id, persist) {
    var tabs = tabsOf(root);
    var panels = panelsOf(root);
    var match = false;
    panels.forEach(function (panel) {
      if (panel.getAttribute("data-tab-panel") === id) match = true;
    });
    if (!match) id = panels.length ? panels[0].getAttribute("data-tab-panel") : id;
    tabs.forEach(function (tab) {
      var on = tab.getAttribute("data-tab") === id;
      tab.classList.toggle("is-on", on);
      tab.setAttribute("aria-selected", on ? "true" : "false");
      tab.setAttribute("tabindex", on ? "0" : "-1");
    });
    panels.forEach(function (panel) {
      var on = panel.getAttribute("data-tab-panel") === id;
      panel.hidden = !on;
    });
    if (persist) {
      var group = root.getAttribute("data-tabs-group");
      if (group) {
        try {
          window.localStorage.setItem(STORAGE_KEY + ":" + group, id);
        } catch (err) {}
        document.querySelectorAll('[data-tabs-group="' + group + '"]').forEach(function (other) {
          if (other !== root) select(other, id, false);
        });
      }
    }
  }

  /* The tab layouts/_partials/tabs.html marked is-on: the first available
     surface, or the template's fallback when every surface is a placeholder. */
  function markedTab(tabs) {
    for (var i = 0; i < tabs.length; i++) {
      if (tabs[i].classList.contains("is-on")) return tabs[i].getAttribute("data-tab");
    }
    return tabs.length ? tabs[0].getAttribute("data-tab") : "";
  }

  function saved(group) {
    if (!group) return "";
    try {
      return window.localStorage.getItem(STORAGE_KEY + ":" + group) || "";
    } catch (err) {
      return "";
    }
  }

  function enhance(root) {
    var tabs = tabsOf(root);
    var panels = panelsOf(root);
    if (!tabs.length || !panels.length) return;
    root.classList.add("is-enhanced");
    var list = root.querySelector(".tabs-list");
    if (list) list.setAttribute("role", "tablist");
    tabs.forEach(function (tab, index) {
      var id = tab.getAttribute("data-tab");
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-controls", root.getAttribute("data-tabs-id") + "-" + id);
      tab.addEventListener("click", function (ev) {
        ev.preventDefault();
        select(root, id, true);
      });
      tab.addEventListener("keydown", function (ev) {
        var next = index;
        if (ev.key === "ArrowRight" || ev.key === "ArrowDown") next = (index + 1) % tabs.length;
        else if (ev.key === "ArrowLeft" || ev.key === "ArrowUp") next = (index - 1 + tabs.length) % tabs.length;
        else if (ev.key === "Home") next = 0;
        else if (ev.key === "End") next = tabs.length - 1;
        else return;
        ev.preventDefault();
        tabs[next].focus();
        select(root, tabs[next].getAttribute("data-tab"), true);
      });
    });
    panels.forEach(function (panel) {
      panel.setAttribute("role", "tabpanel");
      var id = panel.getAttribute("data-tab-panel");
      var tab = root.querySelector('[data-tab="' + id + '"]');
      if (tab && tab.id) panel.setAttribute("aria-labelledby", tab.id);
    });
    var group = root.getAttribute("data-tabs-group");
    var initial = saved(group);
    var hash = (window.location.hash || "").replace(/^#/, "");
    var prefix = root.getAttribute("data-tabs-id") || "";
    if (hash && prefix && hash.indexOf(prefix + "-") === 0) {
      initial = hash.slice(prefix.length + 1);
    }
    select(root, initial || markedTab(tabs), false);
  }

  document.querySelectorAll("[data-tabs]").forEach(enhance);
})();

;
/* Docs all-actions table (layouts/_partials/action-table.html). Without
   this file the table is plain and every row shows. With it: the filter bar
   appears (action type and platform dropdowns, both built from data), and
   the Action and Platform headers become buttons that sort ascending, then
   descending (aria-sort tells which). */
(function () {
  document.querySelectorAll("[data-action-table]").forEach(function (root) {
    var form = root.querySelector("[data-action-table-filters]");
    var tbody = root.querySelector("tbody");
    var count = root.querySelector("[data-action-table-count]");
    var empty = root.querySelector("[data-action-table-empty]");
    if (!form || !tbody) return;
    var rows = Array.prototype.slice.call(tbody.rows);
    var action = form.querySelector('[data-filter="action"]');
    var platform = form.querySelector('[data-filter="platform"]');
    var total = rows.length;
    form.hidden = false;
    root.classList.add("is-enhanced");

    function filter() {
      var a = action.value;
      var p = platform.value;
      var shown = 0;
      rows.forEach(function (row) {
        var hit = (!p || row.getAttribute("data-platform") === p) &&
          (!a || row.getAttribute("data-action") === a);
        row.hidden = !hit;
        if (hit) shown += 1;
      });
      if (count) count.textContent = "Showing " + shown + " of " + total;
      if (empty) empty.hidden = shown !== 0;
    }

    var heads = Array.prototype.slice.call(root.querySelectorAll("thead th[data-sort]"));
    function sortBy(key, dir) {
      var sorted = rows.slice().sort(function (a, b) {
        var x = a.getAttribute("data-k-" + key);
        var y = b.getAttribute("data-k-" + key);
        var c = x.localeCompare(y);
        if (c === 0) c = Number(a.getAttribute("data-order")) - Number(b.getAttribute("data-order"));
        else if (dir === "descending") c = -c;
        return c;
      });
      sorted.forEach(function (row) { tbody.appendChild(row); });
      heads.forEach(function (th) {
        if (th.getAttribute("data-sort") === key) th.setAttribute("aria-sort", dir);
        else th.removeAttribute("aria-sort");
      });
    }
    heads.forEach(function (th) {
      var key = th.getAttribute("data-sort");
      var button = document.createElement("button");
      button.type = "button";
      button.className = "action-table-sort";
      button.textContent = th.textContent;
      th.textContent = "";
      th.appendChild(button);
      button.addEventListener("click", function () {
        var next = th.getAttribute("aria-sort") === "ascending" ? "descending" : "ascending";
        sortBy(key, next);
      });
    });

    action.addEventListener("change", filter);
    platform.addEventListener("change", filter);
    filter();
  });
})();

;
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
