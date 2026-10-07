import test from 'node:test';
import assert from 'node:assert/strict';
import { createReadStream } from 'node:fs';
import { readFile, readdir, stat } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const site = new URL('../vercel-site/', import.meta.url);
const previous = new URL('../site/', import.meta.url);
const catalog = JSON.parse(await readFile(new URL('../assets/CATALOG.json', import.meta.url)));

test('Vercel preserves the catalog, selections, posters, controls, and page presentation', async () => {
  for (const name of ['index.html', 'tests/index.html', 'selects/index.html', 'posters/index.html', 'feasibility/index.html', 'style.css', 'app.js', 'robots.txt']) {
    const current = (await readFile(new URL(name, site), 'utf8')).replace('<a href="/generator/">Headshot generator <span aria-hidden="true">↗</span></a>', '');
    assert.equal(current, await readFile(new URL(name, previous), 'utf8'), name);
  }
});

test('every Vercel preview, original download, and audio link resolves to a static file', async () => {
  for (const name of ['index.html', 'tests/index.html', 'selects/index.html', 'posters/index.html', 'feasibility/index.html']) {
    const html = await readFile(new URL(name, site), 'utf8');
    for (const [, value] of html.matchAll(/(?:src|href|poster)="(\/[^"\s]*)"/g)) {
      const url = new URL(value.replaceAll('&amp;', '&'), 'https://video.example');
      let target = new URL('.' + decodeURIComponent(url.pathname), site);
      if ((await stat(target)).isDirectory()) target = new URL('index.html', target.href.endsWith('/') ? target : target.href + '/');
      assert.ok((await stat(target)).isFile(), `${name}: ${value}`);
    }
  }
});

test('all eighty-nine static MP4s match the source bytes, including the assembled lecture originals', async () => {
  assert.equal(catalog.length, 89);
  assert.deepEqual(catalog.filter(r => r.number >= 48).map(r => r.number), [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]);
  for (const record of catalog) {
    const video = new URL(record.file, site);
    const hash = createHash('sha256');
    for await (const chunk of createReadStream(video)) hash.update(chunk);
    assert.equal(hash.digest('hex'), record.sha256, record.title);
  }
});

test('Vercel publishes only static pages and approved media', async () => {
  assert.deepEqual((await readdir(site)).sort(), [
    'app.js', 'audio', 'feasibility', 'generator', 'index.html', 'posters', 'previews', 'robots.txt', 'selects', 'style.css', 'tests', 'videos'
  ]);
  const videoFiles = await readdir(new URL('videos/', site));
  assert.equal(videoFiles.length, catalog.length);
  assert.ok(videoFiles.every(name => name.endsWith('.mp4')));
});


test('lecture loops retain all 36 posters, requested timing, color sequence, and seamless playback', async () => {
  const loops = catalog.filter(r => r.number >= 60 && r.number <= 61);
  const sequence = JSON.parse(await readFile(new URL('../assets/production-notes/poster-loops-2026-10-05/sequence.json', import.meta.url)));
  const order = ['Green', 'Purple', 'Red', 'Blue', 'Yellow', 'Pink'];
  assert.equal(loops.length, 2);
  assert.equal(new Set(sequence.posters.map(r => r.source_pdf + ':' + r.source_page)).size, 36);
  assert.deepEqual(sequence.posters.map(r => r.color), Array.from({ length: 36 }, (_, i) => order[i % 6]));
  const html = await readFile(new URL('tests/index.html', site), 'utf8');
  const lecture = await readFile(new URL('posters/index.html', site), 'utf8');
  assert.deepEqual([...lecture.matchAll(/id="video-(\d+)"/g)].map(m => Number(m[1])), [60, 61]);
  for (const record of loops) {
    assert.equal(record.poster_count, 36);
    assert.equal(record.seconds, 180);
    assert.equal(record.seconds_per_poster, 5);
    assert.equal(record.audio, 'Silent');
    assert.equal(record.fps, 60);
    assert.equal(record.loop, true);
    assert.deepEqual(record.color_cycle, order);
    assert.ok(record.source_parts.length > 1);
    const assembledHash = createHash('sha256');
    for (const part of record.source_parts) {
      const file = new URL('../assets/' + part, import.meta.url);
      assert.ok((await stat(file)).size <= 64 * 1024 * 1024);
      for await (const chunk of createReadStream(file)) assembledHash.update(chunk);
    }
    assert.equal(assembledHash.digest('hex'), record.sha256);
    assert.match(html, new RegExp('<video id="player-' + record.number + '"[^>]* loop>'));
  }
});

test('the feasibility share page loops the complete three-second slide sequence without changing Selects', async () => {
  const record = catalog.find(r => r.number === 62);
  const sequence = JSON.parse(await readFile(new URL('../assets/production-notes/feasibility-carousel-2026-10-05-r2/sequence.json', import.meta.url)));
  const verification = JSON.parse(await readFile(new URL('../assets/production-notes/feasibility-carousel-2026-10-05-r2/verification.json', import.meta.url)));
  assert.equal(record.slide_count, 229);
  assert.equal(record.seconds_per_slide, 3);
  assert.equal(record.seconds, 687);
  assert.equal(record.audio, 'Silent');
  assert.equal(record.loop, true);
  assert.deepEqual(sequence.team_counts, { Green: 40, Purple: 51, Red: 38, Blue: 31, Yellow: 32, Pink: 37 });
  assert.equal(new Set(sequence.slides.map(s => s.source_pdf + ':' + s.source_page)).size, 229);
  assert.deepEqual(sequence.slides.map(s => s.center_time_seconds), Array.from({ length: 229 }, (_, i) => i * 3));
  assert.equal(verification.sha256, record.sha256);
  assert.equal(verification.all_center_crossings_checked, 229);
  assert.equal(verification.full_decode_errors, 0);
  assert.equal(record.revision, 2);
  assert.equal(record.rotation_mode, 'once');
  assert.equal(record.motion_direction, 'right to left');
  assert.equal(verification.forward_page_order, true);
  assert.ok(verification.measured_horizontal_motion_px < 0);
  const colors = ['Green', 'Purple', 'Red', 'Blue', 'Yellow', 'Pink'];
  const expectedColors = [];
  for (let round = 0; round < 51; round++) {
    for (const color of colors) if (round < sequence.team_counts[color]) expectedColors.push(color);
  }
  assert.deepEqual(sequence.slides.map(s => s.color), expectedColors);
  for (const color of colors) {
    const pages = sequence.slides.filter(s => s.color === color).map(s => s.source_page);
    assert.deepEqual(pages, [...pages].sort((a, b) => a - b));
  }
  const config = JSON.parse(await readFile(new URL('../vercel.json', import.meta.url)));
  assert.ok(config.redirects.some(r => r.source === '/videos/MIT-2.009-Feasibility-Curved-Carousel-229-Slides-687s.mp4' && r.destination === '/' + record.file));
  const page = await readFile(new URL('feasibility/index.html', site), 'utf8');
  assert.deepEqual([...page.matchAll(/id="video-(\d+)"/g)].map(m => Number(m[1])), [62]);
  assert.match(page, /<video id="player-62"[^>]* loop>/);
  const selects = JSON.parse(await readFile(new URL('../assets/SELECTS.json', import.meta.url)));
  assert.deepEqual(selects, [1, 3, 6, 9, 20, 25, 38, 39, 40, 41]);
});
