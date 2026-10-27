const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const sharp=require('sharp');
const {createCanvas,loadImage}=require('@napi-rs/canvas');
(async()=>{
 const source=path.join(__dirname,'input/26-10-27-Staff-Thank-You-Test');
 const files=fs.readdirSync(source).filter(x=>/\.jpg$/i.test(x)).sort();
 if(files.length!==11)throw Error('Expected 11 supplied photos');
 fs.mkdirSync(path.join(__dirname,'tiles'),{recursive:true});
 const c=createCanvas(1320,3*365),g=c.getContext('2d');g.fillStyle='#111827';g.fillRect(0,0,c.width,c.height);
 const records=[];
 for(let i=0;i<files.length;i++){
  const full=path.join(source,files[i]),buf=fs.readFileSync(full),meta=await sharp(buf).metadata();
  const dest=path.join(__dirname,`tiles/${String(i+1).padStart(2,'0')}.png`);
  await sharp(buf).rotate().toColourspace('srgb').resize(900,900,{fit:'contain',background:'#070d18'}).png().toFile(dest);
  const im=await loadImage(dest),x=(i%4)*330,y=Math.floor(i/4)*365;
  g.drawImage(im,x+10,y+10,310,310);g.fillStyle='white';g.font='15px Arial';g.fillText(`${i+1}. ${files[i]}`,x+10,y+343);
  records.push({number:i+1,filename:files[i],width:meta.width,height:meta.height,sha256:crypto.createHash('sha256').update(buf).digest('hex'),tile:`tiles/${String(i+1).padStart(2,'0')}.png`});
 }
 fs.writeFileSync(path.join(__dirname,'review/contact-sheet.jpg'),c.toBuffer('image/jpeg'));
 fs.writeFileSync(path.join(__dirname,'sequence.json'),JSON.stringify({sourceArchive:'26-10-27-Staff-Thank-You-Test.zip',photos:records},null,2)+'\n');
 console.log(JSON.stringify(records.map(({number,filename,width,height})=>({number,filename,width,height}))));
})();
