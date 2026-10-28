from pathlib import Path
import hashlib, json, shutil, zipfile

BASE = Path(__file__).resolve().parent
REPO = BASE.parent / 'mit2009-video-catalog'
SOURCE = Path('/Users/dannygoldfield/MIT Dropbox/2.009media/26-2.009-Media/Exports/26-10-28-Research-So-Far-This-Semester.zip')
OUT = BASE.parent.parent / 'outputs/MIT-2.009-Research-So-Far-2026-10-28'
PHOTOS = BASE / 'photos'
for folder in [PHOTOS, OUT, BASE/'qa']:
    folder.mkdir(parents=True, exist_ok=True)

records=[]
with zipfile.ZipFile(SOURCE) as archive:
    names=sorted(n for n in archive.namelist() if n.startswith('26-10-28-Research-So-Far-This-Semester/') and n.lower().endswith('.jpg') and not Path(n).name.startswith('._'))
    assert len(names)==69
    assert [int(Path(n).name.split('-')[0]) for n in names]==list(range(1,70))
    for name in names:
        data=archive.read(name)
        filename=Path(name).name
        (PHOTOS/filename).write_bytes(data)
        records.append({'filename':filename,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})

sequence={'source_archive':SOURCE.name,'source_archive_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'photo_count':69,'dissolve_seconds':0.1,'interval_options_seconds':[3,5],'loop':True,'photos':records}
(BASE/'sequence.json').write_text(json.dumps(sequence,indent=2)+'\n')
catalog_path=REPO/'assets/CATALOG.json'
catalog=json.loads(catalog_path.read_text())
assert [r['number'] for r in catalog]==list(range(1,99))
for number,seconds in [(99,3),(100,5)]:
    dest=REPO/f'slideshows/2026-10-28-{seconds}s'
    assert not dest.exists()
    dest.mkdir(parents=True)
    shutil.copytree(PHOTOS,dest/'photos')
    template=REPO/'slideshows/2026-10-26-3s'
    title=f'MIT 2.009 · Research So Far This Semester · {seconds} seconds per photo'
    html=(template/'index.html').read_text().replace('MIT 2.009 · October 26 Lecture · 3 seconds per photo',title)
    (dest/'index.html').write_text(html)
    (dest/'slideshow.js').write_text((template/'slideshow.js').read_text().replace('const INTERVAL_MS = 3000;',f'const INTERVAL_MS = {seconds*1000};'))
    shutil.copyfile(template/'style.css',dest/'style.css')
    (dest/'photos.js').write_text('window.SLIDESHOW_PHOTOS = '+json.dumps([r['filename'] for r in records],indent=2)+';\n')
    filename=f'MIT-2.009-Research-So-Far-2026-10-28-{seconds}s.zip'
    with zipfile.ZipFile(OUT/filename,'w',compression=zipfile.ZIP_STORED) as archive:
        for file in sorted(dest.rglob('*')):
            if file.is_file(): archive.write(file,str(file.relative_to(dest)))
    catalog.append({'number':number,'media_type':'slideshow','title':f'Research So Far This Semester — {seconds} seconds per photo','description':'All 69 supplied research photos in numbered order, from early research through Concept Review. Complete photographs on black, automatic playback, and a continuous loop. Use F for full screen, Space to pause, and the arrow keys to browse.','source_directory':f'slideshows/2026-10-28-{seconds}s','thumbnail':'previews/99-research-2026-10-28.jpg','photo_count':69,'seconds_per_slide':seconds,'dissolve_seconds':0.1,'seconds':69*seconds,'audio':'Silent','loop':True,'download_filename':filename})
catalog_path.write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n')
notes=REPO/'assets/production-notes/lecture-slideshow-2026-10-28'
notes.mkdir(parents=True)
shutil.copyfile(BASE/'sequence.json',notes/'sequence.json')
shutil.copyfile(Path(__file__),notes/'prepare.py')
(notes/'README.md').write_text('''# Research So Far This Semester — October 28, 2026

Two silent lecture slideshows from all 69 numbered photos in Danny’s ZIP.
Original photo bytes and numbered order are preserved. Each image fits in
full on black. The 100 ms cross-dissolve is included in the 3- or 5-second
interval. Loops are 207 seconds (3:27) and 345 seconds (5:45).

Catalog entries 99 and 100 are in All Tests. Previous entries and Selects
are unchanged. Playback reuses the established October 26 slideshow:
automatic start, continuous loop, controls that hide, arrows to step,
Space to pause/resume, and F for full screen. Each version has an offline
ZIP; unzip it and open index.html. No network connection is then needed.

The sequence manifest records every source SHA-256. Catalog checks verify
photo count, filename order, unmodified bytes, timing, and offline packages.
''')
print(json.dumps({'photos':len(records),'loops_seconds':[207,345],'offline_files':[str(p) for p in sorted(OUT.glob('*.zip'))]},indent=2))
