from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw
import numpy as np
import math,json,subprocess,time,sys
import render_connect_photos as base
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/connect-rope-exit-tests';WORK=ROOT/'work'
SIZE=1080;FPS=60;SECONDS=30;JOIN=.5;EXIT=.5
PHOTO_IDS=base.PHOTO_IDS;PHOTO_FILES=base.PHOTO_FILES;CROPS=base.CROPS;photo=base.photo
CONFIGS=[
 {'number':90,'name':'Rope drops away','slug':'MIT-2.009-Connect-Rope-Drops-Away-30s','kind':'drop','description':'The photo halves connect, then the pink rope drops downward with an accelerating fall. Its rounded free end travels down and clears the bottom edge. Each clean photograph holds for two seconds.'},
 {'number':91,'name':'Rope pulled upward','slug':'MIT-2.009-Connect-Rope-Pulled-Upward-30s','kind':'pull','description':'The photo halves connect, then the pink rope tightens and is pulled upward. Its rounded trailing end follows it out through the top edge. Each clean photograph holds for two seconds.'},
]
for c in CONFIGS:c.update(title='Connect photo tests — '+c['name'].lower(),size=[1080,1080],seconds=30,fps=60,audio='Silent',added_text=False,photo_count=10,photo_ids=PHOTO_IDS,assembly_seconds=JOIN,rope_exit_seconds=EXIT,hold_seconds=2)

@lru_cache(10)
def frozen_rope(scene):
 t=scene*3+JOIN;p=base.seam_points(t)
 distance=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
 # The two physical ends start beyond the crop. They become visible as the
 # connected rope leaves, rather than deleting the rope with an opacity fade.
 keep=(p[:,1]>=-.14*SIZE)&(p[:,1]<=1.14*SIZE)
 return p[keep].copy(),distance[keep].copy(),(((t/5)%1)*1700)%170

def exit_geometry(c,scene,q):
 p,material,phase=frozen_rope(scene);p=p.copy();s=np.linspace(0,1,len(p))
 if c['kind']=='drop':
  distance=SIZE*1.27*q*q
  p[:,1]+=distance
  # Small slack flutter as the string falls. The upper free end leads the reveal.
  p[:,0]+=SIZE*.022*math.sin(math.pi*q)*np.sin(2*math.pi*(s-q))
 else:
  distance=SIZE*1.27*(.25*q+.75*q*q)
  anchor=np.interp(0,p[:,1],p[:,0]);tighten=.78*float(base.ease(min(1,q*1.25)))
  p[:,0]=anchor+(p[:,0]-anchor)*(1-tighten)
  # A slight flick follows the free lower tail; it never changes opacity.
  p[:,0]+=SIZE*.035*(s**4)*math.sin(2*math.pi*q)*math.sin(math.pi*q)
  p[:,1]-=distance
 return p,material,phase

def exit_layer(c,scene,q):
 p,material,phase=exit_geometry(c,scene,q);tan=np.gradient(p,axis=0);tan/=np.linalg.norm(tan,axis=1)[:,None];normal=np.column_stack([-tan[:,1],tan[:,0]])
 im=Image.new('RGBA',(SIZE*2,SIZE*2),(0,0,0,0));d=ImageDraw.Draw(im)
 def poly(points,color):d.polygon([tuple(p) for p in points*2],fill=color+(255,))
 def circle(point,r,color):
  x,y=point*2;r*=2;d.ellipse((x-r,y-r,x+r,y+r),fill=color+(255,))
 for r,color in [(48,(35,31,32)),(39,(237,58,128))]:
  poly(np.r_[p+normal*r,(p-normal*r)[::-1]],color)
  circle(p[0],r,color);circle(p[-1],r,color)
 v=np.linspace(-1,1,25)
 def pts(a):
  center=np.column_stack([np.interp(a,material,p[:,0]),np.interp(a,material,p[:,1])]);norm=np.column_stack([np.interp(a,material,normal[:,0]),np.interp(a,material,normal[:,1])]);norm/=np.linalg.norm(norm,axis=1)[:,None]
  return center+norm*(39*v)[:,None]
 for start in np.arange(phase-170,material[-1]+170,170):
  leading=start+36*(v+.2*v*v);trailing=leading+20
  if leading.min()<material[0]+40 or trailing.max()>material[-1]-40:continue
  poly(np.r_[pts(leading),pts(trailing)[::-1]],(200,34,99))
 poly(np.r_[p+normal*29.25,(p+normal*39)[::-1]],(200,34,99))
 return im.resize((SIZE,SIZE),Image.Resampling.LANCZOS)

def frame(c,t):
 t=t%SECONDS;scene=int(t//3);local=t-scene*3
 if local>=1:return photo(scene).copy()
 if local<JOIN:
  im=photo(scene-1).copy();target=photo(scene);left,right=base.pieces(t)
  a,b=base.motion({'kind':'together'},scene,local/JOIN)
  im.paste(target,a,left);im.paste(target,b,right)
  rope=base.string_layer(t);im.paste(rope,a,rope);im.paste(rope,b,rope)
  return im
 im=photo(scene).copy();rope=exit_layer(c,scene,(local-JOIN)/EXIT);im.paste(rope,(0,0),rope)
 return im

def previews():
 sheet=Image.new('RGB',(2160,720))
 for row,c in enumerate(CONFIGS):
  for col,t in enumerate([.26,.50,.64,.76,.89,1.3]):sheet.paste(frame(c,t).resize((360,360)),(col*360,row*360))
  frame(c,.86 if c['kind']=='drop' else .80).save(OUT/f"{c['number']}.jpg",quality=94)
 sheet.save(WORK/'rope-exit-previews/two-exits.jpg',quality=94)
 (WORK/'rope-exit-config.json').write_text(json.dumps(CONFIGS,indent=2))

def render(c):
 dest=OUT/(c['slug']+'.mp4');start=time.time()
 cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1080','-r','60','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-profile:v','baseline','-level:v','4.2','-pix_fmt','yuv420p','-bf','0','-g','120','-maxrate','12M','-bufsize','24M','-tag:v','avc1','-movflags','+faststart','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-threads','4',str(dest)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for i in range(FPS*SECONDS):
   proc.stdin.write(frame(c,i/FPS).tobytes())
   if i%360==0:print(f"{c['number']}: {i/FPS:.0f}s of 30s",flush=True)
 finally:proc.stdin.close()
 assert proc.wait()==0
 print(f"Rendered {c['number']}: {dest.stat().st_size/1e6:.1f} MB in {time.time()-start:.1f}s",flush=True)

if __name__=='__main__':
 if '--preview' in sys.argv:previews()
 else:
  for c in CONFIGS:render(c)
