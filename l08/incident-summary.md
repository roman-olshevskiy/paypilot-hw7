# B3 — локалізація втрати даних

Умова: lesson-05, summarize_after2; repeat2 із5. Сесія bf9eef73b800, крок3 request baa778f48bb04937. Вихідний trace незмінний.

| Крок | Спан | Факт | Розбіжність |
|---|---|---|---|
| 1–2 | llm.call / tool results | У діалозі встановлено TX-0401,240 EUR і duplicate_charge | Сутності ще присутні |
| **3** | **agent.summarize** | **summary.input містить TX-0401 і duplicate_charge; summary.text нижче — без них** | **Перша документована втрата на виході стиснення; reason змінено на service_not_rendered** |
| 3 | наступний llm.call | Генерація отримує спотворений summary замість повної справи | Пошкоджені дані вже в контексті |
| 4 | llm.call / tools | tool.get_account, tool.get_transactions | Поведінка після втрати не замінює доказ самого місця втрати |

Для регулятора: на кроці3 спан agent.summarize зберіг на вході TX-0401/duplicate_charge, але видав переказ без номера транзакції та з іншим reason code.

Дослівний вихід summary:

~~~text
**Summary of conversation (for reference):**

- **Customer:** Danylo Kovalenko (CUS-0004), EUR account.
- **Intent:** Customer believes they were charged twice by the same online merchant and wants to dispute the duplicate.
- **Topic:** Duplicate card charge dispute from TechMart Online. Transactions were checked and the later charge was identified as the duplicate.
- **Status:** Eligibility check passed for the service_not_rendered reason. The dispute has not been filed yet. Awaiting the customer's explicit confirmation before filing, since it is irreversible.
- **Time-sensitive:** The filing deadline is close (about 3 days from the conversation date).
~~~

[Повний вхід/вихід і IDs](../evidence/incident.json) · [первинні captures](../evidence/runs/20261027T220440252303Z-full-b3-4903b6/captures.json).
У повній серії clean summary_contains5/5; lesson-05 —0/5. Не всі дефектні перекази губили обидві сутності: частина зберегла TX-0401, але втратила duplicate_charge.
