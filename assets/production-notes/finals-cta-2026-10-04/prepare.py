from pathlib import Path
import subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PREVIOUS=HERE.parent/'headshot-pixel-prism-duration-2026-10-03'
OUT=ROOT/'outputs/MIT-2.009-Finals-CTA-Tests-2026-10-04'
OUT.mkdir(parents=True,exist_ok=True)
(HERE/'lights.cjs').write_text((PREVIOUS/'lights.cjs').read_text())
s=(PREVIOUS/'render.cjs').read_text()
s=s.replace("if(![15,13,11].includes(DURATION))throw Error('Choose 15, 13, or 11 seconds');\nconst LANDING=DURATION-3;", "if(![13,15,17].includes(DURATION))throw Error('Choose 13, 15, or 17 seconds');\nconst LANDING=DURATION-8,TRANSITION_START=DURATION-5,CARD_START=DURATION-4;")
s=s.replace('MIT-2.009-Pixel-Prism-Duration-Tests-2026-10-03','MIT-2.009-Finals-CTA-Tests-2026-10-04')
s=s.replace('MIT-2.009-Blue-Pixel-Prism-Disco-D-${DURATION}s','MIT-2.009-Finals-Light-Tunnel-${DURATION}s')
s=s.replace('`Disco-D-${DURATION}s.m4a`','`Disco-D-Finals-${DURATION}s.m4a`')
s=s.replace('const lights=createLights(mode,LANDING);', "const lights=createLights(mode,LANDING);\nconst {createClosing}=require('./closing.cjs');\nconst closing=createClosing();")
s=s.replace('  function frame(t){\n', '  function frame(t){\n    if(t>=CARD_START){closing.draw(ctx,t,TRANSITION_START,CARD_START);return;}\n')
s=s.replace('    lights.front(ctx,t,t-celebrationAt);','    lights.front(ctx,t,t-celebrationAt);\n    closing.draw(ctx,t,TRANSITION_START,CARD_START);')
s=s.replace('const stillTimes=[0,LANDING*.25,LANDING*.75,LANDING-.5,LANDING,LANDING+.6,LANDING+1.5,DURATION-1/60];','const stillTimes=[0,LANDING*.5,LANDING-.2,LANDING,LANDING+1.5,TRANSITION_START,TRANSITION_START+.25,TRANSITION_START+.5,TRANSITION_START+.75,CARD_START,DURATION-1/60];')
s=s.replace('order:photos.map(p=>p.number),stopTime,settledTime','order:photos.map(p=>p.number),settledTime:LANDING,transitionStart:TRANSITION_START,cardStart:CARD_START,textBounds:closing.textBounds')
s=s.replace("effect:'Pixel perimeter + Prism rays'", "effect:'Pixel + Prism with light-tunnel Finals CTA'")
s=s.replace('audioSourceStart:15-DURATION,audioSourceEnd:15,audioTempoBPM:120,audioFadeIn:.015,audioFadeOut:.25','audioSourceStart:20-DURATION,audioSourceEnd:20,audioTempoBPM:120,audioFadeIn:.015,audioEdit:\'Original Disco D master, one extra two-second bar before the closing resolution\'')
s=s.replace('three-second blue finish','blue winning celebration')
s=s.replace('celebrationSeconds:3,motionTimeScale:', "celebrationSeconds:3,transitionStart:TRANSITION_START,transitionSeconds:1,cardStart:CARD_START,cardHoldSeconds:4,ctaText:['MIT 2.009','FINALS','WATCH LIVE','DEC 7'],ctaURL:null,ctaTime:null,motionTimeScale:")
(HERE/'render.cjs').write_text(s)

source=ROOT/'outputs/MIT-2.009-Disco-Beat-Tests-2026-09-26/MIT-2.009-Disco-Space-Disco-120BPM-18s.wav'
master=OUT/'Disco-D-Finals-20s-master.wav'
# Add one whole 120 BPM bar of the winning groove before the original ending.
# Tiny two-millisecond fades at the splice prevent clicks without shifting any
# beat. Pitch, tempo, and gain stay unchanged; the original ending is retained.
filt='[0:a]asplit=2[a][b];[a]atrim=end=16,asetpts=PTS-STARTPTS,afade=t=out:st=15.998:d=0.002[p];[b]atrim=start=14:end=18,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.002[q];[p][q]concat=n=2:v=0:a=1[out]'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-filter_complex',filt,'-map','[out]','-c:a','pcm_s24le',str(master)],check=True)
for duration in [13,15,17]:
    wav=OUT/f'Disco-D-Finals-{duration}s.wav'
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(master),'-af',f'atrim=start={20-duration}:end=20,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.015','-c:a','pcm_s24le',str(wav)],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-movflags','+faststart',str(OUT/f'Disco-D-Finals-{duration}s.m4a')],check=True)
print('Prepared 13/15/17-second Finals CTA tests with identical eight-second music finishes.')
