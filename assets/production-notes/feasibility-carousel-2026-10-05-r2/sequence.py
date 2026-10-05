"""Alternate teams while retaining forward source-page order."""
import argparse,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['once','repeat'],required=True);args=parser.parse_args()
source=json.loads((BASE/'source-sequence.json').read_text())
colors=source['team_order']
by_color={c:sorted([r for r in source['slides'] if r['color']==c],key=lambda r:r['source_page']) for c in colors}
rows=[]
for round_index in range(max(map(len,by_color.values()))):
 for color in colors:
  team=by_color[color]
  if args.mode=='once' and round_index>=len(team):continue
  record=dict(team[round_index%len(team)])
  record.update(index=len(rows)+1,center_time_seconds=len(rows)*3,team_slide_index=round_index%len(team)+1,color_round=round_index+1)
  rows.append(record)
source.update(revision=2,slides=rows,slide_count=len(rows),duration_seconds=len(rows)*3,motion_direction='right to left',ordering='alternate Green, Purple, Red, Blue, Yellow, Pink; forward page order within each team',rotation_mode=args.mode,unique_slide_count=len(source['slides']))
source['selection_notes']=[note for note in source['selection_notes'] if 'omitted' in note or 'embedded' in note or 'Yellow' in note or 'ZIP supplies' in note or 'paired' in note]
source['selection_notes'].append('Revision 2: alternate teams; upcoming slides enter from the right, with source pages progressing forward. '+('Each source slide appears once; teams drop out when finished.' if args.mode=='once' else 'Shorter teams repeat from page 1 to maintain the exact six-color cycle through all 51 rounds.'))
(BASE/'sequence.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'count':len(rows),'duration_seconds':len(rows)*3,'rotation_mode':args.mode,'first_round':[(r['color'],r['source_page']) for r in rows[:6]],'last_round':[(r['color'],r['source_page']) for r in rows[-6:]]},indent=2))
