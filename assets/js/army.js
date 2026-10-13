// Blowhorn's army (home #how): pick a recruit, Major Blowhorn yells at it and
// its panel shows what it does. Tabs follow the ARIA tabs pattern (arrows,
// Home, End). The rotation runs only while the section is in view, stops for
// good on first interaction and never runs under reduced motion. The bubble
// is announced only after the visitor has chosen something.
(function () {
  var root = document.querySelector('.army');
  if (!root) return;
  var tabs = Array.prototype.slice.call(root.querySelectorAll('.army-rank'));
  var yell = root.querySelector('.army-yell');
  var plats = root.querySelectorAll('.army-plats img');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cur = 0, timer = null, visible = false, touched = false;
  root.classList.add('is-ready');

  function select(i, focus) {
    var t = tabs[i];
    tabs.forEach(function (x, j) {
      var on = j === i;
      x.setAttribute('aria-selected', on);
      x.tabIndex = on ? 0 : -1;
      document.getElementById(x.getAttribute('aria-controls')).hidden = !on;
    });
    cur = i;
    yell.textContent = t.dataset.line;
    yell.classList.remove('is-shout');
    void yell.offsetWidth;
    yell.classList.add('is-shout');
    plats.forEach(function (im, k) {
      
      im.classList.remove('is-hit'); void im.offsetWidth; im.classList.add('is-hit');
    });
    if (focus) t.focus();
  }
  function stop() {
    touched = true;
    clearInterval(timer); timer = null;
    yell.setAttribute('aria-live', 'polite');
  }
  function run() {
    if (reduce || touched || timer || !visible) return;
    timer = setInterval(function () { select((cur + 1) % tabs.length); }, 6000);
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { stop(); select(i); });
    t.addEventListener('keydown', function (e) {
      var n = { ArrowRight: i + 1, ArrowDown: i + 1, ArrowLeft: i - 1, ArrowUp: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
      if (n === undefined) return;
      e.preventDefault(); stop();
      select((n + tabs.length) % tabs.length, true);
    });
  });
  root.addEventListener('focusin', function () { clearInterval(timer); timer = null; });
  root.addEventListener('pointerenter', function () { clearInterval(timer); timer = null; });
  root.addEventListener('pointerleave', run);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      visible = es[0].isIntersecting;
      if (visible) run(); else { clearInterval(timer); timer = null; }
    }, { threshold: 0.4 }).observe(root);
  }

  // Reserve Unit: enlist or discharge Macs (1 to 8). One Mac takes the job.
  var macs = root.querySelector('.army-macs');
  var note = root.querySelector('.army-fleet-note');
  var count = 3, job = 0;
  function drawMacs(added) {
    var claim = job % count, html = '';
    for (var m = 0; m < count; m++) {
      html += '<li class="army-mac' + (m === claim ? ' is-on' : '') + (added && m === count - 1 ? ' is-new' : '') + '">' +
        '<span class="army-mac-name">Mac ' + (m + 1) + '</span><span class="army-mac-tag">' + (m === claim ? 'on it' : 'standing by') + '</span></li>';
    }
    macs.innerHTML = html;
  }
  function say(line) { stop(); yell.textContent = line; }
  root.querySelector('[data-army="enlist"]').addEventListener('click', function () {
    if (count >= 8) { say("Eight Macs. That's a battalion, not a hobby. Carry on."); return; }
    count++; job++; drawMacs(true);
    say('Mac ' + count + ', welcome to the reserves. Mac ' + (job % count + 1) + ' takes this one. Everyone else, as you were.');
    note.textContent = count + ' Macs enlisted. One job, one Mac.';
  });
  root.querySelector('[data-army="discharge"]').addEventListener('click', function () {
    if (count <= 1) { say('One Mac is the minimum. I need someone to yell at.'); return; }
    count--; drawMacs();
    say('Mac ' + (count + 1) + ', honorably discharged. The queue carries on without you.');
    note.textContent = count + (count === 1 ? ' Mac' : ' Macs') + ' enlisted. One job, one Mac.';
  });
  drawMacs();
})();
