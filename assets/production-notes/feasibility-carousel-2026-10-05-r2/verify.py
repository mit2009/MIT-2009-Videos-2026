"""Check every submitted slide's appearance and timing in the final encode."""
import hashlib,json,struct,subprocess
from pathlib import Path
from render import BASE,OUT,Renderer,cv2,np,FPS
r=Renderer();path=OUT/'MIT-2.009-Feasibility-Curved-Carousel-HD.mp4'
probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))
streams=probe['streams'];assert len(streams)==1 and streams[0]['codec_type']=='video'
v=streams[0];assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',r.frames)
assert v['pix_fmt']=='yuv420p' and v['codec_name']=='h264' and v['color_space']=='bt709'
assert float(probe['format']['duration'])==r.count*3
# Inspect MP4 structure without scanning through media payload.
boxes=[]
with path.open('rb') as f:
 while f.tell()<path.stat().st_size:
  at=f.tell();head=f.read(8);size,typ=struct.unpack('>I4s',head)
  if size==1:size=struct.unpack('>Q',f.read(8))[0]
  if size==0:size=path.stat().st_size-at
  boxes.append(typ.decode('ascii'));f.seek(at+size)
assert boxes.index('moov')<boxes.index('mdat')
# Fully decode the entire export, selecting each center-crossing frame.
cmd=['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-xerror','-threads','4','-i',str(path),'-vf','select=not(mod(n\\,180)),scale=320:180','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','bgr24','-']
errors=BASE/'review/decode-errors.log';scores=[]
with errors.open('w') as log:
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=log)
 for i,slide in enumerate(r.slides):
  data=p.stdout.read(320*180*3);assert len(data)==320*180*3,(i,len(data))
  actual=np.frombuffer(data,dtype=np.uint8).reshape(180,320,3)
  expected=cv2.resize(r.frame(i*180),(320,180),interpolation=cv2.INTER_AREA)
  error=float(np.abs(actual.astype('float32')-expected).mean());assert error<8,(i,error)
  scores.append(error)
 assert p.stdout.read()==b''
 assert p.wait()==0
assert errors.stat().st_size==0
# Inspect both sides of each independently encoded join.
join_errors=[]
for frame_number in [179,180,33479,33480,r.frames-1]:
 data=subprocess.check_output(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-ss',str(frame_number/60),'-i',str(path),'-frames:v','1','-vf','scale=320:180','-f','rawvideo','-pix_fmt','bgr24','-'])
 actual=np.frombuffer(data,dtype=np.uint8).reshape(180,320,3)
 expected=cv2.resize(r.frame(frame_number),(320,180),interpolation=cv2.INTER_AREA)
 error=float(np.abs(actual.astype('float32')-expected).mean());assert error<8,(frame_number,error)
 join_errors.append({'frame':frame_number,'error':error})
assert np.array_equal(r.frame(0),r.frame(r.frames))
# All page identities are unique; internal presentation builds remain distinct.
assert len({(s['source_pdf'],s['source_page']) for s in r.slides})==229
colors=r.manifest['team_order']
by_color={c:[s for s in r.slides if s['color']==c] for c in colors}
for c,rows in by_color.items():
 pages=[s['source_page'] for s in rows]
 unique=sorted(set(pages));expected=[unique[i%len(unique)] for i in range(len(pages))]
 assert pages==expected,(c,pages)
if r.manifest['rotation_mode']=='repeat':
 assert [s['color'] for s in r.slides]==colors*(r.count//6)
else:
 expected=[c for round_index in range(max(r.manifest['team_counts'].values())) for c in colors if round_index<r.manifest['team_counts'][c]]
 assert [s['color'] for s in r.slides]==expected
# Measure the actual direction of on-screen features, independently of ordering.
a=cv2.cvtColor(r.frame(30),cv2.COLOR_BGR2GRAY);b=cv2.cvtColor(r.frame(36),cv2.COLOR_BGR2GRAY)
pts=cv2.goodFeaturesToTrack(a,maxCorners=80,qualityLevel=.08,minDistance=12)
tracked,status,_=cv2.calcOpticalFlowPyrLK(a,b,pts,None)
delta=(tracked-pts)[status.reshape(-1).astype(bool),0,:]
motion=float(np.median(delta[:,0]));assert motion<0
assert [s['center_time_seconds'] for s in r.slides]==list(range(0,r.count*3,3))
digest=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
result={'file':path.name,'sha256':digest,'bytes':path.stat().st_size,'duration_seconds':r.count*3,'frames':r.frames,'fps':FPS,'width':1920,'height':1080,'silent':True,'fast_start':True,'loop_exact':True,'all_center_crossings_checked':len(scores),'max_small_frame_mean_absolute_error':max(scores),'mean_small_frame_mean_absolute_error':sum(scores)/len(scores),'team_counts':r.manifest['team_counts'],'team_order':r.manifest['team_order'],'seconds_per_slide':3,'full_decode_errors':0,'revision':2,'rotation_mode':r.manifest['rotation_mode'],'motion_direction':'right to left','measured_horizontal_motion_px':motion,'forward_page_order':True,'unique_slides':229,'join_checks':join_errors}
(BASE/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
