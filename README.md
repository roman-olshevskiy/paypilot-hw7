# ДЗ №7 · Observability & Cost Report

**Прийнято.** Зараховано ментором; підтверджено 2026-10-28 після повторного надсилання. Повна копія актуального L03, власні бюджетні кейси й зафіксована версія L08. [Артефакти](SUBMISSION.md). [Оригінальний README L03](sources/L03-README.md).

## L08 · Observability & Cost Report

- [Звіт: 3 розділи](l08/observability-cost-report.md) · [порожня форма](l08/observability-cost-report.template.md).
- [Інцидент B3](l08/incident-summary.md) · [B4](l08/b4.json) · [витрати](evidence/billing-reconciliation.json).
- [Межі вимірювання](l08/measurement-scope.md) · [зміни кіта](l08/capture-and-runner-changes.md).

### Запуск

Потрібні shared-стенд із OpenRouter, TRACE_CAPTURE_CONTENT=1 і Langfuse, без L07 proxy. Ключ тільки в .env стенду. Сусідній каталог — paypilot-stand-shared; для іншого шляху задати STAND_DIR.

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
| BUD-H04 | Бюджет історії; V2 пропускає D15 | — | 65935 | 46328 | release/5 |
| BUD-D15 | Вартість історії / D15 | — | 47252 | 43080 | release/5 |
| BUD-D14 | D14: повтор інструмента | 1 | — | — | daily/1 |
| BUD-READ | Контроль повторів | 1 | — | — | daily/1 |

### Прогони

Фінальне Docker підтвердження V2: clean **6/6**, lesson-08 **2/6 PASS**. Очікувані defect FAIL — бюджетні порушення, не ERROR. [Чистий клон](evidence/docker-clean-clone.json).

[Усі 11 серій і первинні звіти](l08/run-index.md): 946 chat-відповідей у 173 сесіях. Прямий Anthropic не використовувався.

Поріг H04 V2 пропускає D15; інші три токенові кейси його виявляють. [Калібрування та межі](l08/budget-calibration-notes.md). Budget PASS не підтверджує якість відповіді чи доречність дії.

Витрати ДЗ7 **USD 0.590454076** звірено з кабінетом OpenRouter 28.10.2026: накопичений usage USD 0.6290 відповідає точному usage ключа після округлення. [Звірка та межі модельної розбивки](evidence/billing-reconciliation.json).
