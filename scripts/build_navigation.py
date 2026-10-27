"""Build concise HW7 submission navigation from measured evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
 a=read(ROOT/'evidence/analysis.json');bill=read(ROOT/'evidence/billing-reconciliation.json')
 cases=[json.loads(x) for x in (ROOT/'sets/l05_dialogs.jsonl').read_text(encoding='utf-8').splitlines()]
 clean=a['budget_reports']['clean'];defect=a['budget_reports']['lesson-08']
 settings=json.dumps({'model':'anthropic/claude-haiku-5.5','summarize_after':20,'clock':'2026-09-15T10:00:00Z'})
 lines=['# ДЗ №7 · Observability & Cost Report',
 'На перевірці. Надіслано в LMS 2026-10-28. Повна копія актуального L03, власні бюджетні кейси й pinned L08. [Артефакти](SUBMISSION.md). [Оригінальний README L03](sources/L03-README.md).',
 '## L08 · Observability & Cost Report',
 '- [Звіт: 3 розділи](l08/observability-cost-report.md) · [порожня форма](l08/observability-cost-report.template.md).\n- [Інцидент B3](l08/incident-summary.md) · [B4](l08/b4.json) · [витрати](evidence/billing-reconciliation.json).\n- [Межі вимірювання](l08/measurement-scope.md) · [зміни кіта](l08/capture-and-runner-changes.md).',
 '### Запуск',
 'Потрібні shared-стенд із OpenRouter, TRACE_CAPTURE_CONTENT=1 і Langfuse, без L07 proxy. Ключ тільки в .env стенду. Sibling каталог — paypilot-stand-shared; для іншого шляху задати STAND_DIR.',
 '**Ці команди платні й скидають seed-БД:**',
 '~~~powershell',f"docker compose run --rm eval --set l05_dialogs --gate all --profile lesson-08 --settings '{settings}'",f"docker compose run --rm eval --set l05_dialogs --gate all --profile clean --settings '{settings}'",'~~~',
 'Без --gate all release-кейси не потраплять у звіт. Для іншої моделі змінити model у --settings і перезняти пороги. B4: з l08/kit виконати docker compose run --rm eval --scenario B4 --runs 5.',
 'Без генерацій:', '~~~powershell','docker compose run --rm eval python -m unittest discover -s tests -v','~~~',
 '### Бюджетні кейси (sets/l05_dialogs.jsonl)',
 '| ID | Що ловить | identical max | tokens_total | latency_ms | gate/runs |','|---|---|---|---|---|---|']
 for c in cases:
  m=c['additional_metadata'];b=m['budget'];reason='D14 повтор tool' if c['id']=='BUD-D14' else ('Контроль повторів' if c['id']=='BUD-READ' else ('Вартість історії; V2 пропускає D15' if c['id']=='BUD-H04' else 'Вартість історії / D15'))
  lines.append(f"| {c['id']} | {reason} | {b.get('identical_tool_calls_max','—')} | {b.get('tokens_total','—')} | {b.get('latency_ms','—')} | {m['gate']}/{m['runs']} |")
 lines+=['### Прогони',f'Фінальне Docker підтвердження V2: clean **{clean["passed"]}/{clean["total"]}**, lesson-08 **{defect["passed"]}/{defect["total"]} PASS**. Очікувані defect FAIL — бюджетні порушення, не ERROR. [Чистий клон](evidence/docker-clean-clone.json).',
 '| Серія | Обсяг | Звіт |','|---|---|---|']
 for b in a['batches']:lines.append(f"| {b['label']} | {b['chats']} chat | [native]({b['folder']}/native-results.json) |")
 lines += [f'Всього {a["chat_responses"]} chat /{a["sessions"]} сесій з усіма пілотними, калібрувальними та підтверджувальними серіями. Ці серії не злиті у спільні5/5. OpenRouter **USD{bill["key_usage_delta_usd"]:.8f}**; прямий Anthropic не використовувався.',
 'H04 V1 clean мав запас11 токенів. Clean-only правило розширення вибірки зафіксовано до own defect; V1 збережено, V2 frozen до незалежного Docker. [Рішення](evidence/calibration-amendment-intent.json), [freeze](evidence/budget-freeze.json).',
 'Budget PASS не доводить якість відповіді чи доречність дії. Raw transcripts не редагуються. Попередні ДЗ і стенд окремо не здаються.']
 (ROOT/'README.md').write_bytes(('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n').encode())
 submission='''# ДЗ №7 — артефакти здачі

**Статус: на перевірці. Надіслано в LMS 2026-10-28.**

1. [Observability & Cost Report — 3 розділи](l08/observability-cost-report.md).
2. [Порожня переносна форма](l08/observability-cost-report.template.md).
3. [6 бюджетних кейсів](sets/l05_dialogs.jsonl), [запуск і пороги](README.md#запуск).
4. [B4: дві моделі](l08/b4.json), [інцидент C-07/B3](l08/incident-summary.md).
5. [L03 reports](reports), [первинні докази](evidence/runs), [реальний Docker clean-clone](evidence/docker-clean-clone.json).
6. [Звірка витрат](evidence/billing-reconciliation.json).

Для LMS: https://github.com/roman-olshevskiy/paypilot-hw7/blob/main/SUBMISSION.md

Надсилання в LMS підтверджено 2026-10-28; очікується перевірка ментора. Пілот, калібрування, перша валідація та незалежне підтвердження розділені.
'''
 (ROOT/'SUBMISSION.md').write_bytes(submission.encode())
if __name__=='__main__':main()
