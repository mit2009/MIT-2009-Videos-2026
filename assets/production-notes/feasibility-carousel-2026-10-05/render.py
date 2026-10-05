"""Render submitted slides on the continuous curved lecture carousel."""
import argparse,functools,hashlib,json,math,subprocess,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'render-deps'))
import cv2
import numpy as np
from PIL import Image
cv2.setNumThreads(3)
W,H,FPS=1920,1080,60
TW,TH=1920,1080
SECONDS=3
OUT=BASE.parent.parent/'outputs/MIT-2.009-Feasibility-Carousel-2026-10-05'
class Renderer:
 def __init__(self):
  self.manifest=json.loads((BASE/'sequence.json').read_text())
  self.slides=self.manifest['slides'];self.count=len(self.slides);self.frames=self.count*SECONDS*FPS
  self.radius=4200.;self.distance=1000.;self.focal=self.distance*920/TH
  x=(np.arange(W,dtype=np.float64)+.5-W/2)/self.focal
  a=1+x*x;center=self.radius+self.distance
  disc=center*center-a*(center*center-self.radius*self.radius)
  assert disc.min()>0
  depth=(center-np.sqrt(disc))/a
  arc=np.arctan2(x*depth,center-depth)*self.radius
  self.origin=TW/2+float(arc.min())
  self.width=math.ceil(float(arc.max()-arc.min()))+4
  map_y=((np.arange(H,dtype=np.float32)[:,None]+.5-H/2)*depth[None,:]/self.focal+TH/2-.5).astype('float32')
  self.maps=[];self.start_offsets=[]
  for phase_fraction in range(3):
   start=self.origin-phase_fraction/3
   whole=math.floor(start);fraction=start-whole
   map_x=np.broadcast_to(arc[None,:]-arc.min()+fraction-.5,(H,W)).astype('float32').copy()
   self.maps.append(cv2.convertMaps(map_x,map_y,cv2.CV_16SC2))
   self.start_offsets.append(whole)
  self.canvas=np.empty((TH,self.width,3),dtype=np.uint8)
 @functools.lru_cache(maxsize=8)
 def tile(self,index):
  record=self.slides[index]
  path=BASE/record['image']
  assert hashlib.sha256(path.read_bytes()).hexdigest()==record['image_sha256']
  im=cv2.imread(str(path))
  assert im is not None
  # Submitted pages vary by only rounding at the PDF boundary (1080/1081).
  # Scale uniformly and pad the subpixel rounding instead of cropping content.
  height,width=im.shape[:2];scale=min(TW/width,TH/height)
  rw,rh=round(width*scale),round(height*scale)
  resized=cv2.resize(im,(rw,rh),interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC)
  tile=np.full((TH,TW,3),255,dtype=np.uint8)
  tile[(TH-rh)//2:(TH-rh)//2+rh,(TW-rw)//2:(TW-rw)//2+rw]=resized
  return tile
 def frame(self,n):
  n=n%self.frames
  whole_phase,fraction_phase=divmod(n*32,3)
  start=self.start_offsets[fraction_phase]-whole_phase
  tile_index,offset=divmod(start,TW);written=0
  while written<self.width:
   length=min(TW-offset,self.width-written)
   self.canvas[:,written:written+length]=self.tile((-tile_index)%self.count)[:,offset:offset+length]
   written+=length;tile_index+=1;offset=0
  map1,map2=self.maps[fraction_phase]
  return cv2.remap(self.canvas,map1,map2,cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT,borderValue=(21,17,15))
def encode(renderer,path,frames):
 path.parent.mkdir(parents=True,exist_ok=True)
 cmd=['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1920x1080','-r','60','-i','-','-an','-vf','scale=out_color_matrix=bt709:out_range=tv','-c:v','libx264','-preset','fast','-crf','19','-threads','6','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart','-frames:v',str(frames),str(path)]
 start=time.monotonic()
 with path.with_suffix('.render.log').open('w') as log:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for n in range(frames):
    p.stdin.write(renderer.frame(n).tobytes())
    if n and n%3600==0:print(json.dumps({'seconds_done':n/FPS,'total_seconds':frames/FPS,'elapsed_seconds':round(time.monotonic()-start)}),flush=True)
  finally:p.stdin.close()
  assert p.wait()==0
 print(json.dumps({'complete':str(path),'bytes':path.stat().st_size,'render_seconds':round(time.monotonic()-start,1)}),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--stills',action='store_true');p.add_argument('--preview',action='store_true');args=p.parse_args()
 r=Renderer();review=BASE/'review';review.mkdir(exist_ok=True)
 if args.stills:
  for seconds in [0,1.5,3,120,273,387,480,576,684,687]:
   cv2.imwrite(str(review/f'carousel-{seconds:g}s.jpg'),r.frame(round(seconds*FPS)),[cv2.IMWRITE_JPEG_QUALITY,95])
  assert np.array_equal(r.frame(0),r.frame(r.frames))
  start=time.monotonic()
  for n in range(180):r.frame(n)
  print(json.dumps({'frames_per_second':round(180/(time.monotonic()-start),1),'loop_exact':True}),flush=True)
 else:
  output=review/'preview.mp4' if args.preview else OUT/f'MIT-2.009-Feasibility-Curved-Carousel-{r.count}-Slides-{r.count*3}s.mp4'
  encode(r,output,600 if args.preview else r.frames)
