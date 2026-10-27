# Пілот і прайс

Пілот B1/B2 Haiku та B1 baseline Gemini завершено:20 chat-кроків, повні response/trace/state captures. B1 clean PASS, D14 FAIL identical calls8; B2 clean/defect single-run median6374/7148 проти6500. Це пілот, не5/5.

У Gemini catalog cache-write USD0.083333333/M і cache-read USD0.03/M. Перший span одночасно звітує1481 read і1481 write. За observed provider cost запис включає обидві складові: effective write USD0.113333333/M. При cache_write_inside_read=true read bucket зменшується на write, тому write_factor=(0.083333333+0.03)/0.30=0.3777777778. До пілота спроба застосувати лише catalog write дала недооблік USD0.00004443; сирий пілот не переписано. Для повних серій виправлено фактор до ефективної ціни, без підгонки модельних токенів.

Пілот Haiku B1 root/trace≈USD0.002488, B2≈USD0.010051, Gemini baseline≈USD0.000643. Для повної матриці B4+B3+6 budget-кейсів і окремого clean калібрування плановий резерв USD1.50 (не очікуване списання й не hard cap); за спостережуваною ціною основна оцінка нижча за USD1.00, але D14 Gemini/повтори500 можуть збільшити її. ДоступноUSD9.96 за підтвердженням до запусків. За прямою вказівкою виконання продовжується без проміжного billing review; фінальна точна звірка наприкінці.
