# ДЗ №7 · Observability & Cost Report

**На перевірці.** Надіслано в LMS 2026-10-28. Повна копія актуального L03, власні бюджетні кейси й pinned L08. [Артефакти](SUBMISSION.md). [Оригінальний README L03](sources/L03-README.md).

## L08 · Observability & Cost Report

- [Звіт: 3 розділи](l08/observability-cost-report.md) · [порожня форма](l08/observability-cost-report.template.md).
- [Інцидент B3](l08/incident-summary.md) · [B4](l08/b4.json) · [витрати](evidence/billing-reconciliation.json).
- [Межі вимірювання](l08/measurement-scope.md) · [зміни кіта](l08/capture-and-runner-changes.md).

### Запуск

Потрібні shared-стенд із OpenRouter, TRACE_CAPTURE_CONTENT=1 і Langfuse, без L07 proxy. Ключ тільки в .env стенду. Sibling каталог — paypilot-stand-shared; для іншого шляху задати STAND_DIR.

**Ці команди платні й скидають seed-БД:**

~~~powershell

docker compose run --rm eval --set l05_dialogs --gate all --profile lesson-08 --settings '{"model": "anthropic/claude-haiku-5.5", "summarize_after": 20, "clock": "2026-09-15T10:00:00Z"}'

docker compose run --rm eval --set l05_dialogs --gate all --profile clean --settings '{"model": "anthropic/claude-haiku-5.5", "summarize_after": 20, "clock": "2026-09-15T10:00:00Z"}'

~~~

Без --gate all release-кейси не потраплять у звіт. Для іншої моделі змінити model у --settings і перезняти пороги. B4: з l08/kit виконати docker compose run --rm eval --scenario B4 --runs 5.

Без генерацій:

~~~powershell

docker compose run --rm eval python -m unittest discover -s tests -v

~~~

### Бюджетні кейси (sets/l05_dialogs.jsonl)

| ID | Що ловить | identical max | tokens_total | latency_ms | gate/runs |
|---|---|---|---|---|---|
| BUD-H01 | Вартість історії / D15 | — | 63980 | 40436 | release/5 |
| BUD-H02 | Вартість історії / D15 | — | 44556 | 34254 | release/5 |
| BUD-H04 | Вартість історії; V2 пропускає D15 | — | 65935 | 46328 | release/5 |
| BUD-D15 | Вартість історії / D15 | — | 47252 | 43080 | release/5 |
| BUD-D14 | D14 повтор tool | 1 | — | — | daily/1 |
| BUD-READ | Контроль повторів | 1 | — | — | daily/1 |

### Прогони

Фінальне Docker підтвердження V2: clean **6/6**, lesson-08 **2/6 PASS**. Очікувані defect FAIL — бюджетні порушення, не ERROR. [Чистий клон](evidence/docker-clean-clone.json).

| Серія | Обсяг | Звіт |
|---|---|---|
| budget-clean | 134 chat | [native](evidence/runs/20261027T221538630461Z-budget-clean-2d46f5/native-results.json) |
| budget-lesson-08 | 134 chat | [native](evidence/runs/20261027T222429188410Z-budget-lesson-08-d0d880/native-results.json) |
| calibration-clean | 130 chat | [native](evidence/runs/20261027T220838340008Z-calibration-clean-4ee9d2/native-results.json) |
| docker-budget-clean | 134 chat | [native](evidence/runs/20261027T224126192424Z-docker-budget-clean-bf79e3/native-results.json) |
| docker-budget-lesson-08 | 134 chat | [native](evidence/runs/20261027T223236576766Z-docker-budget-lesson-08-420be1/native-results.json) |
| full-b3 | 40 chat | [native](evidence/runs/20261027T220440252303Z-full-b3-4903b6/native-results.json) |
| full-b4 | 180 chat | [native](evidence/runs/20261027T215512055520Z-full-b4-3be58d/native-results.json) |
| no-summary-control | 40 chat | [native](evidence/runs/20261027T225106650172Z-no-summary-control-0d37bf/native-results.json) |
| pilot-b1 | 4 chat | [native](evidence/runs/20261027T215203220006Z-pilot-b1-013ccb/native-results.json) |
| pilot-b2 | 14 chat | [native](evidence/runs/20261027T215236752199Z-pilot-b2-e4d843/native-results.json) |
| pilot-gemini | 2 chat | [native](evidence/runs/20261027T215338813072Z-pilot-gemini-4de854/native-results.json) |

Всього 946 chat /173 сесій з усіма пілотними, калібрувальними та підтверджувальними серіями. Ці серії не злиті у спільні5/5. OpenRouter **USD0.59045408**; прямий Anthropic не використовувався.

H04 V1 clean мав запас11 токенів. Clean-only правило розширення вибірки зафіксовано до own defect; V1 збережено, V2 frozen до незалежного Docker. [Рішення](evidence/calibration-amendment-intent.json), [freeze](evidence/budget-freeze.json).

Budget PASS не доводить якість відповіді чи доречність дії. Raw transcripts не редагуються. Попередні ДЗ і стенд окремо не здаються.
