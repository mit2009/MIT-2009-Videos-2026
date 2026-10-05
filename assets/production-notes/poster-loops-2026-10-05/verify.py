import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image
from render import BASE, OUT, DURATION, FPS, W, H, prepare, Renderer

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['flat', 'carousel'], required=True)
args = parser.parse_args()
mode = args.mode
suffix = 'Flat-Ribbon' if mode == 'flat' else 'Curved-Carousel'
source = OUT / f'MIT-2.009-36-Posters-{suffix}-180s.mp4'
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(source)]))
assert len(probe['streams']) == 1
stream = probe['streams'][0]
assert stream['codec_type'] == 'video' and stream['codec_name'] == 'h264'
assert (stream['width'], stream['height']) == (W, H)
assert stream['r_frame_rate'] == '60/1'
assert int(stream['nb_frames']) == DURATION * FPS
assert float(probe['format']['duration']) == DURATION
subprocess.run(['ffmpeg', '-v', 'error', '-threads', '2', '-i', str(source), '-f', 'null', '-'], check=True)
strip, manifest = prepare()
renderer = Renderer(strip, mode)
assert renderer.frame(0).tobytes() == renderer.frame(DURATION * FPS).tobytes()
if mode == 'flat':
    # Every five-second center crossing must show its entire expected poster.
    for i, record in enumerate(manifest['posters']):
        expected = Image.open(BASE / record['image']).convert('RGB').resize((720, 1080), Image.Resampling.LANCZOS)
        actual = renderer.frame(i * 5 * FPS).crop((600, 0, 1320, 1080))
        assert actual.tobytes() == expected.tobytes(), record['number']
    # A 2.5-second step shifts the visible artwork exactly 360 pixels right.
    first = renderer.frame(0)
    later = renderer.frame(150)
    assert first.crop((0, 0, W - 360, H)).tobytes() == later.crop((360, 0, W, H)).tobytes()
renderer.frame(0).save(BASE / 'review' / f'{mode}-0s.jpg', quality=95)
with source.open('rb') as f:
    sha = hashlib.file_digest(f, 'sha256').hexdigest()
path = BASE / 'verification.json'
verification = json.loads(path.read_text()) if path.exists() else {'source_poster_count': 36, 'color_cycle': manifest['color_cycle'], 'videos': {}}
verification['videos'][mode] = {
    'filename': source.name,
    'sha256': sha,
    'bytes': source.stat().st_size,
    'duration': float(probe['format']['duration']),
    'frames': int(stream['nb_frames']),
    'width': W, 'height': H, 'fps': FPS,
    'audio_streams': 0,
    'complete_decode': 'passed',
    'periodic_loop_closure': 'exact',
    'source_sequence': '36 original pages; 6 complete color cycles',
    'motion': 'left to right',
    'seconds_per_center_crossing': 5,
    'all_center_posters_pixel_verified': mode == 'flat',
}
path.write_text(json.dumps(verification, indent=2) + '\n')
print(json.dumps(verification['videos'][mode], indent=2))
