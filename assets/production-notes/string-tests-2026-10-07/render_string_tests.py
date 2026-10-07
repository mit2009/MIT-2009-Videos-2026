from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import math, json, subprocess, time, sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/string-tests'; WORK=ROOT/'work'
SIZE=1080; SS=2; FPS=60; SECONDS=5; TAU=2*math.pi
OUTLINE=(35,31,32)
# Exact dominant colors from the supplied Slack icons, not approximate replacements.
PALETTES={
 'red':((245,158,167),(236,32,41),(190,34,39)),
 'blue':((167,199,230),(32,120,186),(0,93,146)),
 'yellow':((252,242,142),(252,213,0),(191,163,47)),
 'green':((178,218,178),(20,177,75),(0,138,69)),
 'purple':((212,183,214),(145,76,157),(86,48,144)),
 'pink':((246,176,202),(237,58,128),(200,34,99)),
}
CONFIGS=[
 {'number':69,'name':'Horizontal glide','color':'red','kind':'horizontal','poster':0.0,'description':'One red string travels straight across the square from left to right. Rounded ends and diagonal shading follow the supplied artwork.'},
 {'number':70,'name':'Vertical rise','color':'blue','kind':'vertical','poster':0.0,'description':'One blue string rises vertically through the frame, with its shaded bands traveling with it.'},
 {'number':71,'name':'Diagonal pass','color':'yellow','kind':'diagonal','poster':0.0,'description':'One yellow string travels diagonally from the lower left to the upper right.'},
 {'number':72,'name':'Traveling wave','color':'green','kind':'wave','poster':0.6,'description':'A broad wave travels along a single green string that stretches beyond both sides of the frame.'},
 {'number':73,'name':'Standing wave','color':'purple','kind':'standing','poster':1.1,'description':'A single purple string has still ends and a moving middle. Two opposing bends pass smoothly through a straight line.'},
 {'number':74,'name':'Downward ripple','color':'pink','kind':'ripple','poster':0.0,'description':'A soft S-shaped ripple travels down a single pink string that extends beyond the top and bottom.'},
 {'number':75,'name':'Around the frame','color':'blue','kind':'perimeter','poster':0.6,'description':'One blue string follows a rounded rectangular route around the inside of the frame, turning each corner without a cut.'},
 {'number':76,'name':'Open orbit','color':'red','kind':'orbit','poster':0.0,'description':'One open red arc circles the center. The gap stays open throughout the rotation; there are no crossings or knots.'},
 {'number':77,'name':'Elastic bend','color':'green','kind':'bend','poster':2.5,'description':'One green string bends from a straight line into a deep open curve and relaxes back. Its centerline length stays constant.'},
]
for c in CONFIGS:
 c.update(title='String tests — '+c['name'].lower(),slug='MIT-2.009-String-'+c['name'].replace(' ','-')+'-5s',size=[1080,1080],seconds=5,fps=60,audio='Silent',added_text=False,string_count=1)

# Sample a rounded rectangle at uniform arc-length positions.
def round_rect(s):
 a,b,r=.14,.86,.17
 line=b-a-2*r; ar=math.pi*r/2; perimeter=4*(line+ar)
 q=np.mod(s,perimeter); x=np.zeros_like(q);y=np.zeros_like(q)
 cursor=0.
 for k in range(4):
  m=(q>=cursor)&(q<cursor+line);v=q[m]-cursor
  if k==0:x[m]=a+r+v;y[m]=a
  elif k==1:x[m]=b;y[m]=a+r+v
  elif k==2:x[m]=b-r-v;y[m]=b
  else:x[m]=a;y[m]=b-r-v
  cursor+=line
  m=(q>=cursor)&(q<cursor+ar);v=(q[m]-cursor)/r
  cx,cy=[(b-r,a+r),(b-r,b-r),(a+r,b-r),(a+r,a+r)][k]
  angle=-math.pi/2+k*math.pi/2+v
  x[m]=cx+r*np.cos(angle);y[m]=cy+r*np.sin(angle);cursor+=ar
 return np.column_stack([x,y]),perimeter


def geometry(c,t):
 u=(t/SECONDS)%1; phase=TAU*u; n=401;s=np.linspace(0,1,n);kind=c['kind'];texture=0.
 if kind in ('horizontal','vertical','diagonal'):
  # One finite string resets only when its two rounded ends are fully outside.
  q=((u+.5)%1)-.5
  if kind=='horizontal':
   x=.5+q*2.04+(s-.5)*.82;y=np.full(n,.5)
  elif kind=='vertical':
   x=np.full(n,.5);y=.5-q*2.04-(s-.5)*.82
  else:
   d=np.array([1.,-1.])/math.sqrt(2);p=np.array([.5,.5])+(q*2.60+(s-.5)*1.08)[:,None]*d
   x,y=p.T
 elif kind=='wave':
  x=np.linspace(-.18,1.18,n);y=.5+.185*np.sin(TAU*(1.32*x-u))
 elif kind=='standing':
  x=.105+.79*s;y=.5+.205*np.sin(TAU*s)*math.sin(phase)
 elif kind=='ripple':
  y=np.linspace(-.18,1.18,n);x=.5+.19*np.sin(TAU*(1.15*y-u))
 elif kind=='perimeter':
  _,perimeter=round_rect(np.array([0.]));p,_=round_rect((s*.43+u)*perimeter)
  x,y=p.T
 elif kind=='orbit':
  angle=TAU*u + (-math.pi*.77 + s*math.pi*1.54)
  x=.5+.328*np.cos(angle);y=.5+.328*np.sin(angle)
 else:
  # Arc length is .90 at every instant, including the straight limit.
  curvature=1.75*(1-math.cos(phase));angle=curvature*(s-.5)
  if curvature<1e-7:x=.9*(s-.5);y=np.zeros(n)
  else:x=.9/curvature*np.sin(angle);y=.9/curvature*(1-np.cos(angle))
  y-=float((y.min()+y.max())/2)
  rot=.20*math.sin(phase);x,y=x*math.cos(rot)-y*math.sin(rot),x*math.sin(rot)+y*math.cos(rot)
  x+=.5;y+=.5
 p=np.column_stack([x,y])*SIZE
 # Texture is attached to the normalized material coordinate. It bends with the
 # string, so markings do not flicker when the centerline changes length.
 return p


def frame(c,t,ss=SS):
 bg,base,dark=PALETTES[c['color']];p=geometry(c,t)
 tangent=np.gradient(p,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None]
 normal=np.column_stack([-tangent[:,1],tangent[:,0]])
 n=len(p);material=np.linspace(0,1,n)
 width=78. if c['kind'] not in ['perimeter','orbit'] else 72.
 radius=width/2;edge=9.
 im=Image.new('RGB',(SIZE*ss,SIZE*ss),bg);draw=ImageDraw.Draw(im)
 def poly(pts,color):draw.polygon([tuple(v) for v in pts*ss],fill=color)
 def circle(pos,r,color):
  x,y=pos*ss;rr=r*ss;draw.ellipse((x-rr,y-rr,x+rr,y+rr),fill=color)
 for r,col in [(radius+edge,OUTLINE),(radius,base)]:
  poly(np.concatenate([p+normal*r,(p-normal*r)[::-1]]),col)
  circle(p[0],r,col);circle(p[-1],r,col)
 # Broad, curved diagonal bands echo the straight ropes in slack_icons-07.
 # Each stripe stays inside the tube; a curved trailing edge avoids a ruler-flat look.
 pitch=.175 if c['kind'] in ['perimeter','orbit'] else .17
 # Longer paths receive more bands, with stable material positions over time.
 nominal={'horizontal':.82,'vertical':.82,'diagonal':1.08,'wave':1.75,'standing':1.05,'ripple':1.72,'perimeter':1.12,'orbit':1.59,'bend':.9}[c['kind']]*SIZE
 pitch=170/nominal; band=20/nominal;slant=36/nominal
 v=np.linspace(-1,1,25)
 for start in np.arange(-pitch,1+pitch,pitch):
  leading=start+slant*(v+.20*v*v)
  trailing=leading+band
  if leading.min()<.018 or trailing.max()>.982:continue
  def points(a,v):
   center=np.column_stack([np.interp(a,material,p[:,0]),np.interp(a,material,p[:,1])])
   norm=np.column_stack([np.interp(a,material,normal[:,0]),np.interp(a,material,normal[:,1])]);norm/=np.linalg.norm(norm,axis=1)[:,None]
   return center+norm*(v*radius)[:,None]
  poly(np.concatenate([points(leading,v),points(trailing,v)[::-1]]),dark)
 # A narrow darker side, continuous around bends, adds the same flat dimensionality
 # seen in the knot references. Keep the center bright rather than using gradients.
 side_inner=p+normal*(radius*.75);side_outer=p+normal*radius
 poly(np.concatenate([side_inner,side_outer[::-1]]),dark)
 if ss!=1:im=im.resize((SIZE,SIZE),Image.Resampling.LANCZOS)
 return im


def previews():
 contact=Image.new('RGB',(1080,1080),(255,255,255))
 for i,c in enumerate(CONFIGS):
  im=frame(c,c['poster']);im.save(OUT/f"{c['number']}.jpg",quality=95)
  contact.paste(im.resize((360,360),Image.Resampling.LANCZOS),((i%3)*360,(i//3)*360))
  board=Image.new('RGB',(1440,240))
  for j,t in enumerate([0,.833,1.667,2.5,3.333,4.167]):board.paste(frame(c,t).resize((240,240)),(j*240,0))
  board.save(WORK/'string-previews'/f"{c['number']}-sequence.jpg",quality=94)
 contact.save(OUT/'String-Tests-Overview.jpg',quality=96)
 (WORK/'string-config.json').write_text(json.dumps(CONFIGS,indent=2))


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
