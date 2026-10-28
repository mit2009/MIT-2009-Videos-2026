import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import vm from 'node:vm';

for (const [number, seconds] of [[93, 1.75], [94, 3], [95, 5], [96, 3], [97, 5], [99, 3], [100, 5]]) {
test(`lecture slideshow ${number} publishes the complete ordered photo set and offline package in both builds`, async () => {
  const catalog = JSON.parse(await readFile(new URL('../assets/CATALOG.json', import.meta.url)));
  const record = catalog.find(r => r.number === number);
  const date = number >= 99 ? '2026-10-28' : number >= 96 ? '2026-10-26' : '2026-10-13';
  const count = number >= 99 ? 69 : number >= 96 ? 52 : 58;
  const provenance = JSON.parse(await readFile(new URL(`../assets/production-notes/lecture-slideshow-${date}/sequence.json`, import.meta.url)));
  assert.equal(record.media_type, 'slideshow');
  assert.equal(record.photo_count, count);
  assert.equal(record.seconds, count * seconds);
  assert.equal(record.seconds_per_slide, seconds);
  assert.equal(record.dissolve_seconds, 0.1);
  for (const build of ['site', 'vercel-site']) {
    const root = new URL('../' + build + '/', import.meta.url);
    const directory = new URL(record.source_directory + '/', root);
    const state = { window: {} };
    vm.runInNewContext(await readFile(new URL('photos.js', directory), 'utf8'), state);
    const photos = Array.from(state.window.SLIDESHOW_PHOTOS);
    assert.deepEqual(photos, provenance.photos.map(p => p.filename));
    assert.deepEqual(photos, photos.toSorted());
    assert.equal(new Set(photos).size, count);
    assert.equal((await readdir(new URL('photos/', directory))).length, count);
    const playback = await readFile(new URL('slideshow.js', directory), 'utf8');
    assert.ok(playback.includes(`const INTERVAL_MS = ${seconds * 1000};`));
    assert.ok(playback.includes('const FADE_MS = 100;'));
    for (const photo of provenance.photos) {
      const hash = createHash('sha256').update(await readFile(new URL('photos/' + photo.filename, directory))).digest('hex');
      assert.equal(hash, photo.sha256);
    }
    if (build === 'vercel-site') {
      const offline = await readFile(new URL(record.source_directory + '.zip', root));
      assert.equal(offline.subarray(0, 2).toString(), 'PK');
    }
    const allTests = await readFile(new URL('tests/index.html', root), 'utf8');
    assert.ok(allTests.includes(`href="/${record.source_directory}/"`));
    assert.match(allTests, /7 browser slideshows/);
    assert.ok(allTests.indexOf(`id="video-${number}"`) < allTests.indexOf('id="video-92"'));
    assert.ok(allTests.indexOf('id="video-95"') < allTests.indexOf('id="video-94"'));
    assert.ok(allTests.indexOf('id="video-94"') < allTests.indexOf('id="video-93"'));
    const selects = await readFile(new URL('index.html', root), 'utf8');
    assert.equal(selects.includes(`id="video-${number}"`), number >= 94 && number <= 97);
    if (number >= 94 && number <= 97) {
      assert.ok(selects.includes(`href="/${record.source_directory}/"`));
      assert.equal(selects.includes(`href="/${record.source_directory}.zip"`), build === 'vercel-site');
    }
  }
});
}
