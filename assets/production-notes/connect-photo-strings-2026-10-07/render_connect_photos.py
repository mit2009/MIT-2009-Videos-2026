from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageOps,ImageDraw
import numpy as np
import math,json,subprocess,time,sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/connect-photo-string-tests';WORK=ROOT/'work'
SIZE=1080;FPS=60;SECONDS=30;TAU=2*math.pi
PHOTO_IDS=['1498','0898','0670','1021','1196','1149','1491','1596','1527','1628']
PHOTO_FILES={p.stem.split('-')[-1]:p for p in (WORK/'photos/26-09-29-Theme-Balloon-3x2').glob('*.jpg')}
CROPS={'1196':(.38,.5),'1498':(.5,.5),'1628':(.5,.5)}
CONFIGS=[
 {'number':87,'name':'Together','slug':'MIT-2.009-Connect-Photo-String-Together-30s','kind':'together','description':'Ten theme-balloon photographs connect from two complementary halves. Both sides glide in together along moving pink string edges. The string disappears at the join, followed by a two-second clean photo hold.'},
 {'number':88,'name':'Alternating lead','slug':'MIT-2.009-Connect-Photo-String-Alternating-Lead-30s','kind':'lead','description':'The same ten photographs join along moving string edges. One half leads and the other catches up, alternating left and right with each photo. The completed photograph holds for two seconds with the string gone.'},
 {'number':89,'name':'Floating join','slug':'MIT-2.009-Connect-Photo-String-Floating-Join-30s','kind':'float','description':'The same ten photographs arrive as two pieces drifting from opposite sides and slightly different heights. Their moving string edges align and disappear, leaving each connected photo still for two seconds.'},
]
for c in CONFIGS:c.update(title='Connect photo tests — '+c['name'].lower(),size=[1080,1080],seconds=30,fps=60,audio='Silent',added_text=False,photo_count=10,photo_ids=PHOTO_IDS,assembly_seconds=1,hold_seconds=2)

def ease(t):
 t=np.clip(t,0,1);return t*t*t*(t*(t*6-15)+10)
@lru_cache(10)
def photo(i):
 key=PHOTO_IDS[i%10];im=ImageOps.exif_transpose(Image.open(PHOTO_FILES[key])).convert('RGB')
 return ImageOps.fit(im,(SIZE,SIZE),Image.Resampling.LANCZOS,centering=CROPS.get(key,(.5,.5)))

def motion(c,scene,u):
 travel=SIZE*.74
 if c['kind']=='lead':
  # A difference in approach speed, but a shared connection time.
  a=1-(1-u)**1.48;b=u**1.48
  ql,qr=(a,b) if scene%2==0 else (b,a)
  return (-round(travel*(1-ease(ql))),0),(round(travel*(1-ease(qr))),0)
 progress=ease(u);dx=round(travel*(1-progress))
 if c['kind']=='float':
  dy=round(145*(1-progress)*math.sin(math.pi*u));sign=1 if scene%2==0 else -1
  return (-dx,sign*dy),(dx,-sign*dy)
 return (-dx,0),(dx,0)

def seam_points(t):
 # Identical centerline, palette, outline, and feed speed to the supplied
 # Falling Ripple video (its bytes match the earlier source export).
 y=np.linspace(-.28,1.28,601);phase=TAU*((t/5)%1)
 return np.column_stack([.5+.185*np.sin(TAU*1.05*y-phase),y])*SIZE

def pieces(t):
 # Split a single crop into exactly complementary halves at the moving seam.
 ys=np.arange(SIZE,dtype=float);xs=SIZE*(.5+.185*np.sin(TAU*1.05*(ys/SIZE)-TAU*((t/5)%1)))
 # Pixel-area coverage provides smooth subpixel edges with no missing column.
 coverage=np.clip(xs[:,None]-np.arange(SIZE)[None,:]+.5,0,1)
 left=np.rint(coverage*255).astype(np.uint8);right=255-left
 return Image.fromarray(left),Image.fromarray(right)

def string_layer(t):
 p=seam_points(t);tan=np.gradient(p,axis=0);tan/=np.linalg.norm(tan,axis=1)[:,None];normal=np.column_stack([-tan[:,1],tan[:,0]])
 distance=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];length=distance[-1]
 im=Image.new('RGBA',(SIZE*2,SIZE*2),(0,0,0,0));d=ImageDraw.Draw(im)
 def poly(points,color):d.polygon([tuple(p) for p in points*2],fill=color+(255,))
 for r,color in [(48,(35,31,32)),(39,(237,58,128))]:poly(np.r_[p+normal*r,(p-normal*r)[::-1]],color)
 v=np.linspace(-1,1,25)
 def pts(a):
  center=np.column_stack([np.interp(a,distance,p[:,0]),np.interp(a,distance,p[:,1])]);norm=np.column_stack([np.interp(a,distance,normal[:,0]),np.interp(a,distance,normal[:,1])]);norm/=np.linalg.norm(norm,axis=1)[:,None]
  return center+norm*(39*v)[:,None]
 phase=(((t/5)%1)*10*170)%170
 for start in np.arange(phase-170,length+170,170):
  leading=start+36*(v+.2*v*v);trailing=leading+20
  if leading.min()<0 or trailing.max()>length:continue
  poly(np.r_[pts(leading),pts(trailing)[::-1]],(200,34,99))
 poly(np.r_[p+normal*29.25,(p+normal*39)[::-1]],(200,34,99))
 return im.resize((SIZE,SIZE),Image.Resampling.LANCZOS)

def frame(c,t):
 t=t%SECONDS;scene=int(t//3);u=t-scene*3
 if u>=1:return photo(scene).copy()
 im=photo(scene-1).copy();target=photo(scene);left,right=pieces(t);a,b=motion(c,scene,u)
 im.paste(target,a,left);im.paste(target,b,right)
 rope=string_layer(t)
 # Each half carries a moving string edge. Both edges become one seam at
 # contact; the layer is removed entirely for the following 120 hold frames.
 im.paste(rope,a,rope);im.paste(rope,b,rope)
 return im

def previews():
 sheet=Image.new('RGB',(1800,1080))
 for row,c in enumerate(CONFIGS):
  for col,t in enumerate([.18,.38,.60,.83,1.35]):sheet.paste(frame(c,t).resize((360,360)),(col*360,row*360))
  frame(c,.6).save(OUT/f"{c['number']}.jpg",quality=94)
 sheet.save(WORK/'connect-photo-previews/three-joins.jpg',quality=94)
 photos=Image.new('RGB',(1800,720))
 for i in range(10):photos.paste(photo(i).resize((360,360)),((i%5)*360,(i//5)*360))
 photos.save(OUT/'Ten-Selected-Photos.jpg',quality=94)
 (WORK/'connect-photo-config.json').write_text(json.dumps(CONFIGS,indent=2))
 # Retain transparent reference layer as an intermediate, not an altered photo.
 string_layer(1.2).save(WORK/'connect-photo-previews/string-no-background.png')

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
