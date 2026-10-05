"""Render the original poster artwork as continuous, silent lecture loops."""
import argparse
import hashlib
import json
import math
import subprocess
import time
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent
OUT = BASE.parent.parent / 'outputs/MIT-2.009-Poster-Loops-2026-10-05'
W, H, FPS = 1920, 1080, 60
POSTER_W, POSTER_H = 720, 1080
COUNT, SECONDS_PER_POSTER = 36, 5
DURATION = COUNT * SECONDS_PER_POSTER
TOTAL = COUNT * POSTER_W


def prepare():
    manifest = json.loads((BASE / 'sequence.json').read_text())
    assert len(manifest['posters']) == COUNT
    assert manifest['color_cycle'] == ['Green', 'Purple', 'Red', 'Blue', 'Yellow', 'Pink']
    assert [r['color'] for r in manifest['posters']] == manifest['color_cycle'] * 6
    tiles = []
    for record in manifest['posters']:
        source = BASE / record['image']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == record['image_sha256']
        with Image.open(source) as im:
            tiles.append(im.convert('RGB').resize((POSTER_W, POSTER_H), Image.Resampling.LANCZOS))
    # The next poster enters from the left. Reverse spatial order so the
    # chronological center crossings follow the requested color sequence.
    strip = Image.new('RGB', (TOTAL, POSTER_H))
    for i, index in enumerate([0] + list(range(COUNT - 1, 0, -1))):
        strip.paste(tiles[index], (i * POSTER_W, 0))
    return strip, manifest


def wrapped_crop(strip, start, width):
    x = int(start) % TOTAL
    if x + width <= TOTAL:
        return strip.crop((x, 0, x + width, POSTER_H))
    result = Image.new('RGB', (width, POSTER_H))
    first = TOTAL - x
    result.paste(strip.crop((x, 0, TOTAL, POSTER_H)), (0, 0))
    result.paste(strip.crop((0, 0, width - first, POSTER_H)), (first, 0))
    return result


class Renderer:
    def __init__(self, strip, mode):
        self.strip = strip
        self.mode = mode
        self.radius = TOTAL / (2 * math.pi)
        self.distance = 700
        # Front poster is 1000 pixels tall, with its entire artwork visible.
        self.focal = self.distance * 1000 / POSTER_H
        if mode == 'carousel':
            self.min_arc = self.surface(0)[0]
            self.max_arc = self.surface(W)[0]
            self.mesh = []
            # Eight-pixel strips accurately approximate the cylindrical
            # projection; connected source edges avoid gaps between posters.
            for left in range(0, W, 8):
                right = min(W, left + 8)
                x0, z0 = self.surface(left)
                x1, z1 = self.surface(right)
                yl0 = -H / 2 * z0 / self.focal + POSTER_H / 2
                yr0 = -H / 2 * z1 / self.focal + POSTER_H / 2
                yl1 = H / 2 * z0 / self.focal + POSTER_H / 2
                yr1 = H / 2 * z1 / self.focal + POSTER_H / 2
                self.mesh.append(((left, 0, right, H),
                                  (x0 - self.min_arc, yl0, x0 - self.min_arc, yl1,
                                   x1 - self.min_arc, yr1, x1 - self.min_arc, yr0)))

    def surface(self, pixel_x):
        dx = (pixel_x - W / 2) / self.focal
        a = 1 + dx * dx
        distance_to_center = self.radius + self.distance
        discriminant = distance_to_center ** 2 - a * (distance_to_center ** 2 - self.radius ** 2)
        assert discriminant > 0
        depth = (distance_to_center - math.sqrt(discriminant)) / a
        world_x = dx * depth
        world_z = -distance_to_center + depth
        angle = math.atan2(world_x, -world_z)
        return angle * self.radius, depth

    def frame(self, frame_number):
        # Integer rational phase makes the wrap exact without a repeated frame.
        phase = (frame_number % (DURATION * FPS)) * POSTER_W / (SECONDS_PER_POSTER * FPS)
        if self.mode == 'flat':
            start = POSTER_W / 2 - W / 2 - phase
            whole = math.floor(start)
            source = wrapped_crop(self.strip, whole, W + 1)
            first = source.crop((0, 0, W, H))
            fraction = start - whole
            if fraction == 0:
                return first
            # Horizontal-only bilinear sampling preserves subpixel movement
            # without the cost of a general two-dimensional perspective warp.
            return Image.blend(first, source.crop((1, 0, W + 1, H)), fraction)
        start = POSTER_W / 2 + self.min_arc - phase
        whole = math.floor(start)
        fraction = start - whole
        source = wrapped_crop(self.strip, whole, math.ceil(self.max_arc - self.min_arc) + 3)
        mesh = [(box, tuple(value + fraction if i % 2 == 0 else value
                           for i, value in enumerate(quad))) for box, quad in self.mesh]
        return source.transform((W, H), Image.Transform.MESH, mesh,
                                Image.Resampling.BICUBIC, fillcolor=(15, 17, 21))


def encode(renderer, output, duration, preview=False):
    output.parent.mkdir(parents=True, exist_ok=True)
    frames = round(duration * FPS)
    command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
               '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
               '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '19', '-threads', '6',
               '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709',
               '-colorspace', 'bt709', '-movflags', '+faststart', '-frames:v', str(frames), str(output)]
    started = time.monotonic()
    with (output.with_suffix('.render.log')).open('w') as log:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=log)
        try:
            for i in range(frames):
                process.stdin.write(renderer.frame(i).tobytes())
                if i and i % (FPS * 15) == 0:
                    print(json.dumps({'mode': renderer.mode, 'seconds_done': i / FPS,
                                      'total_seconds': duration, 'elapsed_seconds': round(time.monotonic() - started)}), flush=True)
        finally:
            process.stdin.close()
        result = process.wait()
        if result:
            raise RuntimeError(f'FFmpeg failed with {result}; see {output.with_suffix(".render.log")}')
    print(json.dumps({'complete': str(output), 'bytes': output.stat().st_size,
                      'render_seconds': round(time.monotonic() - started, 1)}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['flat', 'carousel'], required=True)
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--stills', action='store_true')
    args = parser.parse_args()
    strip, manifest = prepare()
    renderer = Renderer(strip, args.mode)
    review = BASE / 'review'
    review.mkdir(exist_ok=True)
    if args.stills:
        for seconds in [0, 2.5, 5, 175, 179.9833333333, 180]:
            renderer.frame(round(seconds * FPS)).save(review / f'{args.mode}-{seconds:g}s.jpg', quality=95)
        assert renderer.frame(0).tobytes() == renderer.frame(DURATION * FPS).tobytes()
        print(f'{args.mode}: loop closure matches exactly')
    else:
        suffix = 'Flat-Ribbon' if args.mode == 'flat' else 'Curved-Carousel'
        output = (review / f'{args.mode}-preview.mp4' if args.preview else
                  OUT / f'MIT-2.009-36-Posters-{suffix}-180s.mp4')
        encode(renderer, output, 10 if args.preview else DURATION, args.preview)
