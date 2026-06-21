#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorldCupNewsAgent run 2026-06-21.
8 articles (5 news < 12h, 3 trend KZ/CIS): build Russian Markdown bodies,
download + optimize cover images to 16:9 (letterbox on blurred bg so faces
are never centre-cropped), base64-upload, POST to Sport Arena Hub, then log.
"""
import base64, io, json, os, re, urllib.request, urllib.error
from datetime import datetime, timezone

RUN_ID   = "run-20260621-wc2026-groupstage"
SECRET   = os.environ["AGENT_PUBLISH_SECRET"]
ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
ROOT     = "/home/user/worldcup-news-editor"

from PIL import Image, ImageFilter

# ── Cover images (Wikimedia Commons, CC-licensed, real photos) ───────────────
IMAGES = {
    "undav":    "https://upload.wikimedia.org/wikipedia/commons/2/22/Deniz_Undav_%28middle%29_at_BHA_5_v_Espanyol_1_pre_season_30_07_2022_39_%28cropped%29.jpg",
    "advocaat": "https://upload.wikimedia.org/wikipedia/commons/a/a4/Dick_Advocaat_2011_Russia.jpg",
    "gakpo":    "https://upload.wikimedia.org/wikipedia/commons/9/93/Cody_Gakpo_04012026_%281%29.jpg",
    "yamal":    "https://upload.wikimedia.org/wikipedia/commons/d/df/Lamine_Yamal_in_2025_%28cropped2%29.jpg",
    "ueda":     "https://upload.wikimedia.org/wikipedia/commons/9/99/Go_Ahead_Eagles_-_Feyenoord_-_53679351240_%28Ayase_Ueda%29.jpg",
    "ronaldo":  "https://upload.wikimedia.org/wikipedia/commons/5/5b/Cristiano_Ronaldo_Portugal_vs_Brazil.jpg",
    "messi":    "https://upload.wikimedia.org/wikipedia/commons/e/e6/FWC_2018_-_Group_D_-_ARG_v_ISL_-_Messi_penalty_kick.jpg",
    "metlife":  "https://upload.wikimedia.org/wikipedia/commons/d/d1/MetLife_Stadium%2C_East_Rutherford_New_Jersey.jpg",
}


def fetch(url: str) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "WorldCupNewsAgent/1.0 (almaznis1@gmail.com)"})
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.read()
    except Exception as exc:
        print(f"  ✗ download failed {url}: {exc}")
        return None


def to_169_b64(raw: bytes) -> str | None:
    """Fit image into 1600x900 16:9 over a blurred 'cover' background so the
    subject stays fully visible and centred (no face cropping on the site's
    centre-crop). Re-encode JPEG ~82%, strip EXIF."""
    try:
        im = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as exc:
        print(f"  ✗ open failed: {exc}")
        return None
    W, H = 1600, 900
    # background: cover-crop + blur
    sc = max(W / im.width, H / im.height)
    bg = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    left = (bg.width - W) // 2
    top = (bg.height - H) // 2
    bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(28))
    # foreground: contain
    sc2 = min(W / im.width, H / im.height)
    fg = im.resize((max(1, int(im.width * sc2)), max(1, int(im.height * sc2))), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    out = io.BytesIO()
    bg.save(out, format="JPEG", quality=82, optimize=True)
    data = out.getvalue()
    print(f"    → cover {len(data)//1024} KB (1600x900)")
    return base64.b64encode(data).decode("ascii")


print("Preparing cover images…")
COVERS = {}
for key, url in IMAGES.items():
    raw = fetch(url)
    COVERS[key] = to_169_b64(raw) if raw else None
    print(f"  {key}: {'ok' if COVERS[key] else 'MISSING'}")

SRC = "\n\n> Источники: "

# ── Articles ─────────────────────────────────────────────────────────────────
ARTICLES = []

# 1 — Germany 2:1 Ivory Coast (news, match_report)
ARTICLES.append({
"title": "Германия 2:1 Кот-д'Ивуар: Дениз Ундав выходит на замену и вырывает победу на 94-й минуте",
"slug": "germany-2-1-ivory-coast-undav-world-cup-2026",
"category": "Отчёты о матчах",
"type": "match_report",
"source_type": "news",
"image_key": "undav",
"excerpt": "Дениз Ундав вышел на замену и оформил дубль, включая победный гол на 94-й минуте, – Германия обыграла Кот-д'Ивуар 2:1 и впервые с 2014 года вышла в плей-офф чемпионата мира.",
"sources": [
 "https://www.espn.com/soccer/story/_/id/49129600/germany-ivory-coast-2026-fifa-world-cup-deniz-undav",
 "https://www.skysports.com/football/germany-vs-ivory-coast/549798",
 "https://www.aljazeera.com/sports/liveblog/2026/6/20/germany-vs-ivory-coast-live-world-cup-2026",
 "https://theanalyst.com/articles/germany-vs-ivory-coast-stats-world-cup-2026"],
"body": """Сборная Германии одержала волевую победу над Кот-д'Ивуаром – 2:1 – в матче группы E чемпионата мира 2026 года на стадионе «БМО Филд» в Торонто. Героем встречи стал нападающий Дениз Ундав: он вышел на замену во втором тайме и забил оба мяча своей команды, причём решающий – уже на 94-й минуте. Этот результат вывел немцев в плей-офф мирового первенства впервые с 2014 года.

## Кот-д'Ивуар повёл в первом тайме
Первый тайм остался за африканской командой. На 30-й минуте капитан «слонов» Франк Кесси открыл счёт после подачи Яна Диоманде с фланга: мяч прошёл через штрафную, и Кесси хладнокровно пробил мимо вратаря – 0:1. До перерыва команда Жулиана Нагельсманна так и не нашла ответа, выглядела нервозно и проигрывала по движению.

## Замена, изменившая ход игры
Перелом наступил после выхода Ундава. На 68-й минуте Надием Амири отправил длинную передачу вперёд: Кай Хаверц не дотянулся до мяча, зато за его спиной оказался Ундав, который мощно пробил в сетку – 1:1. А в компенсированное время, на 94-й минуте, Феликс Нмеча выдал точный пас в штрафную, где Ундав в касание развернулся и нанёс победный удар – 2:1.

По данным ESPN, Ундав стал четвёртым игроком в истории чемпионатов мира, который, выйдя на замену, забил в одном матче и сравнивающий, и победный голы.

## Ключевые события матча

| Минута | Команда | Событие | Автор |
|---|---|---|---|
| 30' | Кот-д'Ивуар | Гол (0:1) | Франк Кесси |
| 68' | Германия | Гол (1:1) | Дениз Ундав |
| 90+4' | Германия | Гол (2:1) | Дениз Ундав |

## Лучший игрок
Без сомнений – Дениз Ундав. Форвард провёл на поле меньше получаса, но именно его выход перевернул матч и принёс сборной Германии путёвку в раунд плей-офф. Для Нагельсманна это важный сигнал: у команды есть глубина состава и игрок, способный решать судьбу матчей со скамейки.

«Германия снова умеет добывать результат на характере», – отмечает Sky Sports, подчёркивая, что поздний гол Ундава стал самым драматичным эпизодом тура.

Источники: ESPN, Sky Sports, Al Jazeera, The Analyst (Opta)."""
})

# 2 — Curaçao 0:0 Ecuador, Eloy Room record (news, transfer/brief)
ARTICLES.append({
"title": "Кюрасао творит историю: Элой Ром отразил 15 ударов и принёс самой маленькой стране ЧМ первое очко",
"slug": "curacao-eloy-room-15-saves-record-world-cup-2026",
"category": "ЧМ-2026",
"type": "transfer",
"source_type": "news",
"image_key": "advocaat",
"excerpt": "Вратарь Кюрасао Элой Ром отразил 15 ударов в матче с Эквадором (0:0) и помог самой маленькой стране в истории чемпионатов мира завоевать первое очко.",
"sources": [
 "https://www.skysports.com/football/news/29910/13553789/world-cup-2026-ecuador-0-0-curacao-eloy-room-makes-history-with-incredible-15-saves-to-earn-blue-wave-first-ever-point",
 "https://www.aljazeera.com/sports/2026/6/21/room-the-hero-as-tiny-curacao-earn-first-world-cup-point-against-ecuador",
 "https://sports.yahoo.com/soccer/article/2026-world-cup-eloy-rooms-15-save-masterclass-helps-curacao-stun-ecuador-in-0-0-draw-020003395.html",
 "https://www.espn.com/soccer/story/_/id/49128614/ecuador-curacao-live-world-cup-2026-latest-updates-commentary-score-result"],
"body": """Кюрасао – самая маленькая по населению страна, когда-либо выступавшая на чемпионате мира, – добыла историческое первое очко в своём дебютном турнире, сыграв вничью с Эквадором 0:0 в матче группы F. Главным творцом сенсации стал вратарь Элой Ром, отразивший невероятные 15 ударов.

По информации Sky Sports, 15 сэйвов Рома – наибольшее число для голкипера в матче чемпионата мира без учёта дополнительного времени с тех пор, как ведётся подобная статистика (с 1966 года). До абсолютного рекорда вратарю не хватило всего одного отражённого удара: 16 сэйвов в одном матче в 2014 году провёл американец Тим Ховард в игре 1/8 финала против Бельгии.

Эквадор всю встречу шёл вперёд и нанёс, по данным изданий, 28 ударов по воротам, однако пробить Рома так и не сумел. «Голубая волна» выстояла и записала на свой счёт первое очко в истории выступлений на мировых первенствах.

## Адвокат и связь с СНГ
Сборную Кюрасао возглавляет опытный нидерландский специалист Дик Адвокат, хорошо знакомый болельщикам в СНГ: в своё время он работал с петербургским «Зенитом» и национальной сборной России. Под его руководством островная команда сыграла дисциплинированно в обороне и поймала свой шанс в матче с фаворитом группы.

> Как отмечает Al Jazeera, ничья Кюрасао с Эквадором стала одной из самых ярких историй группового этапа: крошечная карибская сборная доказала, что на этом турнире нет проходных соперников.

Источники: Sky Sports, Al Jazeera, Yahoo Sports, ESPN."""
})

# 3 — Netherlands 5:1 Sweden (news, match_report)
ARTICLES.append({
"title": "Нидерланды 5:1 Швеция: дубли Гакпо и Броббея отправляют «оранжевых» на вершину группы F",
"slug": "netherlands-5-1-sweden-world-cup-2026",
"category": "Отчёты о матчах",
"type": "match_report",
"source_type": "news",
"image_key": "gakpo",
"excerpt": "Брайан Броббей и Коди Гакпо оформили по дублю, и сборная Нидерландов разгромила Швецию 5:1, возглавив группу F на чемпионате мира 2026 года.",
"sources": [
 "https://www.skysports.com/football/netherlands-vs-sweden/report/549800",
 "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/netherlands-sweden-match-report-highlights",
 "https://sports.yahoo.com/articles/dumfries-shines-netherlands-thrash-sweden-022336878.html",
 "https://www.espn.com/soccer/report/_/gameId/760447"],
"body": """Сборная Нидерландов разгромила Швецию 5:1 в матче группы F чемпионата мира 2026 года в Хьюстоне и поднялась на первое место в квартете. Дубли оформили Брайан Броббей и Коди Гакпо, ещё один мяч на счету вышедшего на замену Кристалла Саммервилла.

## Быстрый старт «оранжевых»
Нидерланды захватили инициативу с первых минут. Уже на 5-й минуте Броббей открыл счёт после низкой передачи Гакпо, а ближе к 17-й минуте оформил дубль – на сей раз с подачи активного Дензела Дюмфриса справа. К перерыву подопечные сохраняли комфортное преимущество 2:0.

## Гакпо солирует во втором тайме
После перерыва инициативу перехватил Гакпо. На 47-й минуте он замкнул очередную передачу Дюмфриса, а на 54-й оформил дубль, мощно пробив после комбинации с участием Саммервилла. Швеция размочила счёт на 59-й минуте – Энтони Эланга реализовал выход, организованный Александером Исаком. Точку в матче на 89-й минуте поставил Саммервилл, забивший второй мяч на турнире.

## Ключевые события матча

| Минута | Команда | Событие | Автор |
|---|---|---|---|
| 5' | Нидерланды | Гол (1:0) | Брайан Броббей |
| 17' | Нидерланды | Гол (2:0) | Брайан Броббей |
| 47' | Нидерланды | Гол (3:0) | Коди Гакпо |
| 54' | Нидерланды | Гол (4:0) | Коди Гакпо |
| 59' | Швеция | Гол (4:1) | Энтони Эланга |
| 89' | Нидерланды | Гол (5:1) | Кристалл Саммервилл |

## Лучший игрок
Коди Гакпо с дублем и результативной игрой стал главной фигурой атаки, однако в Нидерландах особо выделяют Дензела Дюмфриса: латераль отдал две голевые передачи и был мотором правого фланга. Как пишет Sky Sports, эта победа позволяет «оранжевым» самим решать свою судьбу в заключительном туре группы против Туниса.

Источники: Sky Sports, FIFA, Yahoo Sports, ESPN."""
})

# 4 — Spain vs Saudi Arabia preview (news, preview)
ARTICLES.append({
"title": "Превью: Испания – Саудовская Аравия. «Красная фурия» под давлением после ничьей с Кабо-Верде",
"slug": "spain-vs-saudi-arabia-preview-world-cup-2026",
"category": "Сборные",
"type": "preview",
"source_type": "news",
"image_key": "yamal",
"excerpt": "Испания после неожиданной нулевой ничьей с Кабо-Верде обязана побеждать Саудовскую Аравию во втором туре группы H чемпионата мира 2026 года. Превью, расклады и прогноз.",
"sources": [
 "https://www.espn.com/soccer/story/_/id/49118145/fifa-world-cup-2026-spain-vs-saudi-arabia-tv-channel-how-watch-kickoff-live-stream-referee-predicted-lineups",
 "https://theanalyst.com/articles/spain-vs-saudi-arabia-prediction-world-cup-2026-match-preview",
 "https://sports.yahoo.com/articles/spain-vs-saudi-arabia-world-030000544.html"],
"body": """Сборная Испании проводит ключевой матч второго тура группы H чемпионата мира 2026 года: «Красная фурия» встречается с Саудовской Аравией на «Мерседес-Бенц Стэдиум» в Атланте. После сенсационной нулевой ничьей с дебютантами из Кабо-Верде в стартовом туре команда обязана побеждать, чтобы не превратить выход из группы в нервную лотерею.

## Турнирная ситуация: группа H открыта
Группа H после первого тура сложилась максимально плотно. Испания не сумела обыграть Кабо-Верде (0:0), а Саудовская Аравия добыла важное очко в матче с Уругваем (1:1). В итоге все четыре команды квартета набрали по одному очку – расклад максимально простой: фаворитам нужна победа.

| Команда | И | О |
|---|---|---|
| Испания | 1 | 1 |
| Уругвай | 1 | 1 |
| Саудовская Аравия | 1 | 1 |
| Кабо-Верде | 1 | 1 |

## История встреч
По данным статистиков, испанцы выигрывали все три предыдущие очные встречи с Саудовской Аравией, забив девять мячей и пропустив лишь два. В их единственном матче на чемпионатах мира – на групповом этапе турнира 2006 года – «Красная фурия» победила 1:0.

При этом саудовцы уже умеют огорчать грандов: на ЧМ-2022 они сенсационно обыграли действующих на тот момент чемпионов мира из Аргентины, а в нынешнем турнире удержали ничью с Уругваем благодаря дисциплине в обороне и блестящей игре ветерана-вратаря Мохаммеда Аль-Овайса.

## Ключевые игроки
В составе Испании всё внимание – на юном вундеркинде Ламине Ямале, который, по информации ESPN, готов выйти в стартовом составе после того, как против Кабо-Верде провёл на поле заключительные минуты. Усилить атаку может и Нико Уильямс. У Саудовской Аравии главная надежда снова связана с вратарём Аль-Овайсом, который тащил свою команду в матче с Уругваем.

## Прогноз
Суперкомпьютер Opta считает Испанию безоговорочным фаворитом: вероятность победы «Красной фурии» оценивается примерно в 86,7%, тогда как шансы саудовцев – лишь около 4,3%, а ничьей – порядка 9%. Тем не менее старт турнира показал, что аутсайдеры группы H способны удивлять, и испанцам придётся приложить максимум усилий, чтобы взломать насыщенную оборону соперника.

Источники: ESPN, The Analyst (Opta), Yahoo Sports."""
})

# 5 — Japan 4:0 Tunisia (news, match_report)
ARTICLES.append({
"title": "Япония 4:0 Тунис: дубль Уэды в 1000-м матче в истории чемпионатов мира",
"slug": "japan-4-0-tunisia-world-cup-2026",
"category": "Отчёты о матчах",
"type": "match_report",
"source_type": "news",
"image_key": "ueda",
"excerpt": "Аясэ Уэда оформил дубль, и сборная Японии разгромила Тунис 4:0 в юбилейном, 1000-м матче в истории чемпионатов мира, приблизившись к плей-офф.",
"sources": [
 "https://www.skysports.com/football/tunisia-vs-japan/549801",
 "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/tunisia-japan-match-report-highlights",
 "https://www.espn.com/soccer/match/_/gameId/760449/japan-tunisia"],
"body": """Сборная Японии уверенно обыграла Тунис 4:0 в матче группы F чемпионата мира 2026 года на стадионе в Монтеррее. Дубль оформил нападающий Аясэ Уэда, ещё по голу забили Дайти Камада и Дзюнъя Ито. Эта встреча стала юбилейной – 1000-м матчем в истории чемпионатов мира.

## Ранний гол задал тон
Японцы открыли счёт уже на 4-й минуте: Кейто Накамура ворвался в штрафную и прострелил вдоль ворот, а Камада точно замкнул передачу. На 31-й минуте Уэда получил мяч на свободном пространстве и мощным ударом отправил его в дальний угол – 2:0.

## Контроль во втором тайме
После перерыва Япония довела дело до разгрома. На 69-й минуте Дзюнъя Ито спокойно переиграл вратаря Тунис Дахмена, а на 83-й Уэда оформил дубль, головой замкнув навес после фланговой комбинации с участием Сано – 4:0.

## Ключевые события матча

| Минута | Команда | Событие | Автор |
|---|---|---|---|
| 4' | Япония | Гол (1:0) | Дайти Камада |
| 31' | Япония | Гол (2:0) | Аясэ Уэда |
| 69' | Япония | Гол (3:0) | Дзюнъя Ито |
| 83' | Япония | Гол (4:0) | Аясэ Уэда |

## Что это значит
Победа позволила Японии подняться на второе место в группе F, опередив Швецию, и вплотную приблизиться к выходу в плей-офф. Для Туниса же поражение фактически означает конец борьбы за продолжение турнира – команда осталась на последней строчке квартета. Лучшим игроком встречи стал Аясэ Уэда, чей дубль во многом и решил исход юбилейного матча.

Источники: Sky Sports, FIFA, ESPN."""
})

# 6 — Uzbekistan vs Portugal preview (trend, preview)
ARTICLES.append({
"title": "Превью: Узбекистан – Португалия. Дебютанты ЧМ-2026 бросают вызов Роналду",
"slug": "uzbekistan-vs-portugal-preview-world-cup-2026",
"category": "Сборные",
"type": "preview",
"source_type": "trend",
"image_key": "ronaldo",
"excerpt": "23 июня сборная Узбекистана в своём дебютном чемпионате мира сыграет с Португалией Криштиану Роналду. Превью матча группы K, расклады и ключевые фигуры.",
"sources": [
 "https://www.skysports.com/football/news/12040/13543106/world-cup-2026-group-k-guide-fixtures-schedule-standings-and-odds-for-portugal-dr-congo-uzbekistan-and-colombia",
 "https://www.aljazeera.com/sports/2026/6/18/what-went-wrong-for-cristiano-ronaldo-in-his-first-world-cup-2026-match",
 "https://en.wikipedia.org/wiki/Uzbekistan_at_the_FIFA_World_Cup",
 "https://www.foxsports.com/stories/soccer/uzbekistan-world-cup-2026-schedule-locations-dates-times"],
"body": """Один из самых ожидаемых матчей для болельщиков Центральной Азии и всего СНГ состоится 23 июня в Хьюстоне: сборная Узбекистана в рамках группы K сыграет с Португалией Криштиану Роналду. Для узбекской команды это второй матч в истории выступлений на чемпионатах мира – и шанс добыть первые очки на мировом первенстве.

## Узбекистан: дебют со знаком плюс, несмотря на поражение
В стартовом туре сборная Узбекистана уступила Колумбии со счётом 1:3, однако оставила приятное впечатление. Историческим стал момент на 60-й минуте: полузащитник Аббосбек Файзуллаев ударом головой сравнял счёт и забил первый в истории гол узбекской сборной на чемпионатах мира. Файзуллаев, выступающий за московский ЦСКА, хорошо знаком болельщикам в России и СНГ и считается главной звездой этой команды.

## Португалия буксует на старте
Для Португалии турнир начался с разочарования: в первом туре подопечные дрогнули и сыграли вничью с ДР Конго 1:1. Жуан Невеш вывел европейцев вперёд, но Йоан Висса ещё до перерыва восстановил равновесие. Криштиану Роналду, ставший, по данным Al Jazeera, самым возрастным полевым игроком в истории, выходившим в стартовом составе на матч чемпионата мира, провёл встречу не лучшим образом: нанёс три удара, и все – мимо. На фоне потери очков на Роналду и партнёров обрушилась критика, так что португальцам нужна победа, чтобы не осложнить себе выход из группы.

## Турнирная ситуация в группе K

| Команда | И | О |
|---|---|---|
| Колумбия | 1 | 3 |
| Португалия | 1 | 1 |
| ДР Конго | 1 | 1 |
| Узбекистан | 1 | 0 |

## Ключевые фигуры
У Португалии всё внимание приковано к Роналду и молодому полузащитнику Жуану Невешу, забившему в первом туре. У Узбекистана главные надежды связаны с Файзуллаевым и опытным форвардом Эльдором Шомуродовым, способным зацепиться за мяч впереди.

## Прогноз
На бумаге Португалия – явный фаворит, но старт турнира показал, что европейцы уязвимы, а узбекская команда умеет играть смело. Для подопечных из Центральной Азии даже достойная борьба с одним из грандов станет важным шагом, а очко в матче с Португалией превратилось бы в новую страницу истории узбекского футбола.

Источники: Sky Sports, Al Jazeera, Wikipedia, FOX Sports."""
})

# 7 — Top-7 Golden Boot (trend, ranking)
ARTICLES.append({
"title": "Топ-7 бомбардиров ЧМ-2026: Месси и Джонатан Дэвид возглавляют гонку за «Золотой бутсой»",
"slug": "top-7-scorers-golden-boot-world-cup-2026",
"category": "Тренды",
"type": "ranking",
"source_type": "trend",
"image_key": "messi",
"excerpt": "Лионель Месси и Джонатан Дэвид оформили хет-трики и возглавили гонку бомбардиров чемпионата мира 2026 года. Разбираем семёрку лидеров спора за «Золотую бутсу».",
"sources": [
 "https://www.goal.com/en/lists/world-cup-2026-golden-boot-standings-fifa-award/blt29fdba0896b8fd09",
 "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/adidas-golden-boot-race-top-scorer",
 "https://www.foxsports.com/stories/soccer/2026-fifa-world-cup-golden-boot-tracker"],
"body": """Групповой этап чемпионата мира 2026 года в самом разгаре, а гонка за «Золотой бутсой» уже подарила болельщикам два хет-трика и целую россыпь звёздных имён. Награда adidas Golden Boot достаётся лучшему бомбардиру турнира; при равенстве голов в расчёт идут результативные передачи, а затем – меньшее число сыгранных минут. Разбираем семёрку лидеров на данный момент.

## 1. Лионель Месси (Аргентина) – 3 гола
Капитан сборной Аргентины ворвался в турнир с хет-триком и единолично возглавил список бомбардиров. Месси в очередной раз доказывает, что и в зрелом возрасте остаётся решающим игроком для действующих чемпионов мира. Для болельщиков в СНГ матчи аргентинца – одно из главных украшений турнира.

## 2. Джонатан Дэвид (Канада) – 3 гола
Форвард сборной Канады стал главным открытием старта: он также оформил хет-трик и догнал Месси по числу голов. Дэвид ведёт хозяев турнира вперёд и подтверждает статус одного из самых хладнокровных нападающих своего поколения.

## 3. Килиан Мбаппе (Франция) – 2 гола
Лидер сборной Франции забил два мяча и держится в группе преследователей. Мбаппе традиционно считается одним из фаворитов спора за «Золотую бутсу», и его скорость остаётся головной болью для любой обороны.

## 4. Эрлинг Холанд (Норвегия) – 2 гола
Норвегия впервые за десятилетия играет на чемпионате мира, и Холанд сразу же отметился двумя голами. Мощный форвард – главный символ возвращения «викингов» на большую сцену.

## 5. Гарри Кейн (Англия) – 2 гола
Капитан сборной Англии стабильно поражает ворота и записал на свой счёт два мяча. Кейн остаётся ключевой фигурой в атаке «Трёх львов» и одним из самых опытных снайперов турнира.

## 6. Кай Хаверц (Германия) – 2 гола
Нападающий сборной Германии забил дважды и помогает команде решать турнирные задачи. Хаверц добавляет атаке немцев вариативности и регулярно оказывается в нужном месте.

## 7. Фоларин Балогун (США) – 2 гола
Форвард сборной США оформил два гола и ведёт хозяев чемпионата вперёд. Балогун – одно из лиц молодой американской команды, мечтающей о большом результате на домашнем турнире.

## Кто ещё в гонке
По данным Goal.com и FIFA, на отметке в два мяча также расположились Сайл Ларин (Канада), Илайджа Джаст (Новая Зеландия), Йохан Манзамби (Швейцария) и Ясин Аяри (Швеция). С учётом плотности группового этапа расклад в гонке за «Золотой бутсой» ещё не раз изменится.

Источники: Goal.com, FIFA, FOX Sports."""
})

# 8 — Top-5 sensations (trend, ranking)
ARTICLES.append({
"title": "Топ-5 сенсаций группового этапа ЧМ-2026: фавориты буксуют, аутсайдеры гремят",
"slug": "top-5-sensations-group-stage-world-cup-2026",
"category": "Тренды",
"type": "ranking",
"source_type": "trend",
"image_key": "metlife",
"excerpt": "Кабо-Верде против Испании, Роналду без победы, рекордно быстрые голы и вылет Турции – собрали пять главных сенсаций группового этапа чемпионата мира 2026 года.",
"sources": [
 "https://www.aljazeera.com/sports/2026/6/20/morocco-beat-scotland-1-0-as-saibari-scores-fastest-world-cup-2026",
 "https://www.aljazeera.com/sports/2026/6/20/turkiye-knocked-out-of-world-cup-2026-after-1-0-defeat-to-10-man-paraguay",
 "https://www.espn.com/soccer/story/_/id/49118145/fifa-world-cup-2026-spain-vs-saudi-arabia-tv-channel-how-watch-kickoff-live-stream-referee-predicted-lineups",
 "https://bleacherreport.com/articles/25441794-ronaldo-portugal-draw-congo-final-match-stats-highlights-world-cup-group-k-scenarios"],
"body": """Расширенный до 48 команд чемпионат мира 2026 года с первых дней подарил болельщикам массу сюрпризов: фавориты теряют очки, дебютанты дают бой грандам, а рекорды по скорости голов переписываются почти ежедневно. Собрали пять главных сенсаций группового этапа на данный момент.

## 1. Кабо-Верде 0:0 Испания
Дебютанты из Кабо-Верде сумели сделать то, что не удавалось многим грандам, – удержать нулевую ничью против одного из главных фаворитов турнира. «Красная фурия» владела мячом, но так и не нашла ключей к насыщенной обороне «голубых акул». Для крошечной островной сборной это очко стало историческим.

## 2. ДР Конго 1:1 Португалия
Португалия Криштиану Роналду неожиданно потеряла очки уже в стартовом туре, сыграв вничью с вернувшейся на мировое первенство ДР Конго. Жуан Невеш вывел европейцев вперёд, но Йоан Висса восстановил равновесие, принеся африканцам первый балл. Роналду, по данным Bleacher Report, провёл матч неудачно и попал под волну критики.

## 3. Саудовская Аравия 1:1 Уругвай
Саудовская Аравия продолжает традицию громких результатов на чемпионатах мира: на сей раз команда зацепилась за ничью с Уругваем. Снова героем стал ветеран-вратарь Мохаммед Аль-Овайс, чья игра позволила саудовцам увезти важное очко из матча с южноамериканским грандом.

## 4. Парагвай 1:0 Турция
Парагвай не только обыграл Турцию, но и переписал рекорд турнира по скорости гола: Матиас Галарса отличился уже на 64-й секунде. Более того, парагвайцы провели почти весь второй тайм в меньшинстве после удаления Альмирона, но довели победу до конца. Для Турции же это поражение обернулось вылетом с турнира после двух туров.

## 5. Марокко 1:0 Шотландия
Полуфиналисты прошлого чемпионата мира из Марокко продолжают свой путь: «Атласские львы» дожали Шотландию благодаря голу Исмаэля Саибари уже на 71-й секунде – на тот момент это был самый быстрый мяч турнира. Шотландцы вновь не сумели реализовать свой шанс на большой сцене, а Марокко перехватило контроль над группой C.

Источники: Al Jazeera, ESPN, Bleacher Report."""
})

# ── Attach optimized covers ──────────────────────────────────────────────────
for a in ARTICLES:
    a["image_base64"] = COVERS.get(a["image_key"])
    a["image_url"] = None

# sanity
assert len(ARTICLES) == 8, "need exactly 8"
assert sum(1 for a in ARTICLES if a["source_type"] == "news") == 5
assert sum(1 for a in ARTICLES if a["source_type"] == "trend") == 3
for a in ARTICLES:
    assert "—" not in (a["title"] + a["excerpt"] + a["body"]), f"em dash in {a['slug']}"
    assert a["image_base64"], f"missing cover for {a['slug']}"

# ── Local archive ────────────────────────────────────────────────────────────
for a in ARTICLES:
    src = "news" if a["source_type"] == "news" else "trend"
    d = os.path.join(ROOT, "articles", f"{src}-{a['slug']}")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{src}-{a['slug']}.md"), "w", encoding="utf-8") as f:
        f.write(f"# {a['title']}\n\n_{a['excerpt']}_\n\n{a['body']}\n")

# ── Build payload (strip helper key) ─────────────────────────────────────────
def payload_obj(a):
    return {k: a[k] for k in ("title","slug","body","excerpt","category","type","image_url","image_base64","sources","source_type")}

def post(items):
    body = json.dumps({"articles": [payload_obj(a) for a in items]}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("x-agent-secret", SECRET)
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())

print(f"\nPublishing {len(ARTICLES)} articles…")
try:
    resp = post(ARTICLES)
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:600]}")
    raise
results = resp.get("results", [])
for it in results:
    print(f"  {'✓' if it.get('status')=='inserted' else '✗'} {it.get('slug')} [{it.get('status')}]" + (f" ERR {it.get('error')}" if it.get('error') else ""))

# retry errors once
errs = [it.get("slug") for it in results if it.get("status") != "inserted"]
if errs:
    retry = [a for a in ARTICLES if a["slug"] in errs]
    print(f"\nRetrying {len(retry)} failed…")
    r2 = post(retry).get("results", [])
    for it in r2:
        print(f"  {'✓' if it.get('status')=='inserted' else '✗'} {it.get('slug')} [{it.get('status')}]")
    # merge
    by = {it.get("slug"): it for it in results}
    for it in r2:
        by[it.get("slug")] = it
    results = list(by.values())

# ── Logging ──────────────────────────────────────────────────────────────────
res_by_input = {}
for it in results:
    s = it.get("slug","")
    base = re.sub(r"-\d+$","",s)
    res_by_input.setdefault(base, it)

ts = datetime.now(timezone.utc).isoformat()
log_path = os.path.join(ROOT, "logs", "articles-history.jsonl")
inserted_slugs = []
with open(log_path, "a", encoding="utf-8") as f:
    for a in ARTICLES:
        it = res_by_input.get(a["slug"], {})
        if it.get("status") == "inserted":
            inserted_slugs.append(it.get("slug"))
        entry = {
            "timestamp": ts, "run_id": RUN_ID,
            "publish_status": it.get("status","unknown"),
            "db_id": it.get("id"), "db_slug": it.get("slug"),
            "source_type": a["source_type"], "type": a["type"],
            "title": a["title"], "slug": a["slug"], "category": a["category"],
            "topic": a["excerpt"][:160],
            "image_url": it.get("image_url") or a.get("image_url"),
            "has_cover": True,
            "sources": a["sources"],
        }
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

with open(os.path.join(ROOT,"logs","last-run.json"),"w",encoding="utf-8") as f:
    json.dump({"run_id":RUN_ID,"generated_at":ts,"count":len(ARTICLES),
               "news":5,"trend":3,
               "inserted":len(inserted_slugs),
               "slugs":[a["slug"] for a in ARTICLES],
               "db_slugs":inserted_slugs}, f, ensure_ascii=False, indent=2)

print(f"\nInserted {len(inserted_slugs)}/8. Logs updated.")
# save manifest for final output
with open("/tmp/manifest_20260621.json","w",encoding="utf-8") as f:
    json.dump({"generated_at":ts,"run_id":RUN_ID,
               "articles":[{**payload_obj(a),"image_base64": ("<base64 %d bytes>"%len(a["image_base64"])) } for a in ARTICLES]},
              f, ensure_ascii=False, indent=2)
print("Done.")
