"""Verify all three requested duration tests before adding them to All Tests."""
from pathlib import Path
import hashlib, json, shutil, struct, subprocess, re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'outputs/MIT-2.009-Finals-CTA-Tests-2026-10-04'
REPO = HERE.parent / 'mit2009-video-catalog'
NOTES = REPO / 'assets/production-notes/finals-cta-2026-10-04'

def run(args):
    return subprocess.run(args, capture_output=True, check=True)

def audio_hash(path):
    return run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).stdout.decode().strip().split('=')[1]

def pcm(path):
    return run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-f','s24le','-acodec','pcm_s24le','-']).stdout

catalog = json.loads((REPO / 'assets/CATALOG.json').read_text())
assert len(catalog) == 43 and catalog[-1]['number'] == 56
selects_before = (REPO / 'assets/SELECTS.json').read_bytes()
original = json.loads((REPO / 'assets/production-notes/blue-disco-d-2026-09-26/pixel-details.json').read_text())
source = OUT / 'Disco-D-Finals-20s-master.wav'
source_pcm = pcm(source)
bps = 48000 * 2 * 3
tail = None
records, verification = [], []
for number, duration in [(57,13),(58,15),(59,17)]:
    landing = duration - 8
    d = json.loads((OUT / f'{duration}s-details.json').read_text())
    video, audio = OUT / d['file'], OUT / f'Disco-D-Finals-{duration}s.m4a'
    ah = audio_hash(audio)
    if audio_hash(video) != ah:
        fixed = video.with_name(video.stem + '-remux.mp4')
        run(['ffmpeg','-v','error','-y','-i',str(video),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(duration),'-movflags','+faststart',str(fixed)])
        assert audio_hash(fixed) == ah
        fixed.replace(video)
    probe = json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]).stdout)
    v, a = probe['streams']
    assert (v['codec_name'],v['width'],v['height'],v['r_frame_rate'],v['pix_fmt'],int(v['nb_frames'])) == ('h264',1080,1920,'60/1','yuv420p',duration*60)
    assert (a['codec_name'],int(a['sample_rate']),a['channels'],float(a['start_time'])) == ('aac',48000,2,0)
    assert float(probe['format']['duration']) == duration
    assert d['target'] == 88 and d['settledTime'] == landing and d['celebrationAt'] == landing
    assert d['photos'] == original['photos'] and d['celebrationSeconds'] == 3
    assert d['retainNeighbors'] and d['audioTempoBPM'] == 120
    assert d['transitionStart'] == duration-5 and d['transitionSeconds'] == 1
    assert d['cardStart'] == duration-4 and d['cardHoldSeconds'] == 4
    assert d['ctaText'] == ['MIT 2.009','FINALS','WATCH LIVE','DEC 7']
    assert d['ctaURL'] is None and d['ctaTime'] is None
    run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'])
    frozen=run(['ffmpeg','-hide_banner','-i',str(video),'-vf','freezedetect=n=-50dB:d=3.8','-an','-f','null','-']).stderr.decode()
    starts=[float(t) for t in re.findall(r'freeze_start: ([0-9.]+)',frozen)]
    assert any(abs(t-(duration-4))<.1 for t in starts), starts
    boxes = []
    with video.open('rb') as f:
        while header := f.read(8):
            size, kind = struct.unpack('>I4s', header)
            header_size = 8
            if size == 1:
                size = struct.unpack('>Q', f.read(8))[0]
                header_size = 16
            assert size >= header_size
            boxes.append(kind.decode())
            f.seek(size-header_size, 1)
    assert boxes.index('moov') < boxes.index('mdat')
    data = pcm(OUT / f'Disco-D-Finals-{duration}s.wav')
    assert len(data) == duration*bps
    start = (20-duration)*bps
    # The source samples outside the opening/closing fades remain unchanged.
    assert data[bps:-bps] == source_pcm[start+bps:20*bps-bps]
    this_tail = data[-8*bps:]
    if tail is None:
        tail = this_tail
    else:
        assert tail == this_tail, 'The three winning phrases must be identical'
    digest = hashlib.sha256(video.read_bytes()).hexdigest()
    records.append(dict(number=number,title=f'Finals invitation — {duration} seconds',
        description=f'The portrait lands at {landing} seconds, celebrates for three seconds, then a one-second rush through the rays reveals the Finals invitation. The closing card reads MIT 2.009 FINALS · WATCH LIVE DEC 7 and holds still for four seconds. Same Pixel + Prism look, 54-photo sequence, and eight-second Disco D finish. Total running time: {duration} seconds.',
        file='videos/'+video.name,seconds=duration,dimensions='1080 × 1920',format='Portrait 9:16',photo_count=54,
        size_mb=round(video.stat().st_size/1e6,1),online_url='',thumbnail=f'previews/{number}.jpg',sha256=digest,
        fps=60,codec='H.264',audio=f'Disco D — Space Disco, 120 BPM · Finals {duration}-second edit',audio_sha256=ah,
        fast_start=True,loop=False,landing_seconds=landing,celebration_seconds=3,transition_seconds=1,cta_hold_seconds=4))
    verification.append(dict(number=number,seconds=duration,frames=duration*60,landing_seconds=landing,celebration_seconds=3,
        same_54_original_photos=True,full_decode_pass=True,fast_start=True,audio_sha256=ah,video_sha256=digest,
        audio_source_start=20-duration,audio_source_end=20,original_tempo_and_gain=True,identical_eight_second_music_finish=True,transition_seconds=1,cta_hold_seconds=4,encoded_static_card_verified=True,cta_text=['MIT 2.009','FINALS','WATCH LIVE','DEC 7']))
    print(f'Verified {number}: {duration}s, landing {landing}s, {video.stat().st_size/1e6:.1f} MB', flush=True)

NOTES.mkdir(parents=True, exist_ok=True)
for record, duration in zip(records,[13,15,17]):
    shutil.copy2(OUT / Path(record['file']).name, REPO / 'assets' / record['file'])
    shutil.copy2(OUT / f'{duration}s-poster.jpg', REPO / 'assets' / record['thumbnail'])
    shutil.copy2(OUT / f'{duration}s-details.json', NOTES / f'{duration}s-details.json')
for name in ['render.cjs','lights.cjs','closing.cjs','prepare.py','package.py']:
    shutil.copy2(HERE / name, NOTES / name)
(OUT / 'VERIFICATION.json').write_text(json.dumps(verification, indent=2)+'\n')
shutil.copy2(OUT / 'VERIFICATION.json', NOTES / 'VERIFICATION.json')
(REPO / 'assets/CATALOG.json').write_text(json.dumps(catalog+records, ensure_ascii=False, indent=2)+'\n')
assert (REPO / 'assets/SELECTS.json').read_bytes() == selects_before
print('Three requested experiments added to All Tests; Selects preserved.')
