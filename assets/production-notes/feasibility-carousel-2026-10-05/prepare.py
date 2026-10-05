"""Preserve submitted slide artwork for the requested lecture carousel."""
import concurrent.futures,hashlib,json,subprocess
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from pypdf import PdfReader
BASE=Path(__file__).resolve().parent
POPPLER='/Users/dannygoldfield/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm'
ORDER=['Green','Purple','Red','Blue','Yellow','Pink']
source=BASE/'source'; pdf=BASE/'pdf'; images=BASE/'slides';images.mkdir(exist_ok=True)
choices={
 'Green':(next(source.glob('green*.pdf')),None),
 'Purple':(next(pdf.glob('purple*.pdf')),None),
 'Red':(next(source.glob('red*.pdf')),None),
 'Blue':(next(source.glob('blue*.pdf')),None),
 'Yellow':(pdf/'Feasilbility Student Feedback Forms 2026.pdf',list(range(4,36))),
 'Pink':(next(source.glob('pink*.pdf')),None),
}
def raster(color):
 file,pages=choices[color];reader=PdfReader(file);pages=pages or list(range(1,len(reader.pages)+1))
 folder=images/color.lower();folder.mkdir(exist_ok=True)
 subprocess.run([POPPLER,'-f',str(min(pages)),'-l',str(max(pages)),'-scale-to','1920','-png',str(file),str(folder/'slide')],check=True,stdout=subprocess.DEVNULL)
 rendered={int(p.stem.split('-')[-1]):p for p in folder.glob('slide-*.png')}
 records=[]
 for page in pages:
  image=rendered[page]
  with Image.open(image) as im: size=list(im.size)
  records.append({'color':color,'source_pdf':str(file.relative_to(BASE)),'source_page':page,'image':str(image.relative_to(BASE)),'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'image_size':size,'text':reader.pages[page-1].extract_text() or ''})
 print(json.dumps({'rasterized':color,'slides':len(records)}),flush=True)
 return color,records
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 by_color=dict(pool.map(raster,ORDER))
records=[r for color in ORDER for r in by_color[color]]
for i,r in enumerate(records):r['index']=i+1;r['center_time_seconds']=i*3
manifest={'source_files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()},'team_order':ORDER,'ordering':'team presentations together, original slide order within each team','seconds_per_slide':3,'slide_count':len(records),'duration_seconds':len(records)*3,'team_counts':{c:len(by_color[c]) for c in ORDER},'slides':records,'selection_notes':['Each team submission included once; paired PowerPoint/PDF exports use the submitted PDF.','Yellow project slides 4–35 from the feedback deck duplicate the legacy PPT project content, confirmed by extracted text; bundled renderer cannot open that legacy PPT.','The ZIP supplies complete Green, Purple, Red, Blue and Pink decks, including appendix slides and progressive diagrams.','Classroom introduction, seating instructions, blank separators and feedback cards omitted.']}
(BASE/'sequence.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
review=BASE/'review';review.mkdir(exist_ok=True)
for color in ORDER:
 rows=by_color[color]
 for offset in range(0,len(rows),24):
  batch=rows[offset:offset+24];sheet=Image.new('RGB',(1600,((len(batch)+3)//4)*250),'#e6e6e6');draw=ImageDraw.Draw(sheet)
  for n,r in enumerate(batch):
   x=(n%4)*400;y=(n//4)*250
   with Image.open(BASE/r['image']) as im: thumb=ImageOps.contain(im.convert('RGB'),(396,223),Image.Resampling.LANCZOS);sheet.paste(thumb,(x,y+24))
   draw.text((x+8,y+6),f'{color} · source page {r["source_page"]}',fill='black')
  sheet.save(review/f'contact-{color.lower()}-{offset//24+1}.jpg',quality=90)
print(json.dumps({'count':len(records),'duration':len(records)*3,'counts':manifest['team_counts']}),flush=True)
