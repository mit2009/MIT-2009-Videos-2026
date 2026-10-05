import test from 'node:test';
import assert from 'node:assert/strict';
import { createReadStream } from 'node:fs';
import { readFile, readdir, stat } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const site = new URL('../vercel-site/', import.meta.url);
const previous = new URL('../site/', import.meta.url);
const catalog = JSON.parse(await readFile(new URL('../assets/CATALOG.json', import.meta.url)));

test('Vercel preserves the catalog, selections, posters, controls, and page presentation', async () => {
  for (const name of ['index.html', 'tests/index.html', 'selects/index.html', 'posters/index.html', 'style.css', 'app.js', 'robots.txt']) {
    const current = (await readFile(new URL(name, site), 'utf8')).replace('<a href="/generator/">Headshot generator <span aria-hidden="true">↗</span></a>', '');
    assert.equal(current, await readFile(new URL(name, previous), 'utf8'), name);
  }
});

test('every Vercel preview, original download, and audio link resolves to a static file', async () => {
  for (const name of ['index.html', 'tests/index.html', 'selects/index.html', 'posters/index.html']) {
    const html = await readFile(new URL(name, site), 'utf8');
    for (const [, value] of html.matchAll(/(?:src|href|poster)="(\/[^"\s]*)"/g)) {
      const url = new URL(value.replaceAll('&amp;', '&'), 'https://video.example');
      let target = new URL('.' + decodeURIComponent(url.pathname), site);
      if ((await stat(target)).isDirectory()) target = new URL('index.html', target.href.endsWith('/') ? target : target.href + '/');
      assert.ok((await stat(target)).isFile(), `${name}: ${value}`);
    }
  }
});

test('all sixty-one static MP4s match the source bytes, including the assembled lecture originals', async () => {
  assert.equal(catalog.length, 61);
  assert.deepEqual(catalog.filter(r => r.number >= 48).map(r => r.number), [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61]);
  for (const record of catalog) {
    const video = new URL(record.file, site);
    const hash = createHash('sha256');
    for await (const chunk of createReadStream(video)) hash.update(chunk);
    assert.equal(hash.digest('hex'), record.sha256, record.title);
  }
});

test('Vercel publishes only static pages and approved media', async () => {
  assert.deepEqual((await readdir(site)).sort(), [
    'app.js', 'audio', 'generator', 'index.html', 'posters', 'previews', 'robots.txt', 'selects', 'style.css', 'tests', 'videos'
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
