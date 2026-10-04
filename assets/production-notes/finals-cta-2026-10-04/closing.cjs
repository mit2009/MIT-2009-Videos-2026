const {createCanvas,GlobalFonts}=require('/Users/dannygoldfield/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@napi-rs/canvas');
const path=require('node:path');
const W=1080,H=1920,CX=540,CY=960;
const clamp=x=>Math.max(0,Math.min(1,x));
const smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
const colors=['#FFD62A','#FF4A62','#41E297','#FF89C7','#39B6FF','#B37BFF'];
const fontDir=path.resolve(__dirname,'../studio-brand-2026/Outfit/static');
for(const [file,name] of [['Outfit-ExtraBold.ttf','FinalsHeavy'],['Outfit-SemiBold.ttf','FinalsMedium']]){
  if(!GlobalFonts.registerFromPath(path.join(fontDir,file),name))throw Error('Could not load '+file);
}
function createClosing(){
  const snapshot=createCanvas(W,H),sc=snapshot.getContext('2d');
  const card=createCanvas(W,H),c=card.getContext('2d');
  const bg=c.createRadialGradient(CX,900,70,CX,900,1250);
  bg.addColorStop(0,'#123951');bg.addColorStop(.47,'#061a2f');bg.addColorStop(1,'#020812');
  c.fillStyle=bg;c.fillRect(0,0,W,H);
  // Quiet perimeter lights frame the card without competing with the message.
  for(let y=200;y<1680;y+=31)for(let x=55;x<1040;x+=31){
    if(x>112&&x<968&&y>390&&y<1505)continue;
    c.globalAlpha=.12+.16*(.5+.5*Math.sin(x*.007+y*.014));
    c.fillStyle=colors[(Math.floor(x/220)+Math.floor(y/250))%6];
    c.beginPath();c.roundRect(x,y,9,9,2);c.fill();
  }
  c.globalAlpha=1;
  c.strokeStyle='#4b9dc757';c.lineWidth=2;c.beginPath();c.roundRect(108,394,864,1090,46);c.stroke();
  c.strokeStyle='#82cfff16';c.lineWidth=1;c.beginPath();c.roundRect(92,378,896,1122,55);c.stroke();
  for(let k=0;k<6;k++){
    c.fillStyle=colors[k];c.beginPath();c.roundRect(336+k*70,474,57,7,3.5);c.fill();
  }
  const background=createCanvas(W,H);background.getContext('2d').drawImage(card,0,0);
  const textBounds=[];
  function text(label,y,size,font,color){
    c.font=`${size}px ${font}`;c.fillStyle=color;c.textAlign='center';c.textBaseline='alphabetic';
    const m=c.measureText(label);if(m.width>810)throw Error('CTA text exceeds safe width: '+label);
    c.fillText(label,CX,y);textBounds.push({label,x:CX-m.width/2,width:m.width,y,size});
  }
  text('MIT 2.009',614,67,'FinalsMedium','#b5dcf3');
  text('FINALS',838,190,'FinalsHeavy','#f4faff');
  c.strokeStyle='#71ceff69';c.lineWidth=2;c.beginPath();c.moveTo(303,916);c.lineTo(777,916);c.stroke();
  text('WATCH LIVE',1066,70,'FinalsMedium','#8dd7ff');
  text('DEC 7',1282,176,'FinalsHeavy','#f4faff');
  // The final four seconds are a fully static card, including all text.
  function draw(ctx,t,start,end){
    if(t<start)return;
    if(t>=end){ctx.drawImage(card,0,0);return;}
    const p=clamp((t-start)/(end-start));
    sc.clearRect(0,0,W,H);sc.drawImage(ctx.canvas,0,0);
    ctx.drawImage(background,0,0);
    ctx.save();
    const portraitAlpha=1-smooth((p-.12)/.58),zoom=1+.95*p*p;
    ctx.globalAlpha=portraitAlpha;
    ctx.translate(CX,CY);ctx.scale(zoom,zoom);ctx.drawImage(snapshot,-CX,-CY);ctx.restore();
    // Accelerating radial trails move outward as a virtual camera rushes
    // through the light field. The portrait is never geometrically warped.
    const power=Math.sin(Math.PI*p)**.7;
    ctx.save();ctx.globalCompositeOperation='screen';ctx.lineCap='round';
    for(let k=0;k<64;k++){
      const angle=k*Math.PI/32+.035*Math.sin(k*1.31),lane=(k%7)/7;
      const advance=(p*p*2.2+lane)%1;
      const r0=70+advance*750,r1=r0+150+430*p;
      const alpha=power*(.28+.52*(1-advance));
      const g=ctx.createLinearGradient(CX+Math.cos(angle)*r0,CY+Math.sin(angle)*r0,CX+Math.cos(angle)*r1,CY+Math.sin(angle)*r1);
      g.addColorStop(0,'#66c6ff00');g.addColorStop(.68,k%5?'#65caff':'#d6f5ff');g.addColorStop(1,'#66c6ff00');
      ctx.strokeStyle=g;ctx.globalAlpha=alpha;ctx.lineWidth=k%5?2.4:6;
      ctx.beginPath();ctx.moveTo(CX+Math.cos(angle)*r0,CY+Math.sin(angle)*r0);ctx.lineTo(CX+Math.cos(angle)*r1,CY+Math.sin(angle)*r1);ctx.stroke();
    }
    ctx.restore();
    // The destination grows toward the viewer and becomes still before its
    // four-second reading hold begins. No white flash obscures the text.
    const reveal=smooth((p-.48)/.52);
    if(reveal>0){
      ctx.save();ctx.globalAlpha=reveal;ctx.translate(CX,CY);
      const scale=.86+.14*reveal;ctx.scale(scale,scale);ctx.drawImage(card,-CX,-CY);ctx.restore();
    }
  }
  return{draw,card,textBounds};
}
module.exports={createClosing};
