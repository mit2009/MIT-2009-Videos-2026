import argparse, contextlib, hashlib, html, json, shutil, zipfile
from pathlib import Path

parser = argparse.ArgumentParser(description='Build the MIT 2.009 video library.')
parser.add_argument('--target', choices=['cloudflare', 'vercel'], default='cloudflare')
target = parser.parse_args().target
WORK = Path(__file__).resolve().parent
SOURCE = WORK / 'assets'
SITE = WORK / ('vercel-site' if target == 'vercel' else 'site')
OUT = WORK / 'dist'
PART_SIZE = 16 * 1024 * 1024
records = json.loads((SOURCE/'CATALOG.json').read_text())
selects = json.loads((SOURCE/'SELECTS.json').read_text())
assert isinstance(selects, list) and all(type(n) is int for n in selects), 'SELECTS.json must list catalog numbers'
assert len(selects) == len(set(selects)), 'Duplicate number in SELECTS.json'
assert set(selects) <= {r['number'] for r in records}, 'Unknown catalog number in SELECTS.json'
# site/ contains generated output only. Rebuild it so removed videos cannot
# remain in the next upload package.
if SITE.exists():
    shutil.rmtree(SITE)
videos, cards, verification = {}, {}, []
(SITE/('videos' if target == 'vercel' else 'media')).mkdir(parents=True, exist_ok=True)
(SITE/'previews').mkdir(exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
titles = {r['number']: r['title'] for r in records}
descriptions = {r['number']: r['description'] for r in records}
for r in records:
    number = r['number']
    filename = Path(r['file']).name
    # Long lecture originals are stored in ordered, lossless parts so each
    # Git blob stays below its size limit. The published MP4 is byte-identical.
    originals = [SOURCE / p for p in r.get('source_parts', [r['file']])]
    assert originals, f'No source files for {filename}'
    parts, digest, total = [], hashlib.sha256(), 0
    output = (SITE/'videos'/filename).open('wb') if target == 'vercel' else contextlib.nullcontext()
    with output as published:
        for original in originals:
            with original.open('rb') as f:
                while chunk := f.read(PART_SIZE):
                    if target == 'cloudflare':
                        path = f'media/{number:02d}-{r["sha256"][:12]}-{len(parts):02d}.bin'
                        (SITE/path).write_bytes(chunk)
                        parts.append({'path': '/'+path, 'size': len(chunk)})
                    else:
                        published.write(chunk)
                    digest.update(chunk)
                    total += len(chunk)
    assert digest.hexdigest() == r['sha256'], f'File changed: {filename}'
    path = '/videos/' + filename
    videos[path] = {'filename': filename, 'size': total, 'sha256': r['sha256'], 'parts': parts}
    shutil.copyfile(SOURCE/r['thumbnail'], SITE/r['thumbnail'])
    seconds = r['seconds']
    duration = f'{seconds:g} seconds' if seconds < 60 else f'{int(seconds//60)}:{round(seconds%60):02d}'
    video_loop = ' loop' if r.get('loop', False) else ''
    online = f'<a class="online" href="{html.escape(r["online_url"], quote=True)}" target="_blank" rel="noopener">Open looping slideshow <span aria-hidden="true">↗</span></a>' if r['online_url'] else ''
    card_class = 'card portrait' if r['format'] == 'Portrait 9:16' else 'card'
    audio_label = 'Silent' if r.get('audio', 'Silent') == 'Silent' else 'With sound'
    audio_links = []
    for field, label in [('audio_mp3', 'MP3'), ('audio_wav', 'WAV')]:
        if r.get(field):
            audio_path = r[field]
            (SITE/audio_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE/audio_path, SITE/audio_path)
            audio_links.append(f'<a href="/{html.escape(audio_path, quote=True)}" download>{label}</a>')
    audio_downloads = '<p class="audio-downloads">Beat only: ' + ' · '.join(audio_links) + '</p>' if audio_links else ''
    revision_query = '?v=' + r['sha256'][:12] if r.get('revision') else ''
    playback_path = path + revision_query
    download_path = path + '?download=1' + ('&v=' + r['sha256'][:12] if revision_query else '')
    poster_path = '/' + r['thumbnail'] + revision_query
    cards[number] = f'''<article class="{card_class}" id="video-{number}">
      <div class="screen"><video id="player-{number}" controls playsinline preload="none" poster="{poster_path}" aria-label="{html.escape(titles[number], quote=True)}"{video_loop}><source src="{playback_path}" type="video/mp4">Your browser does not support video. Use Download MP4 below.</video></div>
      <div class="details"><div class="eyebrow">{number:02d} <span>· {html.escape(r['format'])}</span></div>
      <h2>{html.escape(titles[number])}</h2><p class="description">{descriptions[number]}</p>
      <p class="specs">{duration} <span>·</span> {r['dimensions']} <span>·</span> {r['size_mb']} MB <span>·</span> {audio_label}</p>
      <div class="actions"><a class="download" href="{html.escape(download_path, quote=True)}" download="{filename}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m-5-5 5 5 5-5M5 16v4h14v-4"/></svg>Download MP4</a><button class="play" data-player="player-{number}" aria-label="Play {html.escape(titles[number], quote=True)}">Play video <span aria-hidden="true">▷</span></button></div>
      {audio_downloads}{online}<p class="error" hidden>Unable to load this video. Please reload the page and try again.</p></div></article>'''
    verification.append({'number': number, 'title': titles[number], 'filename': filename, 'bytes': total, 'sha256': digest.hexdigest(), 'parts': len(parts)})

if target == 'cloudflare':
    handler = (WORK/'video-handler.mjs').read_text()
    (SITE/'_worker.js').write_text(handler + '\nconst videos = ' + json.dumps(videos) + ';\nexport default createVideoHandler(videos);\n')
    (SITE/'_routes.json').write_text(json.dumps({'version': 1, 'include': ['/videos/*'], 'exclude': []}))
    (SITE/'_headers').write_text('/*\n  X-Robots-Tag: noindex\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n/media/*\n  Cache-Control: public, max-age=31536000, immutable\n')
(SITE/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
def collection_page(title, intro, numbers, navigation=''):
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><meta name="description" content="''' + html.escape(intro, quote=True) + '''"><meta name="theme-color" content="#f4f4f4"><title>2.009 · ''' + title + '''</title><link rel="stylesheet" href="/style.css"><script src="/app.js" defer></script></head>
<body><main><header><div class="topline"><div class="brand"><span>MIT 2.009</span><span class="colors" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></span></div>''' + navigation + '''</div><h1>''' + title + '''</h1><p class="intro">''' + intro + '''</p><p class="note">Original-quality MP4 downloads · Sound indicated on each video</p></header><section class="grid" aria-label="''' + title + ''' videos">''' + '\n'.join(cards[number] for number in numbers) + '''</section><footer>MIT 2.009 · Product Engineering Processes</footer></main></body></html>'''

newest_first = [r['number'] for r in reversed(records)]
(SITE/'tests').mkdir()
(SITE/'tests'/'index.html').write_text(collection_page(
    'All Tests', f'{len(records)} videos. Every version, newest first.', newest_first,
    '<nav aria-label="Collections"><a href="/tests/" aria-current="page">All Tests</a><a href="/">Selects <span aria-hidden="true">↗</span></a></nav>'))
# The already-shared root URL shows only the chosen videos, with no link to experiments.
selects_page = collection_page(
    'Selects', f'{len(selects)} selected videos. Watch, download, and post.',
    [number for number in newest_first if number in selects])
(SITE/'index.html').write_text(selects_page)
# Keep the short-lived /selects/ link working with exactly the same collection.
(SITE/'selects').mkdir()
(SITE/'selects'/'index.html').write_text(selects_page)
# A focused lecture link keeps the two long poster loops together.
poster_numbers = [r['number'] for r in records if r.get('poster_count') == 36 and r.get('seconds_per_poster') == 5]
if poster_numbers:
    (SITE/'posters').mkdir()
    (SITE/'posters'/'index.html').write_text(collection_page(
        'Lecture posters',
        '36 posters. Seamless, silent loops. Green → Purple → Red → Blue → Yellow → Pink. '
        'A new poster passes the center every five seconds; each full loop lasts three minutes.',
        poster_numbers,
        '<nav aria-label="Collections"><a href="/posters/" aria-current="page">Lecture posters</a>'
        '<a href="/tests/">All Tests <span aria-hidden="true">↗</span></a></nav>'))
# A separate share page keeps the feasibility slides easy to play for lecture.
feasibility_numbers = [r['number'] for r in records if r.get('collection') == 'feasibility']
if feasibility_numbers:
    (SITE/'feasibility').mkdir()
    feasibility_page = collection_page(
        'Feasibility carousel',
        'The six teams’ feasibility slides in a continuous, silent loop. '
        'A new slide passes the center every three seconds. '
        'Team presentations stay together in Green → Purple → Red → Blue → Yellow → Pink order.',
        feasibility_numbers,
        '<nav aria-label="Collections"><a href="/feasibility/" aria-current="page">Feasibility carousel</a>'
        '<a href="/posters/">Lecture posters</a><a href="/tests/">All Tests</a></nav>')
    feasibility_page = feasibility_page.replace('<section class="grid"', '<section class="grid" style="grid-template-columns:1fr"')
    feasibility_page = feasibility_page.replace('<div class="screen">', '<div class="screen" style="aspect-ratio:16/9">')
    (SITE/'feasibility'/'index.html').write_text(feasibility_page)
(SITE/'style.css').write_text('''*{box-sizing:border-box}html{color-scheme:light;scroll-behavior:smooth}body{margin:0;background:#f4f4f4;color:#171717;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}main{max-width:1280px;margin:auto;padding:54px 40px 32px}header{padding:0 0 38px}.topline{display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap}nav{display:flex;align-items:center;gap:6px}nav a{font-size:14px;text-decoration:none;color:#555;padding:10px 15px;border-radius:99px}nav a:hover{background:#e8e8e8}nav a[aria-current]{background:#171717;color:white}.brand{display:flex;align-items:center;gap:18px;font-size:14px;font-weight:700;letter-spacing:.09em}.colors{display:flex;gap:5px}.colors i{width:20px;height:5px;border-radius:9px;background:#d83439}.colors i:nth-child(2){background:#e57e20}.colors i:nth-child(3){background:#e6bf16}.colors i:nth-child(4){background:#36966a}.colors i:nth-child(5){background:#2b80c3}.colors i:nth-child(6){background:#8c59ad}h1{font-size:clamp(40px,5.8vw,68px);letter-spacing:-.055em;line-height:1.05;margin:30px 0 15px;font-weight:650}.intro{font-size:19px;line-height:1.5;margin:0;color:#505050}.note{font-size:13px;color:#666;margin:13px 0 0}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px}.card{background:white;border:1px solid #e8e8e8;border-radius:20px;overflow:hidden;box-shadow:0 4px 16px #00000003;scroll-margin-top:24px}.screen{aspect-ratio:3/2;background:#090909;display:flex;align-items:center;justify-content:center}.card.portrait .screen{aspect-ratio:auto;height:min(640px,70vh);background:#d4d4d4}.card.portrait video{width:auto;max-width:100%;aspect-ratio:9/16}video{width:100%;height:100%;display:block;object-fit:contain}.details{padding:25px 27px 26px}.eyebrow{font-size:13px;font-weight:700;color:#333}.eyebrow span{font-weight:400;color:#727272;margin-left:7px}h2{font-size:25px;line-height:1.18;letter-spacing:-.035em;font-weight:650;margin:12px 0}.description{font-size:15px;line-height:1.55;color:#595959;margin:0;min-height:47px}.specs{font-size:12px;color:#6a6a6a;margin:19px 0}.specs span{margin:0 7px}.actions{display:flex;gap:20px;align-items:center;flex-wrap:wrap}a,button{-webkit-tap-highlight-color:transparent}a.download{display:inline-flex;align-items:center;gap:9px;border-radius:99px;background:#171717;color:white;text-decoration:none;font-size:14px;font-weight:600;padding:13px 18px;min-height:46px}a.download:hover{background:#363636}svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}button.play{border:0;background:transparent;color:#333;padding:12px 0;cursor:pointer;font:inherit;font-size:14px}.play span{font-size:18px;vertical-align:-1px;margin-left:4px}.play:hover,.online:hover{text-decoration:underline}.online{display:inline-block;font-size:13px;color:#53626a;margin-top:22px;text-decoration:none}.online span{margin-left:4px}.audio-downloads{font-size:13px;color:#666;margin:20px 0 0}.audio-downloads a{color:#3c596a;text-underline-offset:3px}.error{color:#a02020;font-size:13px;line-height:1.5}footer{padding:38px 0 0;color:#757575;font-size:12px}a:focus-visible,button:focus-visible,video:focus-visible{outline:3px solid #237bd3;outline-offset:4px}@media(max-width:720px){main{padding:30px 18px 25px}header{padding-bottom:27px}.grid{grid-template-columns:1fr;gap:23px}h1{margin-top:25px}.intro{font-size:17px}.details{padding:22px}.description{min-height:0}h2{font-size:24px}.specs{font-size:12px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
''')
(SITE/'app.js').write_text('''const players = [...document.querySelectorAll('video')];
for (const button of document.querySelectorAll('[data-player]')) {
  const player = document.getElementById(button.dataset.player);
  const title = player.getAttribute('aria-label');
  const error = button.closest('.details').querySelector('.error');
  button.addEventListener('click', async () => {
    if (!player.paused) { player.pause(); return; }
    error.hidden = true;
    try { await player.play(); } catch (reason) { if (reason.name !== 'AbortError') error.hidden = false; }
  });
  player.addEventListener('play', () => {
    error.hidden = true;
    players.forEach(other => { if (other !== player) other.pause(); });
    button.textContent = 'Pause video Ⅱ';
    button.setAttribute('aria-label', 'Pause ' + title);
  });
  player.addEventListener('pause', () => {
    button.textContent = 'Play video ▷';
    button.setAttribute('aria-label', 'Play ' + title);
  });
  player.addEventListener('error', () => { error.hidden = false; });
}
''')
if target == 'cloudflare':
    (WORK/'video-manifest.json').write_text(json.dumps(videos, indent=2))
    (OUT/'VERIFICATION.json').write_text(json.dumps(verification, indent=2))
    zip_path = OUT/'MIT-2.009-Selected-Videos-Cloudflare.zip'
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_STORED) as z:
        for f in sorted(SITE.rglob('*')):
            if f.is_file():
                assert f.stat().st_size < 25 * 1024 * 1024
                z.write(f, str(f.relative_to(SITE)))
    print(json.dumps({'zip': str(zip_path), 'bytes': zip_path.stat().st_size, 'videos': verification}, indent=2))
else:
    (OUT/'VERCEL-VERIFICATION.json').write_text(json.dumps(verification, indent=2))
    print(json.dumps({'target': target, 'directory': str(SITE), 'videos': len(verification),
        'bytes': sum(p.stat().st_size for p in SITE.rglob('*') if p.is_file())}, indent=2))
