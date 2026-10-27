"""Plot measured B2 first-call input tokens across five Haiku dialogues per condition."""
import json,statistics
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/json.loads((ROOT/'evidence/full-b4-index.json').read_text(encoding='utf-8'))['folder']/'native-results.json'
cells=json.loads(p.read_text(encoding='utf-8'))[0]['cells'];fig,ax=plt.subplots(figsize=(8,4.4))
for condition,color,label in [('baseline','#176b87','clean'),('defect','#c44934','lesson-08')]:
 c=next(c for c in cells if c['model']=='anthropic/claude-haiku-5.5' and c['scenario']=='B2' and c['condition']==condition)
 values=[[r['steps'][i]['first_call_input'] for r in c['results']] for i in range(7)]
 med=[statistics.median(v) for v in values]
 ax.plot(range(1,8),med,marker='o',color=color,label=label+' (median, n=5)')
 ax.fill_between(range(1,8),[min(v) for v in values],[max(v) for v in values],color=color,alpha=.12)
ax.set(xlabel='Dialogue step',ylabel='First model-call input tokens',title='B2 / C-07: context replay increases input length')
ax.set_xticks(range(1,8));ax.grid(alpha=.18);ax.legend(frameon=False);ax.spines[['top','right']].set_visible(False)
fig.text(.12,.015,'Haiku 5.5 via OpenRouter. Shading: observed min–max; no cross-model token comparison.',fontsize=8,color='#555555')
fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(ROOT/'l08/screenshots/b2-token-curve.png',dpi=180);fig.savefig(ROOT/'l08/screenshots/b2-token-curve.svg')
