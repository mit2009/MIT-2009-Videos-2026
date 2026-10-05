"""Encode the ordering-dependent ends and assemble the shared HD middle."""
import json,subprocess
from render import BASE,OUT,Renderer,encode,FPS
r=Renderer();assert r.manifest['rotation_mode'] in ['once','repeat']
review=BASE/'review';middle=review/'common-middle-3s-558s.mp4';assert middle.exists()
encode(r,review/'intro.mp4',3*FPS)
encode(r,review/'ending.mp4',r.frames-558*FPS,start_frame=558*FPS)
# Matching codec, dimensions, frame rate, time base and color metadata allow
# lossless concatenation. No frame is repeated at either join.
listing=review/'segments.txt'
listing.write_text("file 'intro.mp4'\nfile 'common-middle-3s-558s.mp4'\nfile 'ending.mp4'\n")
output=OUT/'MIT-2.009-Feasibility-Curved-Carousel-HD.mp4';output.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-an','-c','copy','-movflags','+faststart',str(output)],check=True)
print(json.dumps({'assembled':str(output),'bytes':output.stat().st_size,'seconds':r.count*3}),flush=True)
