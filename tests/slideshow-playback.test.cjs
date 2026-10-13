// Deterministic tests of the actual playback script, with image loads and time
// under test control. This is not a substitute for a real full-screen browser test.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');

const script = readFileSync(join(__dirname, '../slideshows/2026-10-13/slideshow.js'), 'utf8');

function fixture({ count = 58, broken = [], deferred = [], fullscreenReject = false } = {}) {
  let now = 0, nextTimer = 0;
  const timers = new Map(), events = new Map(), imageRequests = [], waiting = new Map();
  function element(tagName = 'DIV') {
    const listeners = new Map(), classes = new Set(), attrs = new Map();
    return { tagName, dataset: {}, style: { setProperty() {} }, hidden: true,
      classList: { add: (...ns) => ns.forEach(n => classes.add(n)),
        remove: (...ns) => ns.forEach(n => classes.delete(n)), contains: n => classes.has(n),
        toggle(n, yes) { if (yes) classes.add(n); else classes.delete(n); } },
      setAttribute: (n, v) => attrs.set(n, v), getAttribute: n => attrs.get(n),
      addEventListener: (name, fn) => { if (!listeners.has(name)) listeners.set(name, []); listeners.get(name).push(fn); },
      dispatch(name, evt = {}) { for (const fn of listeners.get(name) || []) fn(evt); },
      contains: () => false, blur() { document.activeElement = body; }, offsetWidth: 1280 };
  }
  const body = element('BODY'), root = element('HTML'), slideshow = element('MAIN');
  const controls = element(), play = element('BUTTON'), next = element('BUTTON');
  const previous = element('BUTTON'), full = element('BUTTON'), status = element('P');
  const layers = [element('IMG'), element('IMG')];
  const selectors = { '#slideshow': slideshow, '#controls': controls, '#play': play,
    '#next': next, '#previous': previous, '#fullscreen': full, '#status': status };
  const document = { body, documentElement: root, hidden: false, activeElement: body,
    querySelector: s => selectors[s], querySelectorAll: s => s === '.slide' ? layers : [],
    addEventListener: (n, fn) => { if (!events.has(n)) events.set(n, []); events.get(n).push(fn); } };
  controls.contains = el => [play, next, previous, full].includes(el);
  function emit(n, evt) { for (const fn of events.get(n) || []) fn(evt); }
  root.requestFullscreen = async () => {
    if (fullscreenReject) throw Error('denied');
    document.fullscreenElement = root; emit('fullscreenchange');
  };
  document.exitFullscreen = async () => { document.fullscreenElement = null; emit('fullscreenchange'); };
  class Image {
    set src(value) {
      this.url = value;
      const index = Number(value.match(/(\d+)\.jpg/)[1]);
      imageRequests.push(index);
      const settle = () => broken.includes(index) ? this.onerror() : this.onload();
      if (deferred.includes(index)) waiting.set(index, settle); else queueMicrotask(settle);
    }
    get src() { return this.url; }
    async decode() {}
  }
  const setTimeout = (fn, delay) => { const id = ++nextTimer; timers.set(id, { at: now + delay, fn }); return id; };
  vm.runInNewContext(script, { window: { SLIDESHOW_PHOTOS: Array.from({ length: count }, (_, i) => `${i + 1}.jpg`) },
    document, Image, setTimeout, clearTimeout: id => timers.delete(id),
    performance: { now: () => now }, console: { warn() {} } });
  const flush = async () => { for (let i = 0; i < 20; i++) await Promise.resolve(); };
  async function advance(ms) {
    await flush();
    const end = now + ms;
    while (true) {
      const candidates = [...timers].filter(([, t]) => t.at <= end).sort((a, b) => a[1].at - b[1].at);
      if (!candidates.length) break;
      const [id, timer] = candidates[0]; timers.delete(id); now = timer.at;
      timer.fn(); await flush();
    }
    now = end; await flush();
  }
  async function click(el) { el.dispatch('click'); await flush(); }
  async function key(key, { code = key, target = body, ...mods } = {}) {
    emit('keydown', { key, code, target, preventDefault() {}, ...mods }); await flush();
  }
  return { body, root, document, controls, play, next, previous, full, status, layers,
    flush, advance, click, key, emit, imageRequests,
    photo: () => Number(slideshow.dataset.photo),
    release: async n => { waiting.get(n)?.(); await flush(); } };
}

test('initial autoplay, exact 1.75-second intervals, complete 58-photo order and loop', async () => {
  const f = fixture(); await f.flush();
  assert.equal(f.photo(), 1);
  await f.advance(1749); assert.equal(f.photo(), 1);
  await f.advance(1); assert.equal(f.photo(), 2);
  for (let photo = 3; photo <= 58; photo++) { await f.advance(1750); assert.equal(f.photo(), photo); }
  await f.advance(1750); assert.equal(f.photo(), 1);
});

test('pause holds the image; resume preserves the remaining display time', async () => {
  const f = fixture(); await f.advance(1000); await f.click(f.play);
  await f.advance(10000); assert.equal(f.photo(), 1);
  assert.equal(f.play.getAttribute('aria-label'), 'Play slideshow');
  await f.click(f.play); await f.advance(749); assert.equal(f.photo(), 1);
  await f.advance(1); assert.equal(f.photo(), 2);
});

test('previous and next wrap at both ends and preserve paused state', async () => {
  const f = fixture(); await f.flush(); await f.click(f.play);
  await f.click(f.previous); assert.equal(f.photo(), 58);
  await f.click(f.next); assert.equal(f.photo(), 1);
  await f.click(f.next); assert.equal(f.photo(), 2);
  await f.advance(8000); assert.equal(f.photo(), 2);
});

test('manual navigation resets the timer while playing', async () => {
  const f = fixture(); await f.advance(1500); await f.click(f.next);
  await f.advance(1749); assert.equal(f.photo(), 2);
  await f.advance(1); assert.equal(f.photo(), 3);
});

test('rapid navigation keeps the most recent request and one active layer', async () => {
  const f = fixture(); await f.flush(); await f.click(f.play);
  for (let i = 0; i < 20; i++) f.next.dispatch('click');
  await f.flush(); assert.equal(f.photo(), 21);
  assert.equal(f.layers.filter(l => l.classList.contains('is-active')).length, 1);
});

test('controls begin hidden, show on pointer movement, and hide at three seconds', async () => {
  const f = fixture(); await f.flush();
  assert.equal(f.body.classList.contains('controls-visible'), false);
  f.emit('pointermove'); await f.advance(2999);
  assert.equal(f.body.classList.contains('controls-visible'), true);
  await f.advance(1); assert.equal(f.body.classList.contains('controls-visible'), false);
  await f.click(f.play); await f.advance(10000);
  assert.equal(f.body.classList.contains('controls-visible'), true);
});

test('pointer hover and keyboard focus keep controls available', async () => {
  const f = fixture(); await f.flush();
  f.controls.dispatch('pointerenter', { pointerType: 'mouse' }); await f.advance(5000);
  assert.equal(f.body.classList.contains('controls-visible'), true);
  f.controls.dispatch('pointerleave'); await f.advance(3000);
  assert.equal(f.body.classList.contains('controls-visible'), false);
  f.document.activeElement = f.play; f.controls.dispatch('focusin'); await f.advance(5000);
  assert.equal(f.body.classList.contains('controls-visible'), true);
});

test('Space and arrows work; browser shortcuts and held Space are ignored', async () => {
  const f = fixture(); await f.flush(); await f.key(' ', { code: 'Space' });
  assert.equal(f.body.classList.contains('paused'), true);
  await f.key('ArrowRight'); assert.equal(f.photo(), 2);
  await f.key('ArrowLeft'); assert.equal(f.photo(), 1);
  await f.key(' ', { code: 'Space', repeat: true });
  await f.key(' ', { code: 'Space', target: f.next });
  await f.key('f', { metaKey: true });
  assert.equal(f.body.classList.contains('paused'), true);
  assert.equal(f.document.fullscreenElement, undefined);
});

test('fullscreen handler enters and exits, updates labels, and handles rejection', async () => {
  const f = fixture(); await f.flush(); await f.click(f.full);
  assert.equal(f.document.fullscreenElement, f.root);
  assert.equal(f.full.getAttribute('aria-label'), 'Exit full screen');
  await f.key('f'); assert.equal(f.document.fullscreenElement, null);
  const rejected = fixture({ fullscreenReject: true }); await rejected.flush();
  await rejected.click(rejected.full);
  assert.equal(rejected.status.hidden, false);
  assert.match(rejected.status.textContent, /Full screen is unavailable/);
});

test('slow Wi-Fi keeps the current photograph until the next one is ready', async () => {
  const f = fixture({ deferred: [2] }); await f.advance(1750);
  assert.equal(f.photo(), 1);
  await f.advance(5000); assert.equal(f.photo(), 1);
  await f.release(2); assert.equal(f.photo(), 2);
  await f.advance(1749); assert.equal(f.photo(), 2);
});

test('pause cancels a pending automatic advance', async () => {
  const f = fixture({ deferred: [2] }); await f.advance(1750);
  await f.click(f.play); await f.release(2); assert.equal(f.photo(), 1);
  await f.advance(5000); assert.equal(f.photo(), 1);
});

test('a missing photo is skipped and an entirely broken set reports an error', async () => {
  const f = fixture({ broken: [2] }); await f.advance(1750); assert.equal(f.photo(), 3);
  const b = fixture({ count: 2, broken: [1, 2] }); await b.flush();
  assert.equal(b.body.classList.contains('paused'), true);
  assert.equal(b.status.hidden, false);
});

test('preloads eight ahead and the previous image without downloading the entire set', async () => {
  const f = fixture(); await f.flush();
  assert.deepEqual([...new Set(f.imageRequests)].sort((a, b) => a - b), [1,2,3,4,5,6,7,8,9,58]);
});

test('hidden tabs suspend timing and resume without skipping a series of photographs', async () => {
  const f = fixture(); await f.advance(1000);
  f.document.hidden = true; f.emit('visibilitychange'); await f.advance(20000);
  assert.equal(f.photo(), 1);
  f.document.hidden = false; f.emit('visibilitychange'); await f.advance(750);
  assert.equal(f.photo(), 2);
});

test('empty and single-photo sets do not cause a loop or unhandled error', async () => {
  const empty = fixture({ count: 0 }); await empty.flush();
  assert.equal(empty.status.hidden, false);
  const single = fixture({ count: 1 }); await single.advance(10000);
  assert.equal(single.photo(), 1);
});
