from pathlib import Path
from PIL import Image
import json,sys
import render_rope_exits as engine
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/connect-rope-color-cycle'
CYCLE=['green','purple','red','blue','yellow','pink']
CONFIG={'number':92,'name':'Upward pull — six colors','slug':'MIT-2.009-Connect-Rope-Upward-Six-Colors-30s','kind':'pull','description':'The rope changes color with every photo: Green → Purple → Red → Blue → Yellow → Pink, then repeats. Photo halves connect, and the matching rope tightens and is pulled upward. Same ten photos with two-second clean holds.','title':'Connect photo tests — upward pull, six colors','size':[1080,1080],'seconds':30,'fps':60,'audio':'Silent','added_text':False,'photo_count':10,'photo_ids':engine.PHOTO_IDS,'assembly_seconds':.5,'rope_exit_seconds':.5,'hold_seconds':2,'color_cycle':CYCLE}
if __name__=='__main__':
 engine.OUT=OUT
 if '--preview' in sys.argv:
  sheet=Image.new('RGB',(1800,720))
  for i in range(10):sheet.paste(engine.frame(CONFIG,i*3+.70).resize((360,360)),((i%5)*360,(i//5)*360))
  sheet.save(OUT/'Ten-Photo-Color-Sequence.jpg',quality=94)
  engine.frame(CONFIG,.70).save(OUT/'92.jpg',quality=94)
  (ROOT/'work/rope-color-config.json').write_text(json.dumps(CONFIG,indent=2))
 else:engine.render(CONFIG)
