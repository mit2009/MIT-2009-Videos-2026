const {createCanvas}=require('/Users/dannygoldfield/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@napi-rs/canvas');
const W=1080,H=1920,CX=540,CY=960;
const teamColors=['#FFD62A','#FF4A62','#41E297','#FF89C7','#39B6FF','#B37BFF'];
const blueColors=['#369ADD','#57C7FF','#2388E6','#8CDAFF','#39B6FF','#64B4F8'];
const clamp=x=>Math.max(0,Math.min(1,x));
const smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
const hex=(color,a)=>color+Math.round(clamp(a)*255).toString(16).padStart(2,'0');
const frac=x=>x-Math.floor(x);
function rnd(seed){return()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};}
const sprites=new Map();
function blend(a,b,u){
  return '#'+[1,3,5].map(i=>Math.round(parseInt(a.slice(i,i+2),16)*(1-u)+parseInt(b.slice(i,i+2),16)*u).toString(16).padStart(2,'0')).join('');
}
function accentColors(t){
  const phase=Math.min(Math.max(0,t),9)/3;
  return teamColors.map((_,i)=>{
    const p=phase+i,whole=Math.floor(p),color=blend(teamColors[whole%6],teamColors[(whole+1)%6],smooth(frac(p)));
    return blend(color,blueColors[i],smooth((t-9)/3));
  });
}
function glow(ctx,x,y,size,color,alpha=1){
  // Quantize glow tint only; thin light cores retain smoothly interpolated color.
  color='#'+[1,3,5].map(i=>Math.min(255,Math.round(parseInt(color.slice(i,i+2),16)/8)*8).toString(16).padStart(2,'0')).join('');
  if(!sprites.has(color)){
    if(sprites.size>=128)sprites.delete(sprites.keys().next().value);
    const c=createCanvas(128,128),g=c.getContext('2d'),r=g.createRadialGradient(64,64,0,64,64,64);
    r.addColorStop(0,hex(color,.85));r.addColorStop(.12,hex(color,.55));r.addColorStop(.4,hex(color,.17));r.addColorStop(1,hex(color,0));
    g.fillStyle=r;g.fillRect(0,0,128,128);sprites.set(color,c);
  }
  ctx.save();ctx.globalAlpha=alpha;ctx.globalCompositeOperation='screen';ctx.drawImage(sprites.get(color),x-size/2,y-size/2,size,size);ctx.restore();
}
function line(ctx,points,color,width=3,alpha=1){
  ctx.save();ctx.globalAlpha=alpha;ctx.strokeStyle=color;ctx.lineWidth=width;ctx.lineJoin='round';ctx.lineCap='round';ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.stroke();ctx.restore();
}
function rr(ctx,x,y,w,h,r,color,width,alpha=1){
  ctx.save();ctx.globalAlpha=alpha;ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.stroke();ctx.restore();
}
function dot(ctx,x,y,color,power=1,size=7){
  glow(ctx,x,y,size*7,color,power*.6);ctx.fillStyle=hex(color,.15+.8*power);ctx.beginPath();ctx.roundRect(x-size/2,y-size/2,size,size,size*.25);ctx.fill();
  if(power>.55){ctx.fillStyle=hex('#FFFFFF',(power-.55)*.8);ctx.fillRect(x-size*.16,y-size*.16,size*.32,size*.32);}
}
function edgePoint(u,x,y,w,h){
  let d=frac(u)*2*(w+h);if(d<w)return[x+d,y];d-=w;if(d<h)return[x+w,y+d];d-=h;if(d<w)return[x+w-d,y+h];return[x,y+h-(d-w)];
}
function createLights(mode, landing=12){
  let colors=accentColors(0);
  const bg=createCanvas(W,H),b=bg.getContext('2d');
  const base=b.createLinearGradient(0,0,W,H);base.addColorStop(0,'#071A2D');base.addColorStop(.5,'#030B15');base.addColorStop(1,'#081D36');b.fillStyle=base;b.fillRect(0,0,W,H);
  const main=mode==='neon'?'#2D95F4':mode==='prism'?'#286DC2':mode==='orbit'?'#42BDFF':'#2387DD';
  glow(b,150,100,800,main,.4);glow(b,950,1810,850,main,.3);
  // Narrow polished metal housing, a screen inset, and an always-dark center.
  const chrome=b.createLinearGradient(65,0,1015,0);[['0','#151a29'],['.03','#8293a7'],['.05','#27303c'],['.5','#060a12'],['.95','#344250'],['.975','#64798b'],['1','#151b28']].forEach(([p,c])=>chrome.addColorStop(+p,c));
  b.fillStyle=chrome;b.beginPath();b.roundRect(72,176,936,1568,58);b.fill();
  b.fillStyle='#02050c';b.beginPath();b.roundRect(98,196,884,1528,37);b.fill();
  rr(b,102,200,876,1520,34,'#8297ac',1,.38);
  if(mode==='neon'){
    for(const sign of [-1,1])for(let k=0;k<3;k++){
      const x=CX+sign*(473+k*22);
      line(b,[[x,115],[x,490],[x-sign*16,525],[x-sign*16,1370],[x,1410],[x,1805]],k%2?'#4A8FFF':'#43DFFD',3,.3);
    }
    for(const y of [110,1810])line(b,[[215,y+35],[260,y],[820,y],[865,y+35]],'#678ca2',2,.5);
  }else if(mode==='prism'){
    for(let k=0;k<6;k++){
      const c='#31506b',x=173+k*126;b.fillStyle=hex(c,.27);b.beginPath();b.moveTo(x,105);b.lineTo(x+55,56);b.lineTo(x+110,105);b.lineTo(x+55,154);b.closePath();b.fill();
      line(b,[[x,105],[x+55,56],[x+110,105],[x+55,154],[x,105]],c,2,.7);
      line(b,[[x,1815],[x+55,1766],[x+110,1815],[x+55,1864],[x,1815]],c,2,.7);
    }
  }else if(mode==='orbit'){
    for(const y of [95,1825]){b.strokeStyle='#57b2de';b.lineWidth=1;b.beginPath();b.ellipse(CX,y,290,44,0,0,Math.PI*2);b.stroke();}
    for(let i=0;i<22;i++){const x=60+(i*173)%960,y=50+(i*421)%1820;b.fillStyle='#779fbd';b.fillRect(x,y,2,2);}
  }else{
    for(let y=55;y<H-40;y+=28)for(let x=34;x<W-20;x+=28){
      if(x>80&&x<1000&&y>162&&y<1758)continue;b.fillStyle='#1b2438';b.beginPath();b.roundRect(x,y,15,15,3);b.fill();
    }
  }
  const random=rnd(912009),sparkles=Array.from({length:90},()=>({angle:random()*Math.PI*2,r:455+random()*460,phase:random(),size:2+random()*5,colorIndex:Math.floor(random()*6)}));
  function back(ctx,t,win){ctx.drawImage(bg,0,0);}
  function front(ctx,t,win){
    colors=accentColors(Math.min(12,t*12/landing));
    const power=smooth(win/.45),u=Math.max(0,win),speed=power?1:0.25;
    const shade=ctx.createLinearGradient(0,196,0,1724);shade.addColorStop(0,'#02050ceb');shade.addColorStop(.17,'#02050c45');shade.addColorStop(.29,'#02050c00');shade.addColorStop(.71,'#02050c00');shade.addColorStop(.83,'#02050c45');shade.addColorStop(1,'#02050ceb');ctx.fillStyle=shade;ctx.fillRect(100,196,880,1528);
    // Thin glass reflections leave the face unfiltered and readable.
    rr(ctx,106,204,868,1512,31,'#a5c9e4',1,.2);
    if(mode==='neon'){
      const c=[colors[4],colors[3]];
      for(let side=0;side<2;side++)for(let row=0;row<48;row++){
        const x=side?1022:58,y=235+row*31;
        const phase=frac(row/16-t*(.5+power*.75)+side*.4),p=.12+(.28+.6*power)*Math.exp(-(((phase-.5)/.20)**2));
        dot(ctx,x,y,c[(Math.floor(row/8)+side)%2],p,11);
      }
      for(let lane=0;lane<4;lane++){
        const col=power?colors[(lane+Math.floor(u*1.5))%6]:c[lane%2];
        const inset=lane*11;rr(ctx,92-inset,190-inset,896+inset*2,1540+inset*2,42+inset,col,2,.18+.25*power);
        for(let k=0;k<4;k++){
          const pts=Array.from({length:13},(_,i)=>edgePoint(t*(.11+lane*.011)+k/4+i*.002,92-inset,190-inset,896+inset*2,1540+inset*2));
          line(ctx,pts,col,5,.4+.6*power);const [x,y]=pts.at(-1);glow(ctx,x,y,85,col,.4+.5*power);
        }
      }
      if(power)for(let n=0;n<5;n++){const v=frac(u*.6+n/5),r=430+v*290;rr(ctx,CX-r,CY-r,r*2,r*2,28+v*90,colors[n],4,(1-v)*.75*power);}
    }else if(mode==='prism'){
      for(let k=0;k<6;k++){
        const p=.22+(.32+.46*power)*(.5+.5*Math.sin(t*Math.PI*3-k*Math.PI/3))**2;
        const c=colors[k],x=228+k*126;
        for(const y of [105,1815]){ctx.fillStyle=hex(c,.35);ctx.beginPath();ctx.moveTo(x-55,y);ctx.lineTo(x,y-49);ctx.lineTo(x+55,y);ctx.lineTo(x,y+49);ctx.closePath();ctx.fill();line(ctx,[[x-55,y],[x,y-49],[x+55,y],[x,y+49],[x-55,y]],c,2,.7);}
        glow(ctx,x,105,170,c,p);glow(ctx,x,1815,170,c,p);
        for(let side=0;side<2;side++)for(let j=0;j<7;j++)dot(ctx,side?1032:48,250+k*238+j*27,c,p,13);
        const inset=k*8;rr(ctx,97-inset,200-inset,886+2*inset,1520+2*inset,36+inset,c,4,p*.45);
      }
      if(power){
        // Six-color rays stop outside the portrait; no full-frame light flashes.
        ctx.save();ctx.beginPath();ctx.rect(0,0,W,H);ctx.rect(108,528,864,864);ctx.clip('evenodd');
        for(let k=0;k<48;k++){
          const a=k*Math.PI/24+u*.10,p=.28+.5*(.5+.5*Math.sin(u*Math.PI*3-k*.4))**3;
          line(ctx,[[CX+Math.cos(a)*450,CY+Math.sin(a)*450],[CX+Math.cos(a)*1100,CY+Math.sin(a)*1100]],colors[k%6],k%3?3:9,p*power);
        }ctx.restore();
      }
    }else if(mode==='orbit'){
      const cs=[colors[4],colors[5],colors[3]];
      for(let n=0;n<3;n++){
        rr(ctx,86-n*11,190-n*11,908+n*22,1540+n*22,48,cs[n],2,.28);
        for(let j=0;j<5;j++){const [x,y]=edgePoint(t*(n%2?-.085:.095)*(1+power)+j/5+n*.1,86-n*11,190-n*11,908+n*22,1540+n*22);glow(ctx,x,y,100,cs[n],.4+.5*power);dot(ctx,x,y,cs[n],.9,8);}
      }
      if(power){
        ctx.save();ctx.beginPath();ctx.rect(0,0,W,H);ctx.rect(110,530,860,860);ctx.clip('evenodd');
        for(let n=0;n<6;n++){
          const r=475+n*30+8*Math.sin(u*1.2+n),ang=u*(n%2?-.7:.8)+n;
          ctx.strokeStyle=hex(colors[n],(.55+.25*Math.sin(u*2+n))*power);ctx.lineWidth=4+n%3*2;
          for(let s=0;s<3;s++){ctx.beginPath();ctx.arc(CX,CY,r,ang+s*Math.PI*2/3,ang+s*Math.PI*2/3+1.18);ctx.stroke();const a=ang+s*Math.PI*2/3+1.18;glow(ctx,CX+Math.cos(a)*r,CY+Math.sin(a)*r,100,colors[n],power);}
        }ctx.restore();
        for(const s of sparkles){const a=s.angle+u*.1,r=s.r+Math.sin(u+s.phase*9)*24,x=CX+Math.cos(a)*r,y=CY+Math.sin(a)*r;if(x>106&&x<974&&y>532&&y<1388)continue;const p=(.5+.5*Math.sin(u*6+s.phase*30))**6;dot(ctx,x,y,colors[s.colorIndex],p*power,s.size);}
      }
    }else{
      for(let y=55;y<H-40;y+=28)for(let x=34;x<W-20;x+=28){
        if(x>80&&x<1000&&y>162&&y<1758)continue;
        const radius=Math.hypot((x-CX)*.9,(y-CY)*.7),phase=frac(radius/290-t*(.45+power*.7));
        const p=.10+(.27+.63*power)*Math.exp(-(((phase-.5)/.22)**2));
        const col=colors[((Math.floor(x/170)+Math.floor(y/210)+Math.floor(t*.8))%6+6)%6];dot(ctx,x+7,y+7,col,p,13);
      }
      if(power){
        // Six-color rays stop outside the portrait; no full-frame light flashes.
        ctx.save();ctx.beginPath();ctx.rect(0,0,W,H);ctx.rect(108,528,864,864);ctx.clip('evenodd');
        for(let k=0;k<48;k++){
          const a=k*Math.PI/24+u*.10,p=.28+.5*(.5+.5*Math.sin(u*Math.PI*3-k*.4))**3;
          line(ctx,[[CX+Math.cos(a)*450,CY+Math.sin(a)*450],[CX+Math.cos(a)*1100,CY+Math.sin(a)*1100]],colors[k%6],k%3?3:9,p*power);
        }ctx.restore();
      }
    }
    if(power){
      const p=.45+.55*(.5+.5*Math.sin(u*Math.PI*3))**2;
      const winnerColor=colors[4];
      rr(ctx,109,529,862,862,24,winnerColor,5,p*power);
      for(const [x,y] of [[110,530],[970,530],[110,1390],[970,1390]])glow(ctx,x,y,130,winnerColor,p*power*.8);
    }
    // Small digital pointers always identify the one winning row.
    for(const sign of [-1,1]){const x=CX+sign*457;ctx.fillStyle=power?'#eef8ff':'#7293a6';ctx.beginPath();ctx.moveTo(x-sign*11,CY);ctx.lineTo(x+sign*5,CY-13);ctx.lineTo(x+sign*5,CY+13);ctx.closePath();ctx.fill();}
  }
  return{back,front,colors};
}
module.exports={createLights,accentColors};
