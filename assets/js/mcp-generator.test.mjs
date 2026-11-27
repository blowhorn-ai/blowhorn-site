import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';

const source = readFileSync(new URL('./mcp-generator.js', import.meta.url), 'utf8');

function createMockElement(tag, attrs = {}) {
  const listeners = {};
  const children = [];
  const classes = new Set();
  const el = {
    tagName: tag.toUpperCase(),
    attributes: { ...attrs },
    hidden: false,
    checked: attrs.checked === true,
    value: attrs.value || '',
    closest: (selector) => {
      if (selector === '.mcp-mode-label' && el.parentLabel) return el.parentLabel;
      return null;
    },
    getAttribute: (name) => el.attributes[name] ?? (name === 'data-mcp-client' ? attrs['data-mcp-client'] : null),
    setAttribute: (name, val) => { el.attributes[name] = String(val); },
    hasAttribute: (name) => name in el.attributes,
    classList: {
      add: (c) => classes.add(c),
      remove: (c) => classes.delete(c),
      toggle: (c, force) => {
        if (force === undefined) {
          if (classes.has(c)) classes.delete(c); else classes.add(c);
        } else if (force) {
          classes.add(c);
        } else {
          classes.delete(c);
        }
      },
      contains: (c) => classes.has(c)
    },
    addEventListener: (ev, fn) => {
      listeners[ev] = listeners[ev] || [];
      listeners[ev].push(fn);
    },
    dispatchEvent: (ev) => {
      (listeners[ev.type] || []).forEach(fn => fn(ev));
    },
    focus: () => { el.focused = true; },
    querySelectorAll: (selector) => {
      if (selector === 'input[name="mcp-mode"]') return el.radios || [];
      if (selector === '[data-mcp-client]') return el.tabs || [];
      if (selector === '[data-panel-client]') return el.panels || [];
      if (selector === '[data-pane-mode]') return el.panes || [];
      return [];
    }
  };
  return el;
}

test('mcp-generator initializes default state and responds to client and mode selection', () => {
  const root = createMockElement('div', { 'data-mcp-generator': '' });
  
  const radioHosted = createMockElement('input', { name: 'mcp-mode', value: 'hosted', checked: true });
  const radioLocal = createMockElement('input', { name: 'mcp-mode', value: 'local', checked: false });
  radioHosted.parentLabel = createMockElement('label');
  radioLocal.parentLabel = createMockElement('label');
  root.radios = [radioHosted, radioLocal];

  const tabClaude = createMockElement('button', { 'data-mcp-client': 'claude-code' });
  const tabCursor = createMockElement('button', { 'data-mcp-client': 'cursor' });
  root.tabs = [tabClaude, tabCursor];

  const paneClaudeHosted = createMockElement('div', { 'data-pane-mode': 'hosted' });
  const paneClaudeLocal = createMockElement('div', { 'data-pane-mode': 'local' });
  const panelClaude = createMockElement('div', { 'data-panel-client': 'claude-code' });
  panelClaude.panes = [paneClaudeHosted, paneClaudeLocal];

  const paneCursorHosted = createMockElement('div', { 'data-pane-mode': 'hosted' });
  const paneCursorLocal = createMockElement('div', { 'data-pane-mode': 'local' });
  const panelCursor = createMockElement('div', { 'data-panel-client': 'cursor' });
  panelCursor.panes = [paneCursorHosted, paneCursorLocal];

  root.panels = [panelClaude, panelCursor];

  const storage = {};
  const mockLocalStorage = {
    getItem: (key) => storage[key] || null,
    setItem: (key, val) => { storage[key] = String(val); }
  };

  vm.runInNewContext(source, {
    document: {
      readyState: 'complete',
      querySelectorAll: (sel) => (sel === '[data-mcp-generator]' ? [root] : [])
    },
    window: {
      localStorage: mockLocalStorage
    }
  });

  assert.equal(root.classList.contains('is-enhanced'), true);
  assert.equal(tabClaude.getAttribute('aria-selected'), 'true');
  assert.equal(tabCursor.getAttribute('aria-selected'), 'false');
  assert.equal(panelClaude.hidden, false);
  assert.equal(panelCursor.hidden, true);
  assert.equal(paneClaudeHosted.hidden, false);
  assert.equal(paneClaudeLocal.hidden, true);

  // Switch to cursor tab
  tabCursor.dispatchEvent({ type: 'click', preventDefault: () => {} });
  assert.equal(tabClaude.getAttribute('aria-selected'), 'false');
  assert.equal(tabCursor.getAttribute('aria-selected'), 'true');
  assert.equal(panelClaude.hidden, true);
  assert.equal(panelCursor.hidden, false);
  assert.equal(paneCursorHosted.hidden, false);
  assert.equal(paneCursorLocal.hidden, true);
  assert.equal(storage['blowhorn-mcp-client'], 'cursor');

  // Switch to local mode
  radioLocal.checked = true;
  radioHosted.checked = false;
  radioLocal.dispatchEvent({ type: 'change' });
  assert.equal(paneCursorHosted.hidden, true);
  assert.equal(paneCursorLocal.hidden, false);
  assert.equal(storage['blowhorn-mcp-mode'], 'local');

  // Test keyboard navigation (ArrowRight from cursor wraps to claude)
  tabCursor.dispatchEvent({ type: 'keydown', key: 'ArrowRight', preventDefault: () => {} });
  assert.equal(tabClaude.getAttribute('aria-selected'), 'true');
  assert.equal(tabCursor.getAttribute('aria-selected'), 'false');
  assert.equal(panelClaude.hidden, false);
});

test('mcp-generator handles missing elements safely', () => {
  vm.runInNewContext(source, {
    document: {
      readyState: 'complete',
      querySelectorAll: () => []
    },
    window: {
      localStorage: { getItem: () => null, setItem: () => {} }
    }
  });
});
