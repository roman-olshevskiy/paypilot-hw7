# Observability & Cost Report · PayPilot

Вимірювання 27–28.10.2026 (Europe/Kyiv); clock стенду 2026-09-15. Shared74f1995; L03 7d0f5e7; L08 666e496. OpenRouter: Haiku 5.5 та Gemini 2.5 Flash. Langfuse 4.69.0 локально. Прайс USD/M: Haiku input 0.10/output 0.50/cache-read0.01/write0.125; Gemini 0.30/2.50/0.03/effective-write0.113333. [Каталог API](../evidence/model-prices-api.json), [облік Gemini](pilot-and-price-review.md). B4/B3:5 незалежних повторів на умову; daily budget 1, release 5. Пілот і clean-калібрування окремі.

## Слайд 1 · Трейс проти лічильника

![C-07: усі 7 кроків і ціна сесії](screenshots/c07-seven-steps-total-cost.png)

Сесія f7146bdde3cf:7 кроків, Langfuse exact generation sum USD 0.00445066; UI сесії округлює до USD 0.004, [колонка Total Cost](screenshots/c07-total-cost-column.png) — до USD 0.004451. Це repeat 1, а таблиці нижче — медіани 5. [Raw Langfuse](../evidence/langfuse/session-f7146bdde3cf.json).

| Сліпа зона | Що пропущено | Джерело перевірки |
|---|---|---|
| usage.cost_usd за D14 | Приховані повтори моделі;8 однакових get_transactions | Provider cost і всі llm.call spans |
| Langfuse без model definition | Ціна Haiku відсутня на старих сесіях | [Сесії, записані до definition](screenshots/sessions-before-haiku-pricing.png) |
| Лише input/output prices | Cache buckets без ціни занижують суму | [Повне визначення](screenshots/haiku-model-definition.png), usage breakdown |
| llm.call sum / root usage | Summary generation не включена | agent.summarize usage + provider total |

Для сесії f7146bdde3cf лише input/output prices дали б USD 0.00340920 замість USD 0.00445066; cache buckets пояснюють різницю. Reasoning high не запускався; нуль reasoning у цих сесіях не доводить відсутність витрат за інших налаштувань.

**Інцидент B3, lesson-05/summarize_after2, repeat 2:**

| Крок | Спан | Що записано | Де розійшлося |
|---|---|---|---|
| 1–2 | tool results / llm.call | TX-0401 і duplicate_charge присутні в історії | Ще є у вході summary |
| **3** | **agent.summarize** | **summary.input: TX-0401/duplicate_charge; summary.text: без них, service_not_rendered** | **Втрата на виході стиснення** |
| 4 | llm.call / tools | tool.get_account, tool.get_transactions | Повторне отримання контексту після втрати |

**Що було у вході генерації на кроці, де розійшлося:** summary.input спана agent.summarize містив TX-0401 і duplicate_charge; summary.text втратив обидві сутності.

Для регулятора: на кроці 3 agent.summarize отримав TX-0401/duplicate_charge, але видав переказ без номера й з іншим reason code. [Дослівні вхід/вихід та IDs](incident-summary.md). Clean summary 5/5; defect0/5, із них не кожен губив обидві сутності.

**Ціна з трьох джерел, медіана USD/діалог (Haiku):**

| Сценарій | Умова | usage.cost_usd | Сума llm.call за прайсом | Provider cost |
|---|---|---|---|---|
| B1 | clean | 0.000349 | 0.000348 | 0.000348 |
| B1 | clean+D14 | 0.000484 | 0.001852 | 0.001852 |
| B2 | clean | 0.004160 | 0.004161 | 0.004161 |
| B2 | lesson-08 | 0.006192 | 0.006192 | 0.006192 |

| B2 · медіани | Clean | Lesson-08 |
|---|---|---|
| Input tokens | 57053 | 76634 |
| Час, мс | 22895 | 24762 |
| USD/діалог | 0.004161 | 0.006192 |

B2 lesson-08/clean: input tokens **1.34×**, час **1.08×**, ціна **1.49×**. [Крива токенів](screenshots/b2-token-curve.png). D15 — різниця нахилів і context replay у вході, не сам факт зростання історії.

Усі платні серії разом: 946 chat, 173 сесій; key delta **USD 0.59045408**. [Повна звірка](../evidence/billing-reconciliation.json); account balance не підміняється лімітом ключа.

## Слайд 2 · Прогноз

| Поверх | Значення | Джерело |
|---|---|---|
| Крок | B2 clean, крок 2: USD 0.000740 (медіана 5) | Реальні spans, [B4](b4.json) |
| Діалог | B2 clean USD 0.004161; lesson-08 USD 0.006192 | Медіани 5 |
| Місяць | 800 активних користувачів ×20 діалогів; mix 30% B1/70% B2 | 800 із завдання; частота й mix — явні планові припущення |
| anthropic/claude-haiku-5.5 | USD 48.27/місяць; C(N)=N×20×0.0030171 | Виміряний clean mix, без hosting/fixed costs |
| google/gemini-2.5-flash | USD 60.23/місяць; C(N)=N×20×0.0037646 | Виміряний clean mix, без hosting/fixed costs |

**Що росте швидше за N:** при фіксованій довжині й mix витрати лінійні в N. Надлінійність потребує зміни довжини/контексту або навантаження; повторне перечитування історії може давати суму порядку T² у довжині діалогу T. Не приписуємо N автоматичну нелінійність. [Припущення](planning-assumptions.json).

Прогноз закомічено до оплати: [4 гіпотези](forecast-before-runs.md). Пілот уточнив запас D15 до 5% до власних прогонів; [історія рішення](calibration-rule-update.md). Гіпотези не переписані заднім числом.

## Слайд 3 · Рішення

| Важіль | Що дає | Що псується |
|---|---|---|
| Ліміт однакових tool calls | Зупиняє D14-петлю | Може блокувати обґрунтований повтор після тимчасової помилки |
| Контроль context replay / бюджет токенів | Зменшує зайвий вхід D15 | Надто тісний поріг відхиляє законний довгий діалог |
| Стиснення історії | Обмежує контекст | B3 показує втрату сутностей і повторні tools; потрібен summary invariant |
| Зміна моделі | Може зменшити час | Інші tokenizer/поведінка, старі пороги не переносні |

**Що обміняли:** дешевші виміряні Haiku-діалоги проти швидшого Gemini. **Чого не робимо:** не міняємо модель лише за прайсом і не видаємо cost PASS за якість. **Умова перегляду:** виміряна потреба меншої latency, новий прайс/навантаження й калібровані бюджети та semantic checks.

### Міграція моделі

| Модель | Сценарій/умова | USD: медіана (min–max) | Час, с: медіана (min–max) | Перевірки |
|---|---|---|---|---|
| Gemini | B1/clean | 0.000518 (0.000498–0.000555) | 3.0 (2.8–3.6) | 5/5 |
| Gemini | B1/D14 | 0.001870 (0.001846–0.004103) | 8.3 (7.8–14.3) | 0/5 |
| Gemini | B2/clean | 0.005156 (0.004906–0.005298) | 11.3 (10.5–11.4) | PASS |
| Gemini | B2/lesson-08 | 0.007002 (0.006837–0.008821) | 10.2 (9.8–12.5) | PASS |
| Haiku | B1/clean | 0.000348 (0.000329–0.000369) | 4.7 (4.6–4.8) | 5/5 |
| Haiku | B1/D14 | 0.001852 (0.001786–0.001875) | 18.6 (18.4–19.9) | 0/5 |
| Haiku | B2/clean | 0.004161 (0.003949–0.004823) | 22.9 (22.6–25.9) | PASS |
| Haiku | B2/lesson-08 | 0.006192 (0.005164–0.006922) | 24.8 (23.2–26.1) | FAIL |

- **Рішення:** зараз не переходимо. Haiku дешевший за обидва виміряні clean діалоги; Gemini швидший.
- **Що зелене:** B1 tool/precondition+duplicate check 5/5 clean на обох; B2 clean aggregate PASS. D14 виявлено 5/5 обома.
- **Чого перевірки не бачать:** правильність/тон/повноту відповідей і доречність раннього create_dispute у C-07; це конкретні кандидати для L09, [межі](measurement-scope.md).
- **Пороги перезняти:** tokens_total, latency_ms власних release-кейсів і first-call-input B2. На Gemini 6500 пропускає defect; tokenizer-токени між моделями не порівнюємо. Довідкові токени є в b4.json.

**Бюджети в кейсах:** [sets/l05_dialogs.jsonl](../sets/l05_dialogs.jsonl): BUD-H01/H02/H04/D15 — release 5; BUD-D14/READ — daily 1. Пороги frozen після окремого calibration, до фінальних умов. [Native L03 reports](../reports), [метод](measurement-scope.md).

### Фінальні власні бюджети · Docker V2

| Кейс | Clean | Lesson-08 |
|---|---|---|
| BUD-H01 | PASS | FAIL |
| BUD-H02 | PASS | FAIL |
| BUD-H04 | PASS | PASS |
| BUD-D15 | PASS | FAIL |
| BUD-D14 | PASS | FAIL |
| BUD-READ | PASS | PASS |

H04 V1 мав лише 11 токенів запасу на held-out clean. Розширення clean-вибірки до 10 зареєстровано до власної defect-серії; V2 frozen до незалежного Docker. Поріг 65935 зменшує ризик false positive, але пропускає D15 у H04. D15 виявляють H01/H02/BUD-D15. Це свідомо зафіксована втрата чутливості, не загальна гарантія покриття. [Хронологія](../evidence/calibration-amendment-intent.json), [V1/V2 і samples](../evidence/budget-calibration.json).

Контроль без summary: provider median clean USD 0.00193182, lesson-05 USD 0.00199224; із summary 2 — USD 0.00283646/0.00298998. По 5 незалежних повторів. На цих коротких діалогах summary не заощаджує кошти; довші діалоги не вимірювалися. [Звірка 4 прогнозів](forecast-review.md).

### Калібрування tokens_total · BUD-D15

| Варіант | Поріг | Clean median/verdict | Lesson-08 median/verdict |
|---|---|---|---|
| Занадто вільний | 52787 | 44884 / PASS | 52242 / PASS |
| Занадто тісний | 43999 | 44884 / FAIL | 52242 / FAIL |
| Обраний | 47252 | 44884 / PASS | 52242 / FAIL |


Вільний/тісний варіанти — retrospective re-evaluation тих самих captures, не нові генерації. Обраний поріг frozen до final clean/lesson-08; запас 5% від незалежного calibration baseline. [Усі samples і запас](../evidence/budget-calibration.json).

**Залишковий ризик:** latency пороги залежать від локального instrumentation; місячний mix — припущення;5 повторів не доводять універсальність. Перезняти при зміні моделі/оточення. Semantic L09 і production capacity/hosting не вимірювалися. Точні raw докази зберігаються окремо.
