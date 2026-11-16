# Правки текстов — список мест

Все тексты сайта лежат в одном файле: `tools/content.py`. Каждое место ниже помечено в файле комментарием `# ПРАВКА N`.

## Как править прямо в браузере, без программ

1. Откройте файл на GitHub: https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py
2. Нажмите карандаш «Edit this file» справа сверху.
3. Нажмите Ctrl+F (на Mac — Cmd+F) и ищите `ПРАВКА 1`, `ПРАВКА 2` и так далее.
4. Замените текст внутри кавычек `'…'` на нужный. Кавычки, запятые и скобки не трогайте.
   Если в тексте есть апостроф, используйте типографский `’`, а не `'`.
5. Нажмите зелёную кнопку «Commit changes».
6. Страницы (HTML) обновятся после пересборки: попросите Claude «пересобери страницы» — он запустит `python3 tools/build.py` и отправит результат на GitHub.

## Список

| № | Страница | Что поправить и откуда взять текст | Строка |
|---|---|---|---|
| 1 | Все страницы | Шаг 2 (текст под «Підготовка довідки…») — на живом сайте | [строка 89](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L89) |
| 2 | Главная | 4 выгоды, 1-я — живой сайт | [строка 100](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L100) |
| 3 | Главная | 4 выгоды, 4-я — живой сайт | [строка 103](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L103) |
| 4 | Главная | «Про наш сервіс», 1-й абзац — ТЗ | [строка 107](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L107) |
| 5 | Меддовідки | Title — живой сайт | [строка 116](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L116) |
| 6 | Меддовідки | 4 выгоды, 1-я | [строка 121](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L121) |
| 7 | Меддовідки | Заголовок 1-го блока-списка — ТЗ | [строка 133](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L133) |
| 8 | Меддовідки | 1-й список, пункт 4 — ТЗ | [строка 139](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L139) |
| 9 | Меддовідки | 2-й список, пункт 1 — ТЗ | [строка 148](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L148) |
| 10 | Меддовідки | 2-й список, пункт 5 — ТЗ | [строка 152](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L152) |
| 11 | Меддовідки | Заголовок SEO-текста — ТЗ | [строка 157](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L157) |
| 12 | Меддовідки | SEO-текст, конец 1-го абзаца — ТЗ | [строка 159](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L159) |
| 13 | Меддовідки | SEO-текст, 3-й абзац — ТЗ | [строка 161](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L161) |
| 14 | Меддовідки | FAQ: вернуть вопрос «Як отримати довідку без візиту в лікарню?» и ответ 5-го вопроса — живой сайт | [строка 167](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L167) |
| 15 | Меддовідки | Таблица цен — живой сайт | [строка 129](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L129) |
| 16 | Довідка 063 | Description — живой сайт | [строка 173](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L173) |
| 17 | Довідка 063 | 4 выгоды, 1-я | [строка 177](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L177) |
| 18 | Довідка 063 | Текст под «Потрібна довідка 063?» — ТЗ | [строка 181](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L181) |
| 19 | Довідка 063 | Заголовок 1-го блока-списка — ТЗ | [строка 189](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L189) |
| 20 | Довідка 063 | SEO-текст, 1-й и 2-й абзацы — ТЗ | [строка 216](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L216) |
| 21 | Басейн | Description — живой сайт | [строка 232](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L232) |
| 22 | Басейн | 4 выгоды, 1-я | [строка 236](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L236) |
| 23 | Басейн | Текст под «Потрібна довідка для басейну?» — ТЗ | [строка 240](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L240) |
| 24 | Басейн | Последняя фраза 1-го блока-списка — ТЗ | [строка 257](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L257) |
| 25 | Басейн | FAQ: вернуть 3-й вопрос «Чи можна отримати довідку без особистого візиту до лікаря?» — живой сайт | [строка 281](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L281) |
| 26 | Медогляд 086 | 4 выгоды, 1-я | [строка 292](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L292) |
| 27 | Медогляд 086 | Заголовок 1-го блока-списка — ТЗ | [строка 304](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L304) |
| 28 | Медогляд 086 | 2-й список, пункты 1–2 — ТЗ | [строка 320](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L320) |
| 29 | Медогляд 086 | SEO-текст, 1-й абзац — ТЗ | [строка 330](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L330) |
| 30 | Флюорографія | Title — живой сайт | [строка 343](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L343) |
| 31 | Флюорографія | 4 выгоды, 1-я | [строка 348](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L348) |
| 32 | Флюорографія | Текст под «Потрібна довідка про флюорографію?» — ТЗ | [строка 352](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L352) |
| 33 | Флюорографія | 1-й список, последняя фраза — ТЗ | [строка 369](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L369) |
| 34 | Флюорографія | 2-й список, пункт 2 и «Результат» — ТЗ | [строка 376](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L376) |
| 35 | Флюорографія | Заголовок SEO-текста — ТЗ | [строка 384](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L384) |
| 36 | Флюорографія | SEO-текст, 1-й абзац — ТЗ | [строка 386](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L386) |
| 37 | Медкнижка | Title — живой сайт | [строка 399](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L399) |
| 38 | Медкнижка | 4 выгоды, 1-я | [строка 404](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L404) |
| 39 | Медкнижка | Текст под «Потрібна санітарна книжка?» — ТЗ | [строка 408](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L408) |
| 40 | Медкнижка | Заголовок 1-го блока-списка — ТЗ | [строка 416](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L416) |
| 41 | Медкнижка | 1-й список, пункты 1, 2, 4 — ТЗ | [строка 419](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L419) |
| 42 | Медкнижка | 1-й список, последняя фраза — ТЗ | [строка 425](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L425) |
| 43 | Медкнижка | 2-й список, пункт 2 и «Результат» — ТЗ | [строка 432](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L432) |
| 44 | Довідка водія | Title — живой сайт | [строка 456](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L456) |
| 45 | Довідка водія | 4 выгоды, 1-я и 3-я | [строка 461](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L461) |
| 46 | Довідка водія | 1-й список, пункт 5 — ТЗ | [строка 480](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L480) |
| 47 | Довідка водія | SEO-текст, 4-й абзац — ТЗ | [строка 502](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L502) |
| 48 | Довідка 100-2/о | 4 выгоды, 1-я | [строка 519](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L519) |
| 49 | Довідка 100-2/о | FAQ, 4-й ответ — живой сайт | [строка 566](https://github.com/ShocKKKKKKK/medvizyt-demo/blob/med-assistant/tools/content.py#L566) |

«ТЗ» — файл «ТЗ правки на med-assistant.txt» в папке заказчика на Google Drive, раздел этой страницы. «Живой сайт» — та же страница на med-assistant.net.
