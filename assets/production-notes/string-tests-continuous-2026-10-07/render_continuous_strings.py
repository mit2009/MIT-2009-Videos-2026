from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import math,json,subprocess,time,sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/string-tests-continuous';WORK=ROOT/'work'
SIZE=1080;SS=2;FPS=60;SECONDS=5;TAU=2*math.pi;PITCH=170.;OUTLINE=(35,31,32)
PALETTES={
 'red':((245,158,167),(236,32,41),(190,34,39)),
 'blue':((167,199,230),(32,120,186),(0,93,146)),
 'yellow':((252,242,142),(252,213,0),(191,163,47)),
 'green':((178,218,178),(20,177,75),(0,138,69)),
 'purple':((212,183,214),(145,76,157),(86,48,144)),
 'pink':((246,176,202),(237,58,128),(200,34,99)),
}
CONFIGS=[
 {'number':78,'name':'Horizontal feed','color':'red','kind':'horizontal','pitches':8,'poster':0,'description':'A red string feeds continuously from the left edge to the right edge. The diagonal bands travel steadily with the string; neither end appears.'},
 {'number':79,'name':'Upward feed','color':'blue','kind':'vertical','pitches':8,'poster':0,'description':'A blue string feeds continuously in through the bottom and out through the top. No pauses or visible ends.'},
 {'number':80,'name':'Diagonal feed','color':'yellow','kind':'diagonal','pitches':10,'poster':0,'description':'A yellow string travels continuously from the lower left to the upper right, extending beyond the frame at both ends.'},
 {'number':81,'name':'Flowing wave','color':'green','kind':'wave','pitches':10,'poster':.6,'description':'A green string keeps feeding left to right while broad waves travel along it. The string crosses both edges throughout the loop.'},
 {'number':82,'name':'Falling ripple','color':'pink','kind':'ripple','pitches':10,'poster':0,'description':'A pink string feeds continuously downward as an S-shaped ripple travels from top to bottom. Both ends stay outside the frame.'},
 {'number':83,'name':'Over the arch','color':'purple','kind':'arch','pitches':10,'poster':1.25,'description':'A purple string flows in from the left, over a gently breathing arch, and out to the right. Its shaded bands make the continuous feed visible.'},
 {'number':84,'name':'Round the corner','color':'yellow','kind':'corner','pitches':9,'poster':0,'description':'A yellow string enters from the left, turns a broad rounded corner, and feeds out through the bottom edge.'},
 {'number':85,'name':'Continuous U-turn','color':'red','kind':'uturn','pitches':12,'poster':0,'description':'A red string enters at the upper left, follows a wide U-turn, and exits at the lower left. One uninterrupted string keeps feeding around the bend.'},
 {'number':86,'name':'Three-pass flow','color':'blue','kind':'serpentine','pitches':16,'poster':0,'description':'A blue string enters from the left, follows three horizontal passes joined by rounded bends, and exits at the right. Continuous feed with no crossings.'},
]
for c in CONFIGS:
 c.update(title='String tests 2 — '+c['name'].lower(),slug='MIT-2.009-String-Continuous-'+c['name'].replace(' ','-')+'-5s',size=[1080,1080],seconds=5,fps=60,audio='Silent',added_text=False,string_count=1,continuous_feed=True)

def line(a,b,n=101):return np.linspace(a,b,n)
def arc(center,r,a,b,n=151):
 angle=np.linspace(a,b,n);return np.array(center)+r*np.column_stack([np.cos(angle),np.sin(angle)])
def join(*parts):return np.concatenate([parts[0]]+[p[1:] for p in parts[1:]])

def geometry(c,t):
 phase=TAU*((t/SECONDS)%1);kind=c['kind'];s=np.linspace(-.28,1.28,601)
 if kind=='horizontal':p=np.column_stack([s,np.full(len(s),.5)])
 elif kind=='vertical':p=np.column_stack([np.full(len(s),.5),1-s])
 elif kind=='diagonal':p=np.column_stack([s,1-s])
 elif kind=='wave':p=np.column_stack([s,.5+.185*np.sin(TAU*1.15*s-phase)])
 elif kind=='ripple':p=np.column_stack([.5+.185*np.sin(TAU*1.05*s-phase),s])
 elif kind=='arch':
  amplitude=.40+.035*math.sin(phase)
  p=np.column_stack([s,.73-amplitude*np.exp(-((s-.5)/.34)**2)])
 elif kind=='corner':
  p=join(line((-.28,.24),(.43,.24)),arc((.43,.54),.30,-math.pi/2,0),line((.73,.54),(.73,1.28)))
 elif kind=='uturn':
  p=join(line((-.28,.22),(.50,.22)),arc((.50,.50),.28,-math.pi/2,math.pi/2),line((.50,.78),(-.28,.78)))
 else:
  p=join(line((-.28,.18),(.70,.18)),arc((.70,.34),.16,-math.pi/2,math.pi/2),line((.70,.50),(.30,.50)),arc((.30,.66),.16,-math.pi/2,-3*math.pi/2),line((.30,.82),(1.28,.82)))
 return p*SIZE

def frame(c,t,ss=SS):
 bg,base,dark=PALETTES[c['color']];p=geometry(c,t)
 tangent=np.gradient(p,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None]
 normal=np.column_stack([-tangent[:,1],tangent[:,0]])
 distance=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]);length=distance[-1]
 radius=39.;edge=9.;im=Image.new('RGB',(SIZE*ss,SIZE*ss),bg);draw=ImageDraw.Draw(im)
 def poly(pts,color):draw.polygon([tuple(v) for v in pts*ss],fill=color)
 # Both endpoints stay well outside the image at every moment, so no caps or
 # hidden resets are needed. This is one continuous open path through the crop.
 for r,col in [(radius+edge,OUTLINE),(radius,base)]:poly(np.concatenate([p+normal*r,(p-normal*r)[::-1]]),col)
 # Advance the rope's markings at a constant positive arc-length speed. An
 # integer number of stripe pitches per five seconds gives an exact loop.
 # Wave motion is independent of this feed: the string never merely sways in place.
 feed_phase=((t/SECONDS)%1)*c['pitches']*PITCH
 offset=feed_phase%PITCH
 v=np.linspace(-1,1,25)
 def points(a):
  center=np.column_stack([np.interp(a,distance,p[:,0]),np.interp(a,distance,p[:,1])])
  norm=np.column_stack([np.interp(a,distance,normal[:,0]),np.interp(a,distance,normal[:,1])]);norm/=np.linalg.norm(norm,axis=1)[:,None]
  return center+norm*(v*radius)[:,None]
 for start in np.arange(offset-PITCH,length+PITCH,PITCH):
  leading=start+36*(v+.2*v*v);trailing=leading+20
  if leading.min()<0 or trailing.max()>length:continue
  poly(np.concatenate([points(leading),points(trailing)[::-1]]),dark)
 poly(np.concatenate([p+normal*(radius*.75),(p+normal*radius)[::-1]]),dark)
 if ss!=1:im=im.resize((SIZE,SIZE),Image.Resampling.LANCZOS)
 return im

def previews():
 contact=Image.new('RGB',(1080,1080))
 for i,c in enumerate(CONFIGS):
  im=frame(c,c['poster']);im.save(OUT/f"{c['number']}.jpg",quality=95)
  contact.paste(im.resize((360,360),Image.Resampling.LANCZOS),((i%3)*360,(i//3)*360))
  board=Image.new('RGB',(1440,240))
  for j,t in enumerate([0,.833,1.667,2.5,3.333,4.167]):board.paste(frame(c,t).resize((240,240)),(j*240,0))
  board.save(WORK/'string-continuous-previews'/f"{c['number']}-sequence.jpg",quality=94)
 contact.save(OUT/'Continuous-String-Tests-Overview.jpg',quality=96)
 (WORK/'continuous-string-config.json').write_text(json.dumps(CONFIGS,indent=2))

def render(c):
 dest=OUT/(c['slug']+'.mp4');start=time.time()
 cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1080','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-profile:v','baseline','-level:v','4.2','-pix_fmt','yuv420p','-bf','0','-g','120','-maxrate','12M','-bufsize','24M','-tag:v','avc1','-movflags','+faststart','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-threads','4',str(dest)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for i in range(FPS*SECONDS):proc.stdin.write(frame(c,i/FPS).tobytes())
 finally:proc.stdin.close()
 assert proc.wait()==0
 print(f"Rendered {c['number']}: {c['name']}, {dest.stat().st_size/1e6:.2f} MB, {time.time()-start:.1f}s",flush=True)

if __name__=='__main__':
 if '--preview' in sys.argv:previews()
 else:
  ids=[int(n) for n in sys.argv[1:]] or [c['number'] for c in CONFIGS]
  for c in CONFIGS:
   if c['number'] in ids:render(c)
