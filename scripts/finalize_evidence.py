import json,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def rd(p):return json.loads((R/p).read_text(encoding='utf-8'))
def wr(p,v):(R/p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
a=rd('evidence/analysis.json');before=rd('evidence/key-usage-before.json');after=rd('evidence/key-usage-after.json');delta=after['usage']-before['usage'];provider=a['provider_span_sum_usd']
assert abs(delta-provider)<1e-8
wr('evidence/billing-reconciliation.json',{'key_usage_before_usd':before['usage'],'key_usage_after_usd':after['usage'],'key_usage_delta_usd':delta,'provider_generation_sum_usd':provider,'independent_span_price_usd':a['independent_all_generation_span_price_usd'],'root_usage_estimate_usd':a['root_usage_estimate_sum_usd'],'key_minus_provider_usd':delta-provider,'chat_responses':a['chat_responses'],'sessions':a['sessions'],'byok_usage':after['byok_usage'],'direct_anthropic_calls':0,'scope':'All HW7 paid batches; no concurrent key consumer confirmed. Key usage is not account available balance.'})
lines=['# Звірка прогнозу і контроль без summary','Прогноз збережено в 4c20fbb до першого платного виклику. Початкові гіпотези не редагувалися.']
for sid in ['B1','B2']:
 cells=[c for c in a['b4'] if c['model']=='anthropic/claude-haiku-5.5' and c['scenario']==sid]
 for c in cells:
  if sid=='B1' and c['condition']=='defect':
   ratios=[s['provider_cost_usd']/s['usage_cost_usd'] for run in c['results'] for s in run['steps'] if s.get('usage_cost_usd') and s.get('provider_cost_usd')]
   lines.append('D14: provider/usage за кроками — '+str(ratios)+'. Прогноз 4–6× стосувався кроку з петлею, не прогрівального кроку.')
 if sid=='B2':
  b=next(c for c in cells if c['condition']=='baseline');d=next(c for c in cells if c['condition']=='defect');lines.append(f"B2 Haiku: {d['cost_usd_median']/b['cost_usd_median']:.3f}×, у прогнозованому інтервалі 1.15–1.5×.")
def totals(label):
 idx=rd('evidence/'+label+'-index.json');rows=rd(idx['folder']+'/captures.json');groups={}
 for row in rows:
  k=(row['condition'],row['response']['session_id']);groups[k]=groups.get(k,0)+sum(float(s['attributes'].get('provider.cost_usd') or 0) for s in row['trace']['children'] if s['name'] in ['llm.call','agent.summarize'])
 return {cond:statistics.median(v for (c,s),v in groups.items() if c==cond) for cond in ['baseline','defect']}
b3=totals('full-b3');no=totals('no-summary-control');wr('evidence/summary-control-comparison.json',{'summary_after_2_provider_median':b3,'summary_disabled_provider_median':no,'runs_per_condition':5,'scope':'Independent real dialogues, not paired deterministic generations; summary disabled via summarize_after=20 on four turns.'})
lines += [f'B3 provider median: clean USD{b3["baseline"]:.8f}, lesson-05 USD{b3["defect"]:.8f}. Прогноз про дорожче дефектне стиснення '+('підтвердився.' if b3['defect']>b3['baseline'] else 'не підтвердився.'),'Span/provider узгоджуються за повного обліку генерацій, включно з agent.summarize; llm.call-only пропускає сумаризатор. Пілотна помилка effective cache-write Gemini виправлена до основної серії й залишена у сирих доказах.',f'Додатковий контроль без summary (окремий намір закомічено до його запусків): clean USD{no["baseline"]:.8f}, lesson-05 USD{no["defect"]:.8f}, по5 повторів. Це нове спостереження, а не заднім числом дописаний початковий прогноз. У цих коротких діалогах обидва варіанти без summary дешевші; переносити висновок на довгі діалоги без вимірювання не можна.']
(R/'l08/forecast-review.md').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'billing':delta,'b3':b3,'no_summary':no},indent=2))
