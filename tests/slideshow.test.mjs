import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import vm from 'node:vm';

test('lecture slideshow publishes the complete ordered photo set and offline package in both builds', async () => {
  const catalog = JSON.parse(await readFile(new URL('../assets/CATALOG.json', import.meta.url)));
  const record = catalog.find(r => r.number === 93);
  const provenance = JSON.parse(await readFile(new URL('../assets/production-notes/lecture-slideshow-2026-10-13/sequence.json', import.meta.url)));
  assert.equal(record.media_type, 'slideshow');
  assert.equal(record.photo_count, 58);
  assert.equal(record.seconds, 58 * 1.75);
  assert.equal(record.dissolve_seconds, 0.1);
  for (const build of ['site', 'vercel-site']) {
    const root = new URL('../' + build + '/', import.meta.url);
    const directory = new URL(record.source_directory + '/', root);
    const state = { window: {} };
    vm.runInNewContext(await readFile(new URL('photos.js', directory), 'utf8'), state);
    const photos = Array.from(state.window.SLIDESHOW_PHOTOS);
    assert.deepEqual(photos, provenance.photos.map(p => p.filename));
    assert.deepEqual(photos, photos.toSorted());
    assert.equal(new Set(photos).size, 58);
    assert.equal((await readdir(new URL('photos/', directory))).length, 58);
    for (const photo of provenance.photos) {
      const hash = createHash('sha256').update(await readFile(new URL('photos/' + photo.filename, directory))).digest('hex');
      assert.equal(hash, photo.sha256);
    }
    if (build === 'vercel-site') {
      const offline = await readFile(new URL(record.source_directory + '.zip', root));
      assert.equal(offline.subarray(0, 2).toString(), 'PK');
    }
    const allTests = await readFile(new URL('tests/index.html', root), 'utf8');
    assert.match(allTests, /href="\/slideshows\/2026-10-13\/"/);
    assert.match(allTests, /1 browser slideshow/);
    assert.ok(allTests.indexOf('id="video-93"') < allTests.indexOf('id="video-92"'));
    const selects = await readFile(new URL('index.html', root), 'utf8');
    assert.ok(!selects.includes('video-93'));
  }
});
