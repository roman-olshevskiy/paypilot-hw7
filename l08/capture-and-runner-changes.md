# Зміни до кіта для ДЗ7

Основа — повний tracked L03 7d0f5e7, поруч pinned L08 666e496 у l08/kit. Оригінальні репозиторії не редагувалися.

- L03 уже рахує діалогові токени й медіани; додано рівень1 для budget лише з identical_tool_calls_max, відповідну coverage L1/L2, budget_samples у звіт і коректні headline tokens/median latency. Вердикт budget не замінено іншою метрикою.
- STAND_DIR у compose типово вказує на sibling paypilot-stand-shared; .env не переноситься.
- L08 run_dialog.py byte-identical до upstream. У prices.json уточнено effective Gemini write-factor після пілота (catalog write+read для overlapping buckets); початкові raw пілота не перераховано.
- hw7_capture обгортає native CLI, записує response до trace, виклики й невдалі спроби; після кожного кроку зберігає стан disputes. Не додає chat retries. Native L08 має власні до3 спроб на500; вони лишаються видимими.
- Independent clean calibration не змішано з фінальними repeat. Пороги frozen і закомічені до фінальних clean/lesson-08. Для D15 правило5% обрано за пілотом до власних замірів; інші15%, latency100%.
- Первинні raw JSON зберігаються без нормалізації EOL; JSONL freeze має LF на Windows/Linux. Offline перевірки включають ранні ходи, canonical arguments, median проти sum і втрату trace після оплаченої відповіді.
- verify_docker_clone виконує реальні native budget-серії через Docker у чистому клоні й зберігає їх окремо. verify_replay — додаткова мережева ізоляція й відтворення, не заміна живих результатів.
