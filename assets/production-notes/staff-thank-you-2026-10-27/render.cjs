const fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const {once}=require('node:events');
const {createCanvas,loadImage}=require('@napi-rs/canvas');
const args=Object.fromEntries(process.argv.slice(2).map(x=>x.replace(/^--/,'').split('=')));
const ROOT=__dirname,OUT=path.resolve(ROOT,'../../outputs/MIT-2.009-Staff-Thank-You-2026-10-27');
const W=1920,H=1080,FPS=60,TILE=900,INTERVAL=2.75,INTRO=3.5,OUTRO=4.5;
const seq=JSON.parse(fs.readFileSync(path.join(ROOT,'sequence.json'))),N=seq.photos.length;
const END=INTRO+N*INTERVAL,DURATION=END+OUTRO;
// Five visual beats per portrait, approximately 109 BPM. The music can set
// the final timing later; no audio is included in this proof of concept.
const BEAT=INTERVAL/5;
const colors=['#49E2A1','#B68AFF','#FF6576','#4CC4FF','#FFDB58','#FF9BD4'];
const clamp=x=>Math.max(0,Math.min(1,x));
const smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
const mod=(x,n)=>((x%n)+n)%n;
const alpha=(hex,a)=>hex+Math.round(clamp(a)*255).toString(16).padStart(2,'0');
const mix=(a,b,u)=>'#'+[1,3,5].map(k=>Math.round(parseInt(a.slice(k,k+2),16)*(1-u)+parseInt(b.slice(k,k+2),16)*u).toString(16).padStart(2,'0')).join('');
const canvas=createCanvas(W,H),ctx=canvas.getContext('2d');
const glowSprites=colors.map(c=>{
 const s=createCanvas(160,160),g=s.getContext('2d'),grad=g.createRadialGradient(80,80,0,80,80,80);
 grad.addColorStop(0,alpha(c,.8));grad.addColorStop(.15,alpha(c,.4));grad.addColorStop(.5,alpha(c,.09));grad.addColorStop(1,alpha(c,0));
 g.fillStyle=grad;g.fillRect(0,0,160,160);return s;
});
function glow(x,y,size,index,power){ctx.save();ctx.globalCompositeOperation='screen';ctx.globalAlpha=power;ctx.drawImage(glowSprites[mod(index,6)],x-size/2,y-size/2,size,size);ctx.restore();}
function line(x1,y1,x2,y2,color,width,a){ctx.strokeStyle=alpha(color,a);ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();}
const R=5000,D=700,F=D*760/TILE,CY=560;
function surface(x){const dx=(x-W/2)/F,a=1+dx*dx,k=R+D;const z=(k-Math.sqrt(k*k-a*(k*k-R*R)))/a;return{arc:Math.atan2(dx*z,k-z)*R,height:TILE*F/z};}
const strips=[];
for(let x=0;x<W;x+=4){const a=surface(x),b=surface(Math.min(W,x+4)),m=surface(x+2);strips.push({x,arc:a.arc,sw:b.arc-a.arc,height:m.height});}
function background(t){
 const g=ctx.createLinearGradient(0,0,W,H);g.addColorStop(0,'#071427');g.addColorStop(.5,'#040A15');g.addColorStop(1,'#151027');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
 const beat=mod(t/BEAT,1),pulse=Math.exp(-beat*5),bar=Math.floor(t/INTERVAL);
 glow(240,110,1100,bar,.22+pulse*.08);glow(1690,990,1300,bar+3,.26+pulse*.1);
 // Pixel Party perimeter, adapted to a widescreen stage.
 for(let y=24;y<H;y+=30)for(let x=25;x<W;x+=30){
  if(x>90&&x<W-90&&y>190&&y<H-190)continue;
  const dist=Math.hypot((x-W/2)*.7,y-H/2),wave=Math.pow(.5+.5*Math.sin(dist/95-t*3.5),5);
  const ci=mod(Math.floor(x/240)+Math.floor(y/180)+bar,6),p=.08+.22*wave+.19*pulse;
  ctx.fillStyle=alpha(colors[ci],p);ctx.beginPath();ctx.roundRect(x,y,10,10,2);ctx.fill();
 }
 // The Prism rays rotate slowly. The photo ribbon is drawn above them.
 for(let k=0;k<60;k++){
  const a=k*Math.PI/30+t*.025,inner=350+50*Math.sin(t*.8+k),outer=1500;
  const p=.08+.19*pulse+.07*Math.pow(.5+.5*Math.sin(t*2+k*.4),2);
  line(W/2+Math.cos(a)*inner,CY+Math.sin(a)*inner,W/2+Math.cos(a)*outer,CY+Math.sin(a)*outer,colors[(k+bar)%6],k%5===0?4:1.7,p);
 }
}
let tiles=[];
function carousel(t){
 const p=(t-INTRO)/INTERVAL-.5;
 for(const s of strips){
  let u=TILE/2+s.arc-p*TILE;
  const raw=Math.floor(u/TILE),index=-raw;
  if(index<0||index>=N)continue;
  const sx=mod(u,TILE),sw=Math.min(s.sw,TILE-sx);
  ctx.drawImage(tiles[index],sx,0,sw,TILE,s.x,CY-s.height/2,4*sw/s.sw+.35,s.height);
  if(sw<s.sw&&index>0)ctx.drawImage(tiles[index-1],0,0,s.sw-sw,TILE,s.x+4*sw/s.sw,CY-s.height/2,4*(s.sw-sw)/s.sw+.35,s.height);
 }
 // The restrained curved rails keep the photographs joined as one carousel.
 const palettePosition=Math.max(0,(t-INTRO)/INTERVAL),pi=Math.floor(palettePosition),color=mix(colors[pi%6],colors[(pi+1)%6],smooth(palettePosition-pi));
 const pulse=Math.exp(-mod(t/BEAT,1)*5);
 for(const side of [-1,1]){
  ctx.beginPath();for(let x=0;x<=W;x+=8){const y=CY+side*(surface(x).height/2+7);if(x===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}
  ctx.strokeStyle=alpha(color,.3+pulse*.3);ctx.lineWidth=2;ctx.stroke();
  for(let j=0;j<10;j++){
   const x=mod(t*220+j*W/10,W),y=CY+side*(surface(x).height/2+9);
   glow(x,y,80,pi%6,.35+pulse*.28);
   ctx.fillStyle=alpha(color,.65);ctx.fillRect(x-3,y-3,6,6);
  }
 }
 // Gentle vignette at the far edges, leaving each center portrait untreated.
 const vignette=ctx.createLinearGradient(0,0,W,0);vignette.addColorStop(0,'#040A1550');vignette.addColorStop(.2,'#040A1500');vignette.addColorStop(.8,'#040A1500');vignette.addColorStop(1,'#040A1550');ctx.fillStyle=vignette;ctx.fillRect(0,160,W,810);
 ctx.textAlign='center';ctx.fillStyle='#F7FAFF';ctx.font='600 40px Arial';ctx.fillText('THANK YOU, 2.009 STAFF',W/2,101);
 ctx.fillStyle='#B6C9E0';ctx.font='22px Arial';ctx.fillText('MIT 2.009  ·  FINALS 2026',W/2,1030);
}
function title(t,closing){
 ctx.textAlign='center';
 ctx.fillStyle='#BBD1EA';ctx.font='500 30px Arial';ctx.fillText('MIT 2.009  /  FINALS 2026',W/2,346);
 ctx.fillStyle='#FAFCFF';ctx.font='bold 150px Arial';ctx.fillText('THANK YOU',W/2,535);
 ctx.font='48px Arial';ctx.fillStyle='#E3ECF8';ctx.fillText(closing?'To our extraordinary staff.':'To the people who make it possible.',W/2,624);
 const length=closing?510:380,start=(W-length)/2;
 for(let i=0;i<6;i++){ctx.fillStyle=colors[i];ctx.beginPath();ctx.roundRect(start+i*length/6,698,length/6-8,7,3);ctx.fill();}
}
function frame(t){
 background(t);
 const photoOpacity=smooth((t-(INTRO-.55))/.55)*(1-smooth((t-(END-.6))/.6));
 if(photoOpacity>0){ctx.save();ctx.globalAlpha=photoOpacity;carousel(Math.max(INTRO,Math.min(END,t)));ctx.restore();}
 if(t<INTRO){ctx.save();ctx.globalAlpha=(1-smooth((t-(INTRO-.7))/.7))*smooth(t/.65);title(t,false);ctx.restore();}
 if(t>END-.15){ctx.save();ctx.globalAlpha=smooth((t-(END-.15))/.7);title(t,true);ctx.restore();}
 // A brief light rush marks the closing thank-you, without flashing the faces.
 if(t>END-.2&&t<END+.8){const u=clamp((t-END+.2)),power=Math.sin(u*Math.PI)*.6;for(let k=0;k<36;k++){const a=k*Math.PI/18,r=360+u*1200;line(W/2+Math.cos(a)*r,CY+Math.sin(a)*r,W/2+Math.cos(a)*(r+240),CY+Math.sin(a)*(r+240),colors[k%6],3,power);}}
 const fade=1-smooth((t-(DURATION-.65))/.65);if(fade<1){ctx.fillStyle=alpha('#040A15',1-fade);ctx.fillRect(0,0,W,H);}
}
(async()=>{
 fs.mkdirSync(OUT,{recursive:true});
 for(const photo of seq.photos)tiles.push(await loadImage(path.join(ROOT,photo.tile)));
 if(args.stills){for(const t of [1.5,3.5,4.875,7.625,10.375,13.125,15.875,18.625,21.375,24.125,26.875,29.625,32.375,34.5,37.25]){frame(t);fs.writeFileSync(path.join(ROOT,`review/frame-${t}.jpg`),canvas.toBuffer('image/jpeg'));}console.log('Stills rendered');return;}
 const seconds=args.preview?8:DURATION,offset=args.preview?3.5:0,frames=Math.round(seconds*FPS);
 const dest=path.join(OUT,args.preview?'preview.mp4':`MIT-2.009-Staff-Thank-You-Carousel-Test-38s.mp4`);
 const log=fs.openSync(path.join(ROOT,args.preview?'preview-encode.log':'encode.log'),'w');
 const ff=spawn('/opt/homebrew/bin/ffmpeg',['-hide_banner','-y','-f','rawvideo','-pix_fmt','rgba','-s',`${W}x${H}`,'-r',String(FPS),'-i','pipe:0','-an','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,setsar=1,format=yuv420p','-c:v','libx264','-preset','fast','-crf','18','-threads','6','-profile:v','high','-level:v','4.2','-g','120','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart','-frames:v',String(frames),'-metadata','title=MIT 2.009 Staff Thank You — Carousel Test',dest],{stdio:['pipe','ignore',log]});
 const finished=once(ff,'close'),started=Date.now();ff.stdin.on('error',e=>{if(e.code!=='EPIPE')throw e;});
 for(let i=0;i<frames;i++){
  frame(i/FPS+offset);const data=Buffer.from(ctx.getImageData(0,0,W,H).data.buffer);
  if(!ff.stdin.write(data))await once(ff.stdin,'drain');
  if(i%300===0)console.log(JSON.stringify({frames:i,total:frames,elapsedSeconds:Math.round((Date.now()-started)/1000)}));
 }
 ff.stdin.end();const[code]=await finished;if(code!==0)throw Error('Encoding failed: '+code);
 console.log(JSON.stringify({complete:dest,seconds,bytes:fs.statSync(dest).size}));
})();
