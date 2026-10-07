import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createVideoHandler } from '../video-handler.mjs';
import { localAssets } from '../local-assets.mjs';

const root = fileURLToPath(new URL('../site', import.meta.url));
const manifest = JSON.parse(await readFile(new URL('../video-manifest.json', import.meta.url)));
const handler = createVideoHandler(manifest);
const env = { ASSETS: localAssets(root) };
const [path, video] = Object.entries(manifest)[0];
const req = (route = path, options = {}) => new Request('https://example.com' + route, options);

test('All Tests preserves the complete catalog and adds nine continuously feeding string tests', () => {
  assert.equal(Object.keys(manifest).length, 86);
  assert.ok(manifest['/videos/MIT-2.009-2025-Finals-1p0s.mp4']);
  assert.ok(manifest['/videos/MIT-2.009-Yellow-Slot-A-Quick-8s-Portrait-15.mp4']);
  assert.ok(manifest['/videos/MIT-2.009-Yellow-Slot-B-Slow-11s-Portrait-15.mp4']);
  assert.ok(manifest['/videos/MIT-2.009-Lecture-1-63-Photos-Final.mp4'], 'Recovered originals keep their original filenames');
});
for (const [route, entry] of Object.entries(manifest)) {
  test('full original bytes: ' + entry.filename, async () => {
    const response = await handler.fetch(req(route), env);
    assert.equal(response.status, 200);
    assert.equal(response.headers.get('Content-Length'), String(entry.size));
    let size = 0;
    const hash = createHash('sha256');
    for await (const chunk of response.body) { hash.update(chunk); size += chunk.byteLength; }
    assert.equal(size, entry.size);
    assert.equal(hash.digest('hex'), entry.sha256);
  });
}
for (const honorRanges of [true, false]) {
  test(`seeking including part boundaries; asset Range support=${honorRanges}`, async () => {
    const all = Buffer.concat(await Promise.all(video.parts.map(p => readFile(root+p.path))));
    const ranges = [[0, 1023], [16777000, 16777400], [video.size-500, video.size-1], [16777216, 16777216]];
    for (const [start, end] of ranges) {
      const response = await handler.fetch(req(path, { headers: { Range: `bytes=${start}-${end}` } }), { ASSETS: localAssets(root, honorRanges) });
      assert.equal(response.status, 206);
      assert.equal(response.headers.get('Content-Range'), `bytes ${start}-${end}/${video.size}`);
      assert.deepEqual(Buffer.from(await response.arrayBuffer()), all.subarray(start,end+1));
    }
    for (const range of ['bytes=-200', `bytes=${video.size-200}-`, `bytes=${video.size-200}-${video.size+900}`]) {
      const response = await handler.fetch(req(path, { headers: { Range: range } }), { ASSETS: localAssets(root, honorRanges) });
      assert.equal(response.status, 206);
      assert.deepEqual(Buffer.from(await response.arrayBuffer()), all.subarray(-200));
    }
  });
}
test('HEAD and named downloads', async () => {
  const response = await handler.fetch(req(path+'?download=1', { method: 'HEAD' }), env);
  assert.equal(response.body, null);
  assert.equal(response.headers.get('Content-Length'), String(video.size));
  assert.equal(response.headers.get('Content-Disposition'), `attachment; filename="${video.filename}"`);
});
test('invalid ranges, unknown files, and methods', async () => {
  for (const Range of ['bytes=-0', 'bytes=999999999-', 'bytes=6-2', 'bytes=-', 'bytes=0-1,4-8', 'junk']) {
    const response = await handler.fetch(req(path, { headers: { Range } }), env);
    assert.equal(response.status, 416);
    assert.equal(response.headers.get('Content-Range'), `bytes */${video.size}`);
  }
  assert.equal((await handler.fetch(req('/videos/unknown.mp4'), env)).status, 404);
  assert.equal((await handler.fetch(req(path, { method: 'POST' }), env)).status, 405);
});
test('conditional requests and static pages', async () => {
  const cached = await handler.fetch(req(path, { headers: { 'If-None-Match': `"${video.sha256}"` } }), env);
  assert.equal(cached.status, 304);
  const mismatch = await handler.fetch(req(path, { headers: { Range: 'bytes=1-9', 'If-Range': '"old"' } }), env);
  assert.equal(mismatch.status, 200);
  await mismatch.body.cancel();
  const index = await handler.fetch(req('/tests/'), env);
  const html = await index.text();
  assert.equal((html.match(/<article/g) || []).length, 86);
  assert.ok(html.includes('2025 Finals'));
  assert.ok(html.includes('86 videos.'));
  assert.ok(html.includes('<h1>All Tests</h1>'));
  assert.ok(html.includes('href="/"'));
  assert.ok(html.includes('With sound'));
  assert.ok(!html.includes('No audio'));
  assert.deepEqual([...html.matchAll(/id="video-(\d+)"/g)].map(m => Number(m[1])), Array.from({ length: 86 }, (_, i) => 86 - i));
  assert.ok(!html.includes('Lecture 1'));
});

test('the already-shared root URL contains only the ten Selects, using the original files', async () => {
  const response = await handler.fetch(req('/'), env);
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.ok(html.includes('<h1>Selects</h1>'));
  assert.ok(html.includes('10 selected videos. Watch, download, and post.'));
  assert.deepEqual([...html.matchAll(/id="video-(\d+)"/g)].map(m => Number(m[1])), [41,40,39,38,25,20,9,6,3,1]);
  assert.ok(!html.includes('href="/tests'), 'Share page should not lead recipients to experiments');
  const legacy = await handler.fetch(req('/selects/'), env);
  assert.equal(legacy.status, 200);
  assert.equal(await legacy.text(), html, 'The earlier Selects link must show the same ten picks');
  const catalog = JSON.parse(await readFile(new URL('../assets/CATALOG.json', import.meta.url)));
  const chosen = catalog.filter(r => [1,3,6,9,20,25,38,39,40,41].includes(r.number));
  const sources = [...html.matchAll(/<source src="([^"]+)"/g)].map(m => m[1]);
  assert.equal(sources.length, 10);
  for (const r of chosen) {
    const route = '/' + r.file;
    assert.ok(sources.includes(route));
    assert.ok(manifest[route]);
    assert.ok(html.includes(`href="${route}?download=1"`));
    assert.ok(html.includes(`poster="/${r.thumbnail}"`));
  }
});

test('All Tests directory redirects and serves HEAD requests in local preview', async () => {
  const redirect = await handler.fetch(req('/tests'), env);
  assert.equal(redirect.status, 301);
  assert.equal(redirect.headers.get('Location'), 'https://example.com/tests/');
  const head = await handler.fetch(req('/tests/', { method: 'HEAD' }), env);
  assert.equal(head.status, 200);
  assert.equal(head.body, null);
  assert.equal(head.headers.get('Content-Type'), 'text/html');
});

test('all four disco auditions offer their original MP3 and WAV files', async () => {
  const html = await (await handler.fetch(req('/tests/'), env)).text();
  const catalog = JSON.parse(await readFile(new URL('../assets/CATALOG.json', import.meta.url)));
  const auditions = catalog.filter(r => r.number >= 34 && r.number <= 37);
  assert.equal(auditions.length, 4);
  for (const r of auditions) {
    for (const [field, type] of [['audio_mp3','audio/mpeg'],['audio_wav','audio/wav']]) {
      const route = '/' + r[field];
      assert.ok(html.includes(`href="${route}" download`));
      const response = await handler.fetch(req(route), env);
      assert.equal(response.status, 200);
      assert.equal(response.headers.get('Content-Type'), type);
      const original = await readFile(new URL('../assets' + route, import.meta.url));
      assert.deepEqual(Buffer.from(await response.arrayBuffer()), original);
    }
  }
});

test('the four blue digital Selects use the same chosen Disco D soundtrack', async () => {
  const catalog = JSON.parse(await readFile(new URL('../assets/CATALOG.json', import.meta.url)));
  const selected = catalog.filter(r => [38,39,40,41].includes(r.number));
  assert.equal(selected.length, 4);
  for (const entry of selected) {
    assert.equal(entry.audio, 'Disco D — Space Disco, 120 BPM');
    assert.match(entry.audio_sha256, /^[a-f0-9]{64}$/);
    assert.equal(entry.seconds, 18);
  }
  assert.equal(new Set(selected.map(r => r.audio_sha256)).size, 1);
  assert.equal(new Set(selected.map(r => r.audio_mp3)).size, 1);
});


test('revised independent reels bypass cached previews and downloads while keeping their MP4 paths', async () => {
  const catalog = JSON.parse(await readFile(new URL('../assets/CATALOG.json', import.meta.url)));
  const html = await (await handler.fetch(req('/tests/'), env)).text();
  const revisions = catalog.filter(r => [45,46,47].includes(r.number));
  assert.equal(revisions.length, 3);
  for (const r of revisions) {
    assert.equal(r.revision, 2);
    const version = r.sha256.slice(0,12);
    assert.ok(html.includes(`src="/${r.file}?v=${version}"`));
    assert.ok(html.includes(`href="/${r.file}?download=1&amp;v=${version}"`));
    assert.ok(html.includes(`poster="/${r.thumbnail}?v=${version}"`));
    const response = await handler.fetch(req('/'+r.file+'?download=1&v='+version, {method:'HEAD'}), env);
    assert.equal(response.status, 200);
    assert.equal(response.headers.get('ETag'), `"${r.sha256}"`);
    assert.ok(response.headers.get('Content-Disposition').startsWith('attachment;'));
  }
});
