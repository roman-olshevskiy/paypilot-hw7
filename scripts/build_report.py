"""Build concise report from completed measured evidence only."""
import json,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def money(v):return f'{v:.6f}'
def main():
 a=read(ROOT/'evidence/analysis.json');bill=read(ROOT/'evidence/billing-reconciliation.json');cells=a['b4']
 def cell(model,scenario,condition):return next(x for x in cells if x['model']==model and x['scenario']==scenario and x['condition']==condition)
 haiku='anthropic/claude-haiku-5.5';gemini='google/gemini-2.5-flash';b=cell(haiku,'B2','baseline');d=cell(haiku,'B2','defect')
 ratios=[d['input_tokens_median']/b['input_tokens_median'],d['time_ms_median']/b['time_ms_median'],d['cost_usd_median']/b['cost_usd_median']]
 incident=read(ROOT/'evidence/incident.json');rootlink='../'+incident['folder']+'/captures.json'
 lines=['# Observability & Cost Report · PayPilot',
 'Вимірювання27–28.10.2026 (Europe/Kyiv); clock стенду2026-09-15. Shared74f1995; L03 7d0f5e7; L08 666e496. OpenRouter: Haiku5.5 та Gemini2.5 Flash. Langfuse4.69.0 локально. Прайс USD/M: Haiku input0.10/output0.50/cache-read0.01/write0.125; Gemini0.30/2.50/0.03/effective-write0.113333. [Каталог API](../evidence/model-prices-api.json), [облік Gemini](pilot-and-price-review.md). B4/B3:5 незалежних повторів на умову; daily budget1, release5. Пілот і clean-калібрування окремі.',
 '## Слайд 1 · Трейс проти лічильника',
 '![C-07: усі7 кроків і ціна сесії](screenshots/c07-seven-steps-total-cost.png)',
 'Сесія f7146bdde3cf:7 кроків, Langfuse exact generation sum USD0.00445066; UI сесії округлює до USD0.004, [колонка Total Cost](screenshots/c07-total-cost-column.png) — до USD0.004451. Це repeat1, а таблиці нижче — медіани5. [Raw Langfuse](../evidence/langfuse/session-f7146bdde3cf.json).',
 '| Сліпа зона | Що пропущено | Джерело перевірки |','|---|---|---|',
 '| usage.cost_usd за D14 | Приховані повтори моделі;8 однакових get_transactions | Provider cost і всі llm.call spans |',
 '| Langfuse без model definition | Ціна Haiku відсутня на старих сесіях | [Скриншот до налаштування](screenshots/sessions-before-haiku-pricing.png) |',
 '| Лише input/output prices | Cache buckets без ціни занижують суму | [Повне визначення](screenshots/haiku-model-definition.png), usage breakdown |',
 '| llm.call sum / root usage | Summary generation не включена | agent.summarize usage + provider total |',
 'Для сесії f7146bdde3cf лише input/output prices дали б USD0.00340920 замість USD0.00445066; cache buckets пояснюють різницю. Reasoning high не запускався; нуль reasoning у цих сесіях не доводить відсутність витрат за інших налаштувань.',
 '**Інцидент B3, lesson-05/summarize_after2, repeat2:**',
 '| Крок | Спан | Що записано | Де розійшлося |','|---|---|---|---|',
 '| 1–2 | tool results / llm.call | TX-0401 і duplicate_charge присутні в історії | Ще є у вході summary |',
 '| **3** | **agent.summarize** | **summary.input: TX-0401/duplicate_charge; summary.text: без них, service_not_rendered** | **Втрата на виході стиснення** |',
 '| 4 | llm.call / tools | '+', '.join(incident['step4_tools'])+' | Повторне отримання контексту після втрати |',
 '**Що було у вході генерації на кроці, де розійшлося:** summary.input спана agent.summarize містив TX-0401 і duplicate_charge; summary.text втратив обидві сутності.',
 'Для регулятора: на кроці3 agent.summarize отримав TX-0401/duplicate_charge, але видав переказ без номера й з іншим reason code. [Дослівні вхід/вихід та IDs](incident-summary.md). Clean summary5/5; defect0/5, із них не кожен губив обидві сутності.',
 '**Ціна з трьох джерел, медіана USD/діалог (Haiku):**',
 '| Сценарій | Умова | usage.cost_usd | Сума llm.call за прайсом | Provider cost |','|---|---|---|---|---|']
 for sid in ['B1','B2']:
  for cond in ['baseline','defect']:
   c=cell(haiku,sid,cond);usage=statistics.median(sum(s['usage_cost_usd'] for s in x['steps']) for x in c['results'])
   label='clean' if cond=='baseline' else ('clean+D14' if sid=='B1' else 'lesson-08')
   lines.append(f"| {sid} | {label} | {money(usage)} | {money(c['cost_usd_median'])} | {money(c['provider_usd_median'])} |")
 lines += [f'B2 lesson-08/clean: input tokens **{ratios[0]:.2f}×**, час **{ratios[1]:.2f}×**, ціна **{ratios[2]:.2f}×**. [Крива токенів](screenshots/b2-token-curve.png). D15 — різниця нахилів і context replay у вході, не сам факт зростання історії.',
 f'Усі платні серії разом: {a["chat_responses"]} chat, {a["sessions"]} сесій; key delta **USD{bill["key_usage_delta_usd"]:.8f}**. [Повна звірка](../evidence/billing-reconciliation.json); account balance не підміняється лімітом ключа.',
 '## Слайд 2 · Прогноз',
 '| Поверх | Значення | Джерело |','|---|---|---|',
 f'| Крок | B1 warm clean/defect і B2 per-step cost | Реальні spans, [B4](b4.json) |',
 f'| Діалог | B2 clean USD{b["cost_usd_median"]:.6f}; lesson-08 USD{d["cost_usd_median"]:.6f} | Медіани5 |',
 '| Місяць | 800 активних користувачів ×20 діалогів; mix30% B1/70% B2 | 800 із завдання; частота й mix — явні планові припущення |']
 monthly={}
 for model in [haiku,gemini]:
  c=.3*cell(model,'B1','baseline')['cost_usd_median']+.7*cell(model,'B2','baseline')['cost_usd_median'];monthly[model]=800*20*c
  lines.append(f'| {model} | USD{monthly[model]:.2f}/місяць; C(N)=N×20×{c:.7f} | Виміряний clean mix, без hosting/fixed costs |')
 lines += ['**Що росте швидше за N:** при фіксованій довжині й mix витрати лінійні в N. Надлінійність потребує зміни довжини/контексту або навантаження; повторне перечитування історії може давати суму порядку T² у довжині діалогу T. Не приписуємо N автоматичну нелінійність. [Припущення](planning-assumptions.json).',
 'Прогноз закомічено до оплати: [4 гіпотези](forecast-before-runs.md). Пілот уточнив запас D15 до5% до власних прогонів; [історія рішення](calibration-rule-update.md). Гіпотези не переписані заднім числом.',
 '## Слайд 3 · Рішення',
 '| Важіль | Що дає | Що псується |','|---|---|---|',
 '| Ліміт однакових tool calls | Зупиняє D14-петлю | Може блокувати обґрунтований повтор після тимчасової помилки |',
 '| Контроль context replay / бюджет токенів | Зменшує зайвий вхід D15 | Надто тісний поріг відхиляє законний довгий діалог |',
 '| Стиснення історії | Обмежує контекст | B3 показує втрату сутностей і повторні tools; потрібен summary invariant |',
 '| Зміна моделі | Може зменшити час | Інші tokenizer/поведінка, старі пороги не переносні |',
 '**Що обміняли:** дешевші виміряні Haiku-діалоги проти швидшого Gemini. **Чого не робимо:** не міняємо модель лише за прайсом і не видаємо cost PASS за якість. **Умова перегляду:** виміряна потреба меншої latency, новий прайс/навантаження й калібровані бюджети та semantic checks.',
 '### Міграція моделі',
 '| Модель | Сценарій/умова | USD: медіана (min–max) | Час, с: медіана (min–max) | Перевірки |','|---|---|---|---|---|']
 for c in cells:
  name='Haiku' if c['model']==haiku else 'Gemini';t=c['time_ms_spread'];cond='clean' if c['condition']=='baseline' else ('D14' if c['scenario']=='B1' else 'lesson-08')
  lines.append(f"| {name} | {c['scenario']}/{cond} | {c['cost_usd_median']:.6f} ({c['cost_usd_min']:.6f}–{c['cost_usd_max']:.6f}) | {t['median']/1000:.1f} ({t['min']/1000:.1f}–{t['max']/1000:.1f}) | {c['verdict']} |")
 lines += ["""- **Рішення:** зараз не переходимо. Haiku дешевший за обидва виміряні clean діалоги; Gemini швидший.
- **Що зелене:** B1 tool/precondition+duplicate check5/5 clean на обох; B2 clean aggregate PASS. D14 виявлено5/5 обома.
- **Чого перевірки не бачать:** правильність/тон/повноту відповідей і доречність раннього create_dispute у C-07; це конкретні кандидати для L09, [межі](measurement-scope.md).
- **Пороги перезняти:** tokens_total, latency_ms власних release-кейсів і first-call-input B2. На Gemini6500 пропускає defect; tokenizer-токени між моделями не порівнюємо. Довідкові токени є в b4.json.""",
 '**Бюджети в кейсах:** [sets/l05_dialogs.jsonl](../sets/l05_dialogs.jsonl): BUD-H01/H02/H04/D15 — release5; BUD-D14/READ — daily1. Пороги frozen після окремого calibration, до фінальних умов. [Native L03 reports](../reports), [метод](measurement-scope.md).',
 '### Калібрування tokens_total · BUD-D15',
 '| Варіант | Поріг | Clean median/verdict | Lesson-08 median/verdict |','|---|---|---|---|']
 for c in a['calibration']:lines.append(f"| {c['label']} | {c['threshold']} | {c['clean_median']} / {'PASS' if c['clean_pass'] else 'FAIL'} | {c['defect_median']} / {'PASS' if c['defect_pass'] else 'FAIL'} |")
 lines += ['Вільний/тісний варіанти — retrospective re-evaluation тих самих captures, не нові генерації. Обраний поріг frozen до final clean/lesson-08; запас5% від незалежного calibration baseline. [Усі samples і запас](../evidence/budget-calibration.json).',
 '**Залишковий ризик:** latency пороги залежать від локального instrumentation; місячний mix — припущення;5 повторів не доводять універсальність. Перезняти при зміні моделі/оточення. Semantic L09 і production capacity/hosting не вимірювалися. Точні raw докази зберігаються окремо.']
 (ROOT/'l08/observability-cost-report.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n',encoding='utf-8')
 print('Report written')
if __name__=='__main__':main()
