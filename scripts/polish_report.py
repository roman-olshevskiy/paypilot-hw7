import re,json,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'l08/observability-cost-report.md';s=p.read_text(encoding='utf-8')
a=json.loads((R/'evidence/analysis.json').read_text(encoding='utf-8'));cells=[c for c in a['b4'] if c['model']=='anthropic/claude-haiku-5.5' and c['scenario']=='B2'];b=next(c for c in cells if c['condition']=='baseline');d=next(c for c in cells if c['condition']=='defect')
step=statistics.median(run['steps'][1]['trace_cost_usd'] for run in b['results']) if 'trace_cost_usd' in b['results'][0]['steps'][1] else None
if step is None:
 print('STEP KEYS',list(b['results'][0]['steps'][1]))
else:s=s.replace('B1 warm clean/defect і B2 per-step cost',f'B2 clean, крок2: USD{step:.6f} (медіана5)')
start=s.index('### Калібрування');end=s.index('### Фінальні власні бюджети')
if start<end:
 cal=s[start:end];s=s[:start]+s[end:];pos=s.index('Вільний/тісний варіанти');s=s[:pos]+cal+'\n'+s[pos:]
# Space numbers in authored prose, without changing technical identifiers.
s=re.sub(r'([А-Яа-яІіЇїЄєҐґ])(?=\d)',r'\1 ',s)
for word in ['Haiku','Gemini','Langfuse','USD','input','output','repeat','summary','budget','release','daily','mix','check']:
 s=re.sub(r'\b'+word+r'(?=\d)',word+' ',s)
s=s.replace('стенду 2026','стенду 2026')
p.write_text(s,encoding='utf-8')
# Portable form keeps the submitted report headings and table columns.
out=['# Observability & Cost Report · <система>','<Версії, модель, прайс, backend, дата, repeats і спосіб вимірювання.>'];lines=s.splitlines();i=0
while i<len(lines):
 line=lines[i]
 if line.startswith('##'):out+=['',line,'','<Власні вимірювання, джерела та висновок.>']
 elif line.startswith('|') and i+1<len(lines) and lines[i+1].startswith('|---'):
  out+=['',line,lines[i+1],'|'+' |'*(line.count('|')-1)];i+=2
  while i<len(lines) and lines[i].startswith('|'):i+=1
  continue
 i+=1
out+=['','**Що обміняли:** <…>. **Чого не робимо:** <…>. **Умова перегляду:** <…>.','**Що не оцінюють перевірки:** <конкретні відповіді для наступного етапу>.','**Бюджети в кейсах:** <файл, IDs, daily/release, модель калібрування>.','**Залишковий ризик:** <наслідок, рішення та умова перегляду>.']
(R/'l08/observability-cost-report.template.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
