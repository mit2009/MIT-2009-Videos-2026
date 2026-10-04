const fs = require('node:fs');
const path = require('node:path');
const {spawn} = require('node:child_process');
const {once} = require('node:events');
const {createHash} = require('node:crypto');
const {createCanvas, loadImage} = require('/Users/dannygoldfield/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@napi-rs/canvas');

const args=Object.fromEntries(process.argv.slice(2).map(s=>s.replace(/^--/,'').split('=')));
const mode='pixel';
const retainNeighbors=true;
if(!['neon','prism','orbit','pixel'].includes(mode))throw Error('Unknown digital variant');
const W=1080,H=1920,FPS=60,S=848,STEP=876,PAD=0,CY=960,DURATION=Number(args.duration||15);
if(![13,15,17].includes(DURATION))throw Error('Choose 13, 15, or 17 seconds');
const LANDING=DURATION-8,TRANSITION_START=DURATION-5,CARD_START=DURATION-4;
const cfg={intro:.2,accel:.6,cruise:5.3,decel:5.2,settle:.7,overshoot:.09};
const stopTime=cfg.intro+cfg.accel+cfg.cruise+cfg.decel,settledTime=stopTime+cfg.settle;
const celebrationAt=LANDING;
const TARGET=88;
const palette=[
  {team:'Yellow',hex:'#F5CE19'}, {team:'Red',hex:'#E8414A'},
  {team:'Green',hex:'#38AA6A'}, {team:'Pink',hex:'#F184B6'},
  {team:'Blue',hex:'#348DDB'}, {team:'Purple',hex:'#955BCD'}
];
function random(seed){return()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};}
const rng=random(20092026);
const inventory=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../headshot-slot-reel-2026-09-26/headshots.json')));
const winner=inventory.photos.find(p=>p.number===TARGET);
if(!winner||inventory.photos.length!==108)throw Error('Check the approved headshot inventory');
const groups=Object.fromEntries(palette.map(c=>[c.team,inventory.photos.filter(p=>p.team===c.team&&p.number!==TARGET).map(p=>({p,key:rng()})).sort((a,b)=>a.key-b.key).map(x=>x.p).slice(0,c.team===winner.team?8:9)]));
const photos=[];
while(Object.values(groups).some(g=>g.length)){
  const last=photos.at(-1)?.team;
  const choices=Object.entries(groups).filter(([team,g])=>g.length&&team!==last).map(([team,g])=>({team,score:g.length+rng()*4})).sort((a,b)=>b.score-a.score);
  if(!choices.length)throw Error('Mixing exhausted other colors');
  photos.push(groups[choices[0].team].shift());
}
if(photos.at(-1).team===winner.team){
  const last=photos.length-1;
  const swap=photos.findIndex((p,i)=>i>0&&i<last-1&&p.team!==winner.team&&p.team!==photos[last-1].team&&photos[i-1].team!==winner.team&&photos[i+1].team!==winner.team);
  if(swap<0)throw Error('Cannot arrange final color');
  [photos[swap],photos[last]]=[photos[last],photos[swap]];
}
photos.push(winner);
if(photos[0].team===photos.at(-2).team){
  const swap=photos.findIndex((p,i)=>i>1&&i<photos.length-2&&p.team!==photos.at(-2).team&&p.team!==winner.team&&p.team!==photos[1].team&&photos[i-1].team!==photos[0].team&&photos[i+1].team!==photos[0].team);
  if(swap>=0)[photos[0],photos[swap]]=[photos[swap],photos[0]];
}
if(new Set(photos.map(p=>p.number)).size!==54||photos.some((p,i)=>i&&p.team===photos[i-1].team))throw Error('Headshots must be unique and adjacent colors different');
if(photos.some(p=>p.number===60))throw Error('Removed photo must remain excluded');
for(const p of photos){if(createHash('sha256').update(fs.readFileSync(p.source)).digest('hex')!==p.sha256)throw Error('Source changed: '+p.filename);}

const distance=photos.length-1;
const peakSpeed=(distance+cfg.overshoot)/(.5*cfg.accel+cfg.cruise+cfg.decel/4);
const clamp=x=>Math.max(0,Math.min(1,x));
const smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
const ease=x=>1-(1-clamp(x))**3;
function originalPosition(t){
  t-=cfg.intro;if(t<=0)return 0;
  if(t<cfg.accel)return peakSpeed*(t/2-cfg.accel*Math.sin(Math.PI*t/cfg.accel)/(2*Math.PI));
  t-=cfg.accel;const a=peakSpeed*cfg.accel/2;
  if(t<cfg.cruise)return a+peakSpeed*t;
  t-=cfg.cruise;
  if(t<cfg.decel){const u=t/cfg.decel;const base=a+peakSpeed*cfg.cruise+peakSpeed*cfg.decel/4*(1-(1-u)**4);const hesitation=.023*Math.exp(-(((u-.70)/.10)**2))*Math.sin((u-.70)*28);return base+hesitation;}
  t-=cfg.decel;
  if(t<cfg.settle){const knots=[[0,.09],[.18,-.030],[.39,.010],[.53,-.002],[.7,0]];for(let k=1;k<knots.length;k++){if(t<=knots[k][0]){const [ta,ya]=knots[k-1],[tb,yb]=knots[k];return distance+ya+(yb-ya)*smooth((t-ta)/(tb-ta));}}}
  return distance;
}

function position(t){return originalPosition(t*12/LANDING);}
const OUT=path.resolve(__dirname,'../../outputs/MIT-2.009-Finals-CTA-Tests-2026-10-04');
const REVIEW=path.join(__dirname,'review',String(DURATION));
fs.mkdirSync(OUT,{recursive:true});fs.mkdirSync(REVIEW,{recursive:true});
const names={neon:'Neon-Circuit',prism:'Prism-Jackpot',orbit:'Orbit',pixel:'Pixel-Party'};
const slug=`MIT-2.009-Finals-Light-Tunnel-${DURATION}s`;
const AUDIO=path.join(OUT,`Disco-D-Finals-${DURATION}s.m4a`);
const {createLights}=require('./lights.cjs');
const lights=createLights(mode,LANDING);
const {createClosing}=require('./closing.cjs');
const closing=createClosing();
(async()=>{
  const tiles=[];
  for(const p of photos){
    const img=await loadImage(p.source);
    if(img.width!==img.height)throw Error('Expected square image');
    const tile=createCanvas(S,S),c=tile.getContext('2d');c.beginPath();c.roundRect(0,0,S,S,19);c.clip();c.imageSmoothingQuality='high';c.drawImage(img,0,0,S,S);tiles.push(tile);
  }
  const canvas=createCanvas(W,H),ctx=canvas.getContext('2d');
  const motion=createCanvas(W,H),mctx=motion.getContext('2d');
  const sample=createCanvas(W,H),sctx=sample.getContext('2d');
  function reel(dest,t){
    dest.clearRect(0,0,W,H);const pos=position(t);
    for(let j=Math.floor(pos)-2;j<=Math.ceil(pos)+2;j++){
      const y=CY+(pos-j)*STEP-S/2;if(y>H||y+S<0)continue;
      dest.drawImage(tiles[((j%tiles.length)+tiles.length)%tiles.length],(W-S)/2,y);
    }
  }
  function frame(t){
    if(t>=CARD_START){closing.draw(ctx,t,TRANSITION_START,CARD_START);return;}
    lights.back(ctx,t,t-celebrationAt);
    mctx.clearRect(0,0,W,H);
    const speed=Math.abs(position(t+1/120)-position(Math.max(0,t-1/120)))*60;
    const samples=speed>2?3:1;mctx.globalCompositeOperation='lighter';mctx.globalAlpha=1/samples;
    for(let k=0;k<samples;k++){
      const offset=samples===1?0:((k+.5)/samples-.5)/FPS*.32;
      reel(sctx,Math.max(0,t+offset));mctx.drawImage(sample,0,0);
    }
    mctx.globalCompositeOperation='source-over';mctx.globalAlpha=1;
    ctx.save();ctx.beginPath();ctx.roundRect(105,202,870,1516,32);ctx.clip();ctx.drawImage(motion,0,0);ctx.restore();
    lights.front(ctx,t,t-celebrationAt);
    closing.draw(ctx,t,TRANSITION_START,CARD_START);
  }
  const stillTimes=[0,LANDING*.5,LANDING-.2,LANDING,LANDING+1.5,TRANSITION_START,TRANSITION_START+.25,TRANSITION_START+.5,TRANSITION_START+.75,CARD_START,DURATION-1/60];
  if(args.stills==='true'){
    for(const t of stillTimes){frame(t);fs.writeFileSync(path.join(REVIEW,`${mode}-${t.toFixed(2)}.jpg`),canvas.toBuffer('image/jpeg'));}
    console.log(JSON.stringify({mode,count:photos.length,order:photos.map(p=>p.number),settledTime:LANDING,transitionStart:TRANSITION_START,cardStart:CARD_START,textBounds:closing.textBounds}));return;
  }
  const frames=DURATION*FPS;
  const log=fs.openSync(path.join(__dirname,slug+'.log'),'w');
  const ff=spawn('/opt/homebrew/bin/ffmpeg',['-hide_banner','-y','-f','rawvideo','-pixel_format','rgba','-video_size',`${W}x${H}`,'-framerate',String(FPS),'-i','pipe:0','-i',AUDIO,'-map','0:v:0','-map','1:a:0','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,setsar=1,format=yuv420p','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-profile:v','high','-level:v','4.2','-maxrate','20M','-bufsize','40M','-g','120','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','copy','-t',String(DURATION),'-frames:v',String(frames),'-movflags','+faststart',path.join(OUT,slug+'.mp4')],{stdio:['pipe','ignore',log]});
  const finished=once(ff,'close');ff.stdin.on('error',e=>{if(e.code!=='EPIPE')throw e;});
  for(let f=0;f<frames;f++){
    frame(f/FPS);
    if(f===Math.round((LANDING+1.5)*FPS))fs.writeFileSync(path.join(OUT,DURATION+'s-poster.jpg'),canvas.toBuffer('image/jpeg'));
    const data=Buffer.from(ctx.getImageData(0,0,W,H).data.buffer);
    if(!ff.stdin.write(data))await once(ff.stdin,'drain');
    if(f%180===0)console.log(`${mode}: ${f}/${frames} frames`);
  }
  ff.stdin.end();const[code]=await finished;if(code!==0)throw Error('FFmpeg exited '+code);
  fs.writeFileSync(path.join(OUT,DURATION+'s-details.json'),JSON.stringify({file:slug+'.mp4',effect:'Pixel + Prism with light-tunnel Finals CTA',retainNeighbors:true,seconds:DURATION,width:W,height:H,fps:FPS,audio:'Disco D — Space Disco',audioSource:AUDIO,audioUnchanged:false,audioSourceStart:20-DURATION,audioSourceEnd:20,audioTempoBPM:120,audioFadeIn:.015,audioEdit:'Original Disco D master, one extra two-second bar before the closing resolution',background:'Blue glow; original photographs unchanged',accents:'Pixel Party perimeter; original team-color transition retimed to the landing; Prism Jackpot rays during the blue winning celebration',target:TARGET,count:photos.length,availableHeadshots:inventory.photos.length,stopTime:stopTime*LANDING/12,settledTime:LANDING,celebrationAt,celebrationSeconds:3,transitionStart:TRANSITION_START,transitionSeconds:1,cardStart:CARD_START,cardHoldSeconds:4,ctaText:['MIT 2.009','FINALS','WATCH LIVE','DEC 7'],ctaURL:null,ctaTime:null,motionTimeScale:12/LANDING,style:'Modern digital slot display; LED chases and localized 1.5 Hz winning pulses, no full-frame strobes',palette,photos:photos.map(p=>({number:p.number,team:p.team,filename:p.filename,sha256:p.sha256}))},null,2));
  console.log('FINISHED '+path.join(OUT,slug+'.mp4'));
})().catch(e=>{console.error(e);process.exitCode=1;});
