"""Restore two embedded GIF illustrations omitted by slide-to-PDF export."""
import hashlib,io,json,zipfile
from pathlib import Path
from PIL import Image
BASE=Path(__file__).resolve().parent
z=zipfile.ZipFile(BASE/'source/Feasilbility Student Feedback Forms 2026.pptx')
gif=Image.open(io.BytesIO(z.read('ppt/media/image5.gif')));gif.seek(171)
frame=gif.convert('RGB')
# Exact picture placement from slides 6 and 11, in 9144000 × 5143500 EMU.
box=(3584850,1405725,5006952,2816402)
manifest=json.loads((BASE/'sequence.json').read_text())
for record in manifest['slides']:
 if record['color']!='Yellow' or record['source_page'] not in [6,11]:continue
 path=BASE/record['image']
 with Image.open(path) as src:im=src.convert('RGB')
 x,y,w,h=box
 x,y,w,h=round(x*im.width/9144000),round(y*im.height/5143500),round(w*im.width/9144000),round(h*im.height/5143500)
 # Keep the original outline around the image area.
 inset=4
 im.paste(frame.resize((w-2*inset,h-2*inset),Image.Resampling.LANCZOS),(x+inset,y+inset))
 im.save(path)
 record['image_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
 record['animation_still']={'embedded_asset':'ppt/media/image5.gif','frame':171,'total_frames':428,'reason':'PDF conversion omitted the embedded GIF. Restore a representative original CAD frame in its original picture rectangle.'}
manifest['selection_notes'].append('Two Yellow CAD GIF illustrations use original frame 171; slide-to-PDF export omitted those illustrations. Embedded slide media otherwise appear as their supplied poster frames.')
(BASE/'sequence.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
