import test from 'node:test';
import assert from 'node:assert/strict';
import { createReadStream } from 'node:fs';
import { readFile, readdir, stat } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const site = new URL('../vercel-site/', import.meta.url);
const previous = new URL('../site/', import.meta.url);
const catalog = JSON.parse(await readFile(new URL('../assets/CATALOG.json', import.meta.url)));

test('Vercel preserves the catalog, selections, posters, controls, and page presentation', async () => {
  for (const name of ['index.html', 'tests/index.html', 'selects/index.html', 'style.css', 'app.js', 'robots.txt']) {
    const current = (await readFile(new URL(name, site), 'utf8')).replace('<a href="/generator/">Headshot generator <span aria-hidden="true">↗</span></a>', '');
    assert.equal(current, await readFile(new URL(name, previous), 'utf8'), name);
  }
});

test('every Vercel preview, original download, and audio link resolves to a static file', async () => {
  for (const name of ['index.html', 'tests/index.html', 'selects/index.html']) {
    const html = await readFile(new URL(name, site), 'utf8');
    for (const [, value] of html.matchAll(/(?:src|href|poster)="(\/[^"\s]*)"/g)) {
      const url = new URL(value.replaceAll('&amp;', '&'), 'https://video.example');
      let target = new URL('.' + decodeURIComponent(url.pathname), site);
      if ((await stat(target)).isDirectory()) target = new URL('index.html', target.href.endsWith('/') ? target : target.href + '/');
      assert.ok((await stat(target)).isFile(), `${name}: ${value}`);
    }
  }
});

test('all forty-six static MP4s match the source bytes, including Finals invitation tests 57–59', async () => {
  assert.equal(catalog.length, 46);
  assert.deepEqual(catalog.filter(r => r.number >= 48).map(r => r.number), [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]);
  for (const record of catalog) {
    const video = new URL(record.file, site);
    const hash = createHash('sha256');
    for await (const chunk of createReadStream(video)) hash.update(chunk);
    assert.equal(hash.digest('hex'), record.sha256, record.title);
  }
});

test('Vercel publishes only static pages and approved media', async () => {
  assert.deepEqual((await readdir(site)).sort(), [
    'app.js', 'audio', 'generator', 'index.html', 'previews', 'robots.txt', 'selects', 'style.css', 'tests', 'videos'
  ]);
  const videoFiles = await readdir(new URL('videos/', site));
  assert.equal(videoFiles.length, catalog.length);
  assert.ok(videoFiles.every(name => name.endsWith('.mp4')));
});
