from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile
from PIL import Image, ImageDraw, ImageOps

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--repo', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
BASE = Path(__file__).resolve().parent
REPO = args.repo.resolve()
OUT = args.output.resolve()
QA = BASE / 'qa'
OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
records = []
photos = {}
thumbs = []
with zipfile.ZipFile(args.source) as archive:
    names = sorted(n for n in archive.namelist()
                   if n.startswith('26-10-28-Research-to-Date-Slideshow/')
                   and n.lower().endswith('.jpg') and not Path(n).name.startswith('._'))
    assert len(names) == 86
    assert [int(Path(n).name.split('-')[0]) for n in names] == list(range(1, 87))
    for name in names:
        data = archive.read(name)
        filename = Path(name).name
        photos[filename] = data
        import io
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            displayed = ImageOps.exif_transpose(image).convert('RGB')
            width, height = displayed.size
            thumb = ImageOps.contain(displayed, (220, 150))
            thumbs.append(thumb)
        records.append({'filename': filename, 'bytes': len(data),
                        'sha256': hashlib.sha256(data).hexdigest(),
                        'width': width, 'height': height})

sheet = Image.new('RGB', (6 * 240, 15 * 180), '#161616')
draw = ImageDraw.Draw(sheet)
for i, thumb in enumerate(thumbs):
    x, y = (i % 6) * 240, (i // 6) * 180
    sheet.paste(thumb, (x + (240 - thumb.width)//2, y + (150-thumb.height)//2))
    draw.text((x+10, y+157), str(i+1).zfill(2), fill='white')
sheet.save(QA / 'contact-sheet.jpg', quality=85)
with Image.open(io.BytesIO(photos[records[0]['filename']])) as first:
    first = ImageOps.exif_transpose(first).convert('RGB')
    preview = Image.new('RGB', (1200, 800), 'black')
    thumb = ImageOps.contain(first, preview.size)
    preview.paste(thumb, ((1200-thumb.width)//2, (800-thumb.height)//2))
    preview.save(REPO/'assets/previews/101-research-to-date-2026-10-28.jpg', quality=88)

sequence = {'source_archive': args.source.name,
            'source_archive_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
            'photo_count': 86, 'dissolve_seconds': 0.1,
            'interval_options_seconds': [2, 3.5], 'loop': True, 'photos': records}
catalog_path = REPO/'assets/CATALOG.json'
catalog = json.loads(catalog_path.read_text())
assert [r['number'] for r in catalog] == list(range(1, 101))
template = REPO/'slideshows/2026-10-26-3s'
variants = [(101, 2, '2s'), (102, 3.5, '3-5s')]
for number, seconds, slug in variants:
    relative = f'slideshows/2026-10-28-research-{slug}'
    dest = REPO/relative
    assert not dest.exists()
    (dest/'photos').mkdir(parents=True)
    for filename, data in photos.items():
        (dest/'photos'/filename).write_bytes(data)
    title = f'MIT 2.009 · Research to Date · {seconds} seconds per photo'
    html = (template/'index.html').read_text().replace(
        'MIT 2.009 · October 26 Lecture · 3 seconds per photo', title)
    (dest/'index.html').write_text(html)
    (dest/'slideshow.js').write_text((template/'slideshow.js').read_text().replace(
        'const INTERVAL_MS = 3000;', f'const INTERVAL_MS = {int(seconds*1000)};'))
    shutil.copyfile(template/'style.css', dest/'style.css')
    (dest/'photos.js').write_text('window.SLIDESHOW_PHOTOS = '+json.dumps(list(photos), indent=2)+';\n')
    filename = f'MIT-2.009-Research-to-Date-2026-10-28-{seconds}s.zip'
    with zipfile.ZipFile(OUT/filename, 'w', compression=zipfile.ZIP_STORED) as archive:
        for file in sorted(dest.rglob('*')):
            if file.is_file(): archive.write(file, str(file.relative_to(dest)))
    catalog.append({'number': number, 'media_type': 'slideshow',
                    'title': f'Research to Date — {seconds} seconds per photo',
                    'description': 'Updated collection: all 86 supplied photos in numbered order. Complete photographs on black, automatic playback, and a continuous loop. Use F for full screen, Space to pause, and the arrow keys to browse.',
                    'source_directory': relative,
                    'thumbnail': 'previews/101-research-to-date-2026-10-28.jpg',
                    'photo_count': 86, 'seconds_per_slide': seconds, 'dissolve_seconds': 0.1,
                    'seconds': 86*seconds, 'audio': 'Silent', 'loop': True,
                    'download_filename': filename})
catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False)+'\n')
notes = REPO/'assets/production-notes/lecture-slideshow-2026-10-28-updated'
notes.mkdir(parents=True)
(notes/'sequence.json').write_text(json.dumps(sequence, indent=2)+'\n')
shutil.copyfile(Path(__file__), notes/'prepare.py')
(notes/'README.md').write_text('''# Research to Date — October 28, 2026 updated collection

All 86 numbered JPEGs from Danny’s updated collection retain their original
bytes and numbered order. Both versions use the established player from
items 96–97, fitting complete images on black with a 100 ms cross-dissolve.
The dissolve is included in each 2- or 3.5-second interval. Silent loops
are 172 seconds (2:52) and 301 seconds (5:01).

Catalog entries 101 and 102 are in All Tests. Playback starts automatically;
controls hide, Space pauses/resumes, arrows step, and F toggles fullscreen.
Each offline ZIP contains the complete player and all photos. Unzip and open
index.html. Earlier catalog entries and Selects are preserved.

sequence.json records the input archive and original photograph SHA-256s.
''')
print(json.dumps({'photos': len(records), 'loops_seconds': [172, 301],
                  'offline_files': [str(p) for p in sorted(OUT.glob('*.zip'))]}, indent=2))
