// Style exploration "Live run" (layouts/_partials/home/live-run.html).
// Plays the hero's scripted Blowhorn run once, when the desk scrolls into
// view: each mono status line types in and ticks off, the platform list
// checks off while drafting, the approval window slides in and its Approve
// button presses, then the summary line types. Motion's animate and inView
// only (bundled by js.Build, like home-reveal.js). The markup is the final
// state; the hidden start is set here, never in CSS, so with scripts off or
// prefers-reduced-motion the finished run shows and nothing moves. Text
// stays in the DOM while it types (a transparent copy holds the line's
// size and is what assistive tech reads), so nothing shifts or goes silent.
import { animate, inView } from 'motion';

const desk = document.querySelector('[data-live-run]');
const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (desk && !reduce && 'IntersectionObserver' in window) {
  const steps = [...desk.querySelectorAll('[data-lr-step]')];
  const plats = [...desk.querySelectorAll('[data-lr-plat]')];
  const summary = desk.querySelector('[data-lr-summary]');
  const mini = desk.querySelector('[data-lr-mini]');
  const approve = desk.querySelector('[data-lr-approve]');
  const ease = [0.2, 0.7, 0.2, 1];
  const wait = (s) => new Promise((resolve) => { window.setTimeout(resolve, s * 1000); });

  // A line types over a transparent copy of itself, so its box never changes.
  function prepare(line) {
    const full = line.textContent;
    const ghost = document.createElement('span');
    ghost.className = 'lr-ghost';
    ghost.textContent = full;
    const typed = document.createElement('span');
    typed.className = 'lr-typed';
    typed.setAttribute('aria-hidden', 'true');
    line.replaceChildren(ghost, typed);
    return { line, full, typed };
  }

  function settle(job) {
    job.line.replaceChildren(document.createTextNode(job.full));
  }

  function type(job, speed) {
    const n = job.full.length;
    return animate(0, n, {
      duration: Math.min(1.1, n * speed),
      ease: 'linear',
      onUpdate: (v) => { job.typed.textContent = job.full.slice(0, Math.round(v)); },
    }).then(() => settle(job));
  }

  function show(el, from) {
    return animate(el, { opacity: 1, transform: 'translateY(0px)' }, { duration: 0.45, ease }).then(() => {
      el.style.removeProperty('opacity');
      el.style.removeProperty('transform');
    }, () => {});
  }

  // Hidden start: written inline by the script only.
  const lines = steps.map((li) => prepare(li.querySelector('[data-lr-text]')));
  const sum = summary ? prepare(summary) : null;
  steps.forEach((li) => { li.dataset.state = 'wait'; li.style.opacity = '0'; li.style.transform = 'translateY(6px)'; });
  plats.forEach((li) => { li.dataset.state = 'wait'; });
  if (summary) summary.style.opacity = '0';
  if (mini) {
    mini.classList.remove('is-approved');
    mini.style.opacity = '0';
    mini.style.transform = 'translateY(16px)';
  }

  async function play() {
    await wait(0.35);
    for (let i = 0; i < steps.length; i += 1) {
      const li = steps[i];
      li.dataset.state = 'run';
      show(li);
      await type(lines[i], 0.03);
      if (i === 1) {
        for (const p of plats) {
          await wait(0.16);
          p.dataset.state = 'done';
        }
      } else {
        await wait(0.55);
      }
      if (li.hasAttribute('data-lr-hold') && mini) {
        li.dataset.state = 'hold';
        await show(mini);
        await wait(1.1);
        if (approve) approve.classList.add('is-pressed');
        await wait(0.25);
        if (approve) approve.classList.remove('is-pressed');
        mini.classList.add('is-approved');
        await wait(0.35);
      }
      li.dataset.state = 'done';
    }
    if (summary && sum) {
      summary.style.opacity = '1';
      await type(sum, 0.018);
    }
    steps.forEach((li) => { delete li.dataset.state; });
    plats.forEach((li) => { delete li.dataset.state; });
  }

  // Once: the run plays the first time the desk shows, never again.
  let played = false;
  const stop = inView(desk, () => {
    if (played) return;
    played = true;
    if (stop) stop();
    play();
  }, { amount: 0.3 });
}
