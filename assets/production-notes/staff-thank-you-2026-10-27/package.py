from pathlib import Path
import hashlib, json, shutil, subprocess

BASE = Path(__file__).resolve().parent
REPO = BASE.parent / 'mit2009-video-catalog'
OUT = BASE.parent.parent / 'outputs/MIT-2.009-Staff-Thank-You-2026-10-27'
VIDEO = OUT / 'MIT-2.009-Staff-Thank-You-Carousel-Test-38s.mp4'
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(VIDEO)]))
assert len(probe['streams']) == 1
stream = probe['streams'][0]
assert stream['codec_type'] == 'video' and stream['codec_name'] == 'h264'
assert (stream['width'], stream['height']) == (1920, 1080)
assert stream['r_frame_rate'] == '60/1'
assert int(stream['nb_frames']) == 2295
assert abs(float(probe['format']['duration']) - 38.25) < 0.01
subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(VIDEO), '-f', 'null', '-'], check=True)
data = VIDEO.read_bytes()
digest = hashlib.sha256(data).hexdigest()
assert data.index(b'moov') < data.index(b'mdat')
sequence = json.loads((BASE/'sequence.json').read_text())
assert len(sequence['photos']) == 11
for photo in sequence['photos']:
    original = BASE/'input/26-10-27-Staff-Thank-You-Test'/photo['filename']
    assert hashlib.sha256(original.read_bytes()).hexdigest() == photo['sha256']

for i in range(11):
    time = 3.5 + (i+.5)*2.75
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(time), '-i', str(VIDEO), '-frames:v', '1', str(BASE/f'review/encoded-{i+1:02d}.jpg')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '13.125', '-i', str(VIDEO), '-frames:v', '1', str(OUT/'preview.jpg')], check=True)

check = {'file': VIDEO.name, 'sha256': digest, 'bytes': len(data), 'seconds': 38.25, 'dimensions': [1920,1080], 'fps': 60, 'frames': 2295, 'audio_streams': 0, 'full_decode': 'passed', 'fast_start': True, 'supplied_photos': 11, 'photo_source_hashes': 'passed', 'center_crossing_seconds': [3.5+(i+.5)*2.75 for i in range(11)], 'photo_interval_seconds': 2.75, 'opening_seconds': 3.5, 'closing_seconds': 4.5, 'projected_36_staff_seconds': 107, 'visual_beat_seconds': .55, 'visual_bpm': 60/.55}
(BASE/'verification.json').write_text(json.dumps(check, indent=2)+'\n')
catalog_path = REPO/'assets/CATALOG.json'
catalog = json.loads(catalog_path.read_text())
assert [r['number'] for r in catalog] == list(range(1,98)), 'New item must append to the existing catalog'
shutil.copyfile(VIDEO, REPO/'assets/videos'/VIDEO.name)
shutil.copyfile(OUT/'preview.jpg', REPO/'assets/previews/98-staff-thank-you.jpg')
catalog.append({'number':98, 'title':'Staff thank-you — Celebratory carousel', 'description':'Silent concept for Peko: all 11 supplied staff portraits glide through a curved carousel inspired by video 61, with six-color pixel lights and radiating rays inspired by video 57. A new portrait crosses the center every 2.75 seconds. Includes opening and closing thank-you titles. This 38.25-second sample scales to 1:47 for 36 staff at the same pace; the visual beat can be retimed to the eventual song.', 'file':'videos/'+VIDEO.name, 'seconds':38.25, 'dimensions':'1920 × 1080', 'format':'Landscape 16:9', 'photo_count':11, 'size_mb':round(len(data)/1e6,1), 'online_url':'', 'thumbnail':'previews/98-staff-thank-you.jpg', 'sha256':digest, 'fps':60, 'codec':'H.264', 'audio':'Silent', 'fast_start':True, 'loop':False, 'collection':'staff-thank-you', 'seconds_per_photo':2.75, 'opening_seconds':3.5, 'closing_seconds':4.5, 'projected_36_staff_seconds':107, 'visual_bpm':round(60/.55,2), 'reference_videos':[61,57], 'added_text':True})
catalog_path.write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n')
notes = REPO/'assets/production-notes/staff-thank-you-2026-10-27'
notes.mkdir(parents=True,exist_ok=True)
for name in ['prepare.cjs','render.cjs','package.py','sequence.json','verification.json']:
    shutil.copyfile(BASE/name, notes/name)
(notes/'README.md').write_text('''# Staff thank-you carousel test — October 27, 2026

Danny requested a silent example for Peko combining the curved carousel in
video 61 with the Pixel + Prism celebration in video 57. All eleven supplied
2600 × 2600 photographs appear in filename order. Their complete square frames
pass through the center; the curved projection makes the sides recede.
The lights sit around and behind the photographs. No names are inferred.

The sample is 38.25 seconds: a 3.5-second opening, 30.25 seconds of photos at
2.75 seconds per center crossing, and a 4.5-second closing. Applying that same
pace to 36 photos gives 107 seconds (1:47). Pixel pulses have a 0.55-second
beat (about 109 BPM), with slower rotating rays and color changes. This is a
visual timing sketch; the eventual Suno song can determine the final timing.

1920 × 1080, 60 fps, H.264, no audio stream, fast-start MP4. Added as item 98
in All Tests only. Existing items and Selects are preserved.

QA: all eleven source hashes verified; full MP4 decode passes; duration,
resolution, frame count, silent audio status, and fast start checked. Center
frames were extracted from the encoded MP4 and visually reviewed.

Reproduction: place the source ZIP photos under
input/26-10-27-Staff-Thank-You-Test in work/staff-thank-you-2026-10-27.
Run prepare.cjs and render.cjs with Node, @napi-rs/canvas, sharp, and FFmpeg.
Original photo files are kept locally and are not published separately.

Watch: https://26-mit-2009-videos.vercel.app/tests/#video-98
''')
print(json.dumps(check,indent=2))
