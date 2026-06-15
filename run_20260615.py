#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WorldCupNewsAgent run for 2026-06-15: 8 articles (5 news + 3 trend)."""
import base64, json, os, io, time, urllib.parse, datetime
import requests
from PIL import Image, ImageFilter

RUN_ID   = "run-20260615-wc2026-day5"
SECRET   = os.environ["AGENT_PUBLISH_SECRET"]
ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
ROOT     = "/home/user/worldcup-news-editor"
UA       = "WorldCupNewsAgent/1.0 (almaznis1@gmail.com)"

# ── Cover images: Wikimedia Commons file names (CC-licensed) ─────────────────
COVERS = {
    "germany":  "1 kai havertz 2026.jpg",
    "yamal":    "Lamine Yamal in 2025.jpg",
    "sweden":   "1 Viktor Gyökeres 2026.jpg",
    "belgium":  "Kevin De Bruyne WC2022.jpg",
    "nether":   "20160604 AUT NED 8876 (cropped).jpg",
    "uzbek":    "James Rodriguez 2018.jpg",
    "ranking":  "Met Life Stadium.jpg",
    "portugal": "Cristiano Ronaldo 2018.jpg",
}

def filepath_url(name):
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(name)

def make_cover_b64(name):
    """Download a Commons image and render a 1600x900 (16:9) cover with a
    blurred fill so the subject is never face-cropped. Returns (b64, fallback_url)."""
    url = filepath_url(name)
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
        r.raise_for_status()
        src = Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception as e:
        print(f"  ! download/open failed for {name}: {e}")
        return None, url

    W, H = 1600, 900
    sw, sh = src.size
    # background: cover-crop + blur + slight darken
    scale = max(W / sw, H / sh)
    bg = src.resize((int(sw * scale), int(sh * scale)), Image.LANCZOS)
    left = (bg.width - W) // 2; top = (bg.height - H) // 2
    bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(28))
    bg = Image.eval(bg, lambda p: int(p * 0.72))
    # foreground: contain-fit, centered
    scale = min(W / sw, H / sh)
    fw, fh = int(sw * scale), int(sh * scale)
    fg = src.resize((fw, fh), Image.LANCZOS)
    bg.paste(fg, ((W - fw) // 2, (H - fh) // 2))

    for q in (85, 80, 74, 68, 60):
        buf = io.BytesIO()
        bg.save(buf, format="JPEG", quality=q, optimize=True)
        data = buf.getvalue()
        if len(data) <= 480_000:
            break
    print(f"  ok {name[:42]:42}  {len(data)//1024} KB  q={q}")
    return base64.b64encode(data).decode("ascii"), url

print("Building covers…")
COVER_B64 = {}
COVER_URL = {}
for k, fn in COVERS.items():
    b64, furl = make_cover_b64(fn)
    COVER_B64[k] = b64
    COVER_URL[k] = furl
    time.sleep(3.5)  # Wikimedia courtesy delay

# ── Articles ────────────────────────────────────────────────────────────────
A = []

A.append({
"key":"germany","source_type":"news","type":"match_report","category":"Отчёты о матчах",
"slug":"germany-7-1-curacao-world-cup-2026",
"title":"Германия 7:1 Кюрасао: Хаверц оформляет дубль, Бундестим становится самой результативной сборной в истории ЧМ",
"excerpt":"Германия разгромила дебютанта Кюрасао 7:1 в стартовом матче группы E чемпионата мира 2026 и вышла на первое место по числу забитых мячей в истории мировых первенств.",
"body":"""Германия уверенно открыла чемпионат мира 2026 года, разгромив дебютанта турнира Кюрасао со счётом 7:1 в матче группы E. Игра прошла 14 июня на «Эн-Эр-Джи Стэдиум» в Хьюстоне при 68 021 зрителе, и команда Юлиана Нагельсманна не оставила сопернику ни шанса.

## Как развивался матч

Бундестим открыла счёт уже на 6-й минуте: после передачи Флориана Вирца отличился Феликс Немеча. Кюрасао неожиданно сравнял счёт на 21-й минуте усилиями Ливано Коменсии, однако этот успех лишь раззадорил фаворита. Никлас Шлоттербек вернул преимущество на 38-й минуте, а в компенсированное к первому тайму время Кай Хаверц реализовал пенальти, заработанный после фола на Немече, – 3:1.

После перерыва игра окончательно перешла под контроль немцев. Джамал Мусиала забил уже на 47-й минуте, затем счёт нарастили Натаниэл Браун (68'), Дениз Ундав (78') и снова Кай Хаверц (88'), оформивший дубль. Итог – разгромные 7:1.

## Статистика матча

| Показатель | Германия | Кюрасао |
| --- | --- | --- |
| Голы | 7 | 1 |
| Авторы голов | Немеча (6'), Шлоттербек (38'), Хаверц (45+5' пен., 88'), Мусиала (47'), Браун (68'), Ундав (78') | Коменсия (21') |

## Исторический рекорд

Этот результат принёс Германии не только три очка. По информации FIFA и аналитического портала The Analyst, забитые в Хьюстоне мячи позволили Бундестим довести счётчик голов на чемпионатах мира до 239 и обойти Бразилию (238), став самой результативной сборной в истории мировых первенств.

Для Кюрасао же это был исторический дебют: карибский остров стал одной из самых маленьких по населению территорий, когда-либо пробивавшихся на чемпионат мира, а у руля команды стоит 78-летний нидерландский специалист Дик Адвокат.

> «Мы хотели мощно начать турнир и сделали это. Но впереди ещё много работы», – приводит слова из лагеря сборной Германии портал The Analyst.

В параллельном матче группы E Кот-д'Ивуар на последней минуте обыграл Эквадор 1:0, поэтому после первого тура немцы и ивуарийцы делят первое место.

Источники: FIFA.com, The Analyst, ESPN, Wikipedia.""",
"sources":[
 "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/germany-curacao-highlights-match-report",
 "https://theanalyst.com/articles/germany-vs-curacao-stats-world-cup-2026",
 "https://www.espn.com/soccer/report/_/gameId/760422",
 "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_E"]})

A.append({
"key":"yamal","source_type":"news","type":"transfer","category":"Новости игроков",
"slug":"lamine-yamal-fit-spain-world-cup-2026-debut",
"title":"Ламин Ямаль готов к дебюту на ЧМ-2026: «идеальная форма», но не на весь матч с Кабо-Верде",
"excerpt":"Главный тренер сборной Испании Луис де ла Фуэнте подтвердил, что Ламин Ямаль восстановился и готов дебютировать на чемпионате мира в матче против Кабо-Верде, однако проведёт на поле ограниченное время.",
"body":"""Сборная Испании получила важнейшую новость перед стартом чемпионата мира 2026 года: 18-летний вингер «Барселоны» Ламин Ямаль восстановился от повреждений и готов выйти на поле в дебютном матче группы H против Кабо-Верде 15 июня в Атланте.

Ямаль не играл с апреля из-за проблем с приводящей мышцей и повреждения задней поверхности бедра, и его готовность оставалась главной интригой испанского лагеря. По информации Al Jazeera и World Soccer Talk, главный тренер Луис де ла Фуэнте заявил, что игрок находится «в идеальном состоянии», но беречь его всё же будут.

> «Ламин в идеальной форме, но вряд ли проведёт весь матч. Мы будем действовать постепенно», – приводит слова де ла Фуэнте World Soccer Talk.

## План восстановления

Тренерский штаб готовит вундеркинда к плей-офф поэтапно. По данным источников, испанцы планируют дать Ямалю около 15–20 минут против Кабо-Верде, не менее 30 минут во втором матче с Саудовской Аравией и, возможно, поставить его в стартовый состав на заключительную игру группового этапа против Уругвая.

Хорошие новости пришли и по другому флангу: как сообщает ESPN, к полноценным тренировкам вернулся и Нико Уильямс, что усиливает атакующий потенциал «Красной фурии».

## Контекст

Испания подходит к турниру в статусе одного из главных фаворитов: суперкомпьютер Opta оценивает шансы команды на титул примерно в 16 процентов – выше, чем у любого другого участника. В группе H испанцам противостоят Кабо-Верде, Саудовская Аравия и Уругвай.

Возвращение Ямаля – ключевой фактор для амбиций сборной, действующего чемпиона Европы, нацелившейся на второй в истории титул чемпиона мира.

Источники: Al Jazeera, ESPN, World Soccer Talk.""",
"sources":[
 "https://www.aljazeera.com/sports/2026/6/14/lamine-yamal-fit-to-start-on-bench-for-spain-vs-cape-verde-at-world-cup",
 "https://www.espn.com/soccer/story/_/id/49031484/spain-world-cup-2026-lamine-yamal-nico-williams-injury",
 "https://worldsoccertalk.com/amp/world-cup/lamine-yamal-in-perfect-condition-but-unlikely-to-play-full-match-in-spains-world-cup-opener-says-de-la-fuente/",
 "https://www.aljazeera.com/sports/2026/6/14/spain-vs-cape-verde-world-cup-predictions-lamine-yamal-schedule-how-to-watch"]})

A.append({
"key":"sweden","source_type":"news","type":"match_report","category":"Отчёты о матчах",
"slug":"sweden-5-1-tunisia-world-cup-2026",
"title":"Швеция 5:1 Тунис: дубль Айяри и историческая результативность скандинавов на ЧМ-2026",
"excerpt":"Швеция разгромила Тунис 5:1 в матче группы F и впервые с 1938 года забила пять мячей в одной игре чемпионата мира. Дубль оформил Ясин Айяри, отличились также Исак, Йёкереш и Сванберг.",
"body":"""Сборная Швеции мощно вошла в чемпионат мира 2026 года, разгромив Тунис со счётом 5:1 в матче группы F. Встреча прошла 14 июня на «Эстадио ББВА» в Гуадалупе (штат Нуэво-Леон, Мексика) и стала для скандинавов исторической.

## Ход матча

Швеция открыла счёт уже на 7-й минуте: отличился полузащитник Ясин Айяри. На 30-й минуте преимущество удвоил Александер Исак, хладнокровно реализовав свой момент. Тунис ответил голом Омара Рекика на 43-й минуте и ушёл на перерыв с надеждой, но во втором тайме скандинавы добили соперника.

На 59-й минуте Виктор Йёкереш сделал счёт 3:1, на 84-й Маттиас Сванберг забил четвёртый мяч, а в компенсированное время (90+6') Айяри оформил дубль и установил окончательные 5:1.

## Статистика матча

| Показатель | Швеция | Тунис |
| --- | --- | --- |
| Голы | 5 | 1 |
| Авторы голов | Айяри (7', 90+6'), Исак (30'), Йёкереш (59'), Сванберг (84') | Рекик (43') |

## Исторический результат

По данным Wikipedia и обзоров матчевого дня, Швеция впервые с чемпионата мира 1938 года забила пять голов в одной игре мирового первенства – это рекордная для современной эпохи результативность скандинавов на турнире такого уровня. Победа вывела команду на первое место в группе F.

Связка Исак – Йёкереш в атаке выглядела грозно, а молодой Айяри стал главным героем встречи с дублем. Для Туниса же поражение с разницей в четыре мяча стало болезненным стартом.

В параллельном матче группы F Нидерланды и Япония разошлись миром – 2:2, поэтому Швеция единолично возглавила квартет после первого тура.

Источники: Wikipedia, GMA News.""",
"sources":[
 "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_F",
 "https://www.gmanetwork.com/news/sports/football/991493/2026-fifa-world-cup-updates-and-results-june-15-2026/story/"]})

A.append({
"key":"belgium","source_type":"news","type":"preview","category":"ЧМ-2026",
"slug":"belgium-egypt-world-cup-2026-preview",
"title":"Бельгия – Египет: превью матча ЧМ-2026, дуэль де Брёйне и Салаха в группе G",
"excerpt":"15 июня Бельгия и Египет проведут стартовый матч группы G чемпионата мира 2026 в Сиэтле. «Красные дьяволы» – фавориты, но Мохамед Салах способен наказать соперника за любую ошибку.",
"body":"""Чемпионат мира 2026 года продолжается, и 15 июня на стадионе «Люмен Филд» в Сиэтле сыграют Бельгия и Египет. Этот матч группы G открывает турнирный путь обеих команд и обещает интригующую дуэль звёзд: Кевин де Брёйне против Мохамеда Салаха.

## Что на кону

Группа G помимо Бельгии и Египта включает Иран и Новую Зеландию. Для «красных дьяволов» уверенный старт принципиален: команда по-прежнему считается одним из крепких европейских коллективов и рассчитывает на выход в плей-офф с первого места. Египет же возвращается на чемпионат мира с понятным планом – действовать компактно, плотно обороняться и использовать индивидуальное мастерство Салаха на контратаках.

## Форма и ключевые игроки

По информации Squawka и Sports Mole, Бельгия подходит к матчу с устоявшимся составом: оркестром в центре поля дирижирует Кевин де Брёйне, а на фланге опасен Жереми Доку. Египет делает ставку на капитана Мохамеда Салаха, который восстановился от весеннего повреждения задней поверхности бедра и выйдет с первых минут.

| Команда | Лидер атаки | Тренерская установка |
| --- | --- | --- |
| Бельгия | Кевин де Брёйне | контроль мяча, доминирование |
| Египет | Мохамед Салах | компактная оборона, быстрые выпады |

## Прогноз

Букмекеры и аналитические модели отдают предпочтение Бельгии: по данным рыночных котировок, шансы «красных дьяволов» на победу оцениваются примерно в 60 процентов против 17 у Египта. Наиболее вероятный счёт – минимальная или уверенная победа фаворита, однако недооценивать Салаха нельзя: один его момент способен изменить ход встречи.

В параллельном матче группы G встретятся Иран и Новая Зеландия, что делает стартовый тур особенно важным в борьбе за выход из квартета.

Источники: Squawka, Sports Mole, Wikipedia.""",
"sources":[
 "https://www.squawka.com/us/news/world-cup/match-preview-belgium-vs-egypt-06-15-26-world-cup-2026/",
 "https://www.sportsmole.co.uk/football/belgium/world-cup-2026/team-news/belgium-vs-egypt-injury-suspension-list-predicted-xis_599144.html",
 "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_G"]})

A.append({
"key":"nether","source_type":"news","type":"match_report","category":"Отчёты о матчах",
"slug":"netherlands-2-2-japan-world-cup-2026",
"title":"Нидерланды 2:2 Япония: Камада спасает «Самураев» на 88-й минуте в группе F ЧМ-2026",
"excerpt":"Нидерланды и Япония разошлись миром в результативном матче группы F чемпионата мира 2026 – 2:2. Поздний гол Дайти Камады принёс «Самураям» важное очко.",
"body":"""Один из самых зрелищных матчей стартового тура чемпионата мира 2026 года выдали Нидерланды и Япония: команды сыграли вничью 2:2 в группе F. Встреча прошла 14 июня на «Эй-Ти-энд-Ти Стэдиум» в Арлингтоне (Техас) и держала зрителей в напряжении до финального свистка.

## Ход матча

Первый тайм завершился без голов, а вся развязка пришлась на вторую половину. На 50-й минуте капитан «оранжевых» Вирджил ван Дейк вывел Нидерланды вперёд. Япония быстро ответила: на 57-й минуте отличился Кейто Накамура, восстановив равновесие.

На 64-й минуте Крисенсио Сюммервилл снова вывел нидерландцев вперёд – 2:1, и казалось, что европейцы доведут дело до победы. Однако «Самураи» проявили характер: на 88-й минуте Дайти Камада принёс своей команде заслуженную ничью – 2:2.

## Статистика матча

| Показатель | Нидерланды | Япония |
| --- | --- | --- |
| Голы | 2 | 2 |
| Авторы голов | ван Дейк (50'), Сюммервилл (64') | Накамура (57'), Камада (88') |

## Контекст

Нидерланды подошли к турниру с кадровыми потерями: как сообщает ESPN, из-за травм заявку команды не пополнили защитник Маттейс де Лигт (пах) и ряд других игроков, что сказалось на надёжности обороны. Япония же в очередной раз подтвердила репутацию неудобного соперника для грандов, отыгравшись на последних минутах.

После первого тура оба коллектива набрали по одному очку и расположились вслед за Швецией, которая в параллельном матче разгромила Тунис 5:1. Борьба за выход из группы F обещает быть плотной.

Источники: Wikipedia, GMA News, ESPN.""",
"sources":[
 "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_F",
 "https://www.gmanetwork.com/news/sports/football/991493/2026-fifa-world-cup-updates-and-results-june-15-2026/story/",
 "https://www.espn.com/soccer/story/_/id/48572979/2026-fifa-world-cup-injuries-tracker-which-stars-miss-latest-info"]})

A.append({
"key":"uzbek","source_type":"trend","type":"preview","category":"Сборные",
"slug":"uzbekistan-world-cup-2026-debut-colombia",
"title":"Узбекистан дебютирует на ЧМ-2026: «Белые волки» стартуют против Колумбии 18 июня",
"excerpt":"Сборная Узбекистана впервые в истории сыграет на чемпионате мира и станет первой центральноазиатской командой на мундиале. Стартовый матч группы K против Колумбии пройдёт 18 июня в Мехико.",
"body":"""Для болельщиков Центральной Азии и всего постсоветского пространства чемпионат мира 2026 года войдёт в историю: сборная Узбекистана впервые пробилась на мундиаль и станет первой центральноазиатской командой, сыгравшей на главном футбольном турнире планеты. Дебют «Белых волков» – одна из самых обсуждаемых тем в регионе.

## Группа K и календарь

По информации Sky Sports и Olympics.com, Узбекистан попал в группу K вместе с Колумбией, Португалией и ДР Конго – квартет получился крайне непростым. Расписание матчей сборной выглядит так:

| Дата | Соперник | Город |
| --- | --- | --- |
| 18 июня | Колумбия | Мехико (Мексика) |
| 23 июня | Португалия | Хьюстон (США) |
| 28 июня | ДР Конго | Атланта (США) |

## Дебют против Колумбии

Стартовый матч 18 июня в Мехико против Колумбии Хамеса Родригеса станет историческим моментом для узбекского футбола. Колумбийцы – опытная и техничная команда, однако «Белые волки» прошли уверенный отборочный цикл в азиатской зоне и едут на турнир без комплекса неполноценности.

Особое значение приобретает заключительный тур против ДР Конго 28 июня в Атланте: именно эта игра может стать решающей в борьбе за выход в плей-офф, ведь Португалия с Криштиану Роналду считается фаворитом квартета.

## Почему это важно для региона

Выход Узбекистана – повод для гордости для всей Центральной Азии. Впервые на чемпионате мира будет представлена команда из региона, и интерес к её матчам в Казахстане, Кыргызстане, Таджикистане и других странах СНГ будет огромным. Трансляции мундиаля доступны зрителям региона, и дебют «Белых волков» обещает собрать рекордную аудиторию.

Источники: Sky Sports, Olympics.com, Yahoo Sports.""",
"sources":[
 "https://www.skysports.com/football/news/12040/13543106/world-cup-2026-group-k-guide-fixtures-schedule-standings-and-odds-for-portugal-dr-congo-uzbekistan-and-colombia",
 "https://www.olympics.com/en/news/fifa-world-cup-2026-uzbekistan-all-players-full-squad-list-key-stats-schedule",
 "https://sports.yahoo.com/articles/uzbekistan-2026-world-cup-squad-160000886.html"]})

A.append({
"key":"ranking","source_type":"trend","type":"ranking","category":"Тренды",
"slug":"top-7-blowouts-upsets-world-cup-2026-start",
"title":"Топ-7 разгромов и сенсаций старта ЧМ-2026: от семи мячей Германии до спасения Катара на 94-й минуте",
"excerpt":"Первые туры чемпионата мира 2026 подарили крупные разгромы и громкие сенсации. Собрали семь самых ярких результатов старта турнира – от рекорда Германии до драматичных концовок.",
"body":"""Чемпионат мира 2026 года стартовал ярко: уже в первых турах болельщики увидели крупные разгромы, исторические рекорды и драматичные концовки. Мы собрали семь самых запоминающихся результатов начала турнира. Критерий отбора – масштаб результата и его значение для расклада в группах.

## 1. Германия 7:1 Кюрасао

Самый крупный счёт старта. Германия разнесла дебютанта из Карибского бассейна, оформила семь мячей (дубль Кая Хаверца) и, по данным The Analyst, стала самой результативной сборной в истории чемпионатов мира, обойдя Бразилию по общему числу голов.

## 2. Швеция 5:1 Тунис

Скандинавы впервые с 1938 года забили пять мячей в одном матче мирового первенства. Дубль оформил Ясин Айяри, отличились также Александер Исак, Виктор Йёкереш и Маттиас Сванберг.

## 3. США 4:1 Парагвай

Хозяева турнира начали с повторения своего лучшего результата на чемпионатах мира. Как сообщает Sky Sports, дубль оформил Фоларин Балогун, забили также Джио Рейна, а ещё один мяч соперник отправил в свои ворота. Команда Маурисио Почеттино возглавила группу D.

## 4. Кот-д'Ивуар 1:0 Эквадор

Образец валидольной концовки: единственный гол Кот-д'Ивуар забил на 90-й минуте и вырвал победу у считавшегося фаворитом Эквадора. Африканцы догнали Германию в группе E.

## 5. Катар 1:1 Швейцария

Дебютная драма: Катар сравнял счёт на 94-й минуте и завоевал первое очко в истории своих выступлений на чемпионатах мира, отобрав важный балл у Швейцарии.

## 6. Нидерланды 2:2 Япония

«Самураи» в очередной раз доказали, что неудобны для грандов: уступая по ходу матча, Япония благодаря голу Дайти Камады на 88-й минуте вырвала ничью у Нидерландов.

## 7. Бразилия 1:1 Марокко

Пятикратные чемпионы мира неожиданно не сумели обыграть Марокко и поделили очки – результат, который подчеркнул высокую конкуренцию уже на групповом этапе расширенного до 48 команд турнира.

Старт чемпионата получился богатым на события, и впереди болельщиков ждёт ещё больше интриги. Источники: GMA News, Wikipedia, Sky Sports.""",
"sources":[
 "https://www.gmanetwork.com/news/sports/football/991493/2026-fifa-world-cup-updates-and-results-june-15-2026/story/",
 "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_E",
 "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_F",
 "https://www.skysports.com/football/news/17251/13552628/world-cup-2026-usa-4-1-paraguay-folarin-balogun-at-double-as-mauricio-pochettinos-hosts-deliver-statement-victory"]})

A.append({
"key":"portugal","source_type":"trend","type":"preview","category":"ЧМ-2026",
"slug":"portugal-dr-congo-ronaldo-world-cup-2026-preview",
"title":"Португалия – ДР Конго: Роналду стартует на шестом чемпионате мира в карьере",
"excerpt":"17 июня Португалия проведёт стартовый матч группы K чемпионата мира 2026 против ДР Конго в Хьюстоне. Для 41-летнего Криштиану Роналду это уже шестой мундиаль – вероятно, последний в карьере.",
"body":"""Одной из главных тем чемпионата мира 2026 года в Казахстане и СНГ остаётся Криштиану Роналду. 17 июня сборная Португалии проведёт стартовый матч группы K против ДР Конго на «Эн-Эр-Джи Стэдиум» в Хьюстоне, и для капитана «красно-зелёных» это будет уже шестой чемпионат мира в карьере – рекордный показатель.

## Последний шанс легенды

В свои 41 год Роналду подходит, вероятно, к последнему мундиалю в карьере. Главный трофей в сборной – единственное, чего не хватает в его коллекции, и Португалия рассчитывает построить турнирный путь так, чтобы дать капитану шанс. По информации Sports Mole и UEFA, команду тренирует Роберто Мартинес, а в средней линии по-прежнему ключевую роль играет Бруну Фернандеш.

## Группа K

Соперники Португалии в группе – ДР Конго, Узбекистан и Колумбия. Расписание выглядит так:

| Дата | Соперник | Город |
| --- | --- | --- |
| 17 июня | ДР Конго | Хьюстон |
| 23 июня | Узбекистан | Хьюстон |
| 27 июня | Колумбия | Майами |

Стартовый матч против ДР Конго принципиально важен: африканская сборная физически мощна и способна доставить проблемы, поэтому португальцам нужен уверенный старт, чтобы снять давление перед встречами с дебютантом Узбекистаном и опасной Колумбией.

## Почему за этим следят в СНГ

Роналду – один из самых популярных футболистов в Казахстане и странах СНГ, а его дуэль с дебютантом турнира Узбекистаном 23 июня дополнительно подогревает интерес региональных болельщиков к группе K. Старт португальской команды против ДР Конго станет первым шагом в этой истории.

Источники: Sky Sports, Sports Mole, Outlook India.""",
"sources":[
 "https://www.skysports.com/football/news/12040/13543106/world-cup-2026-group-k-guide-fixtures-schedule-standings-and-odds-for-portugal-dr-congo-uzbekistan-and-colombia",
 "https://www.sportsmole.co.uk/football/portugal/world-cup/feature/portugal-2026-world-cup-preview-squad-fixtures-and-prediction_599092.html",
 "https://www.outlookindia.com/sports/football/portugal-vs-dr-congo-fifa-world-cup-2026-group-k-cristiano-ronaldo-bruno-fernandes-training-in-pics"]})

# ── Attach covers ───────────────────────────────────────────────────────────
for art in A:
    k = art["key"]
    if COVER_B64.get(k):
        art["image_base64"] = COVER_B64[k]
        art["image_url"] = None
    else:
        art["image_base64"] = None
        art["image_url"] = COVER_URL[k]  # fallback: public Commons URL

# ── Validate em-dash absence ────────────────────────────────────────────────
for art in A:
    for f in ("title","excerpt","body"):
        assert "—" not in art[f], f"EM DASH found in {art['slug']} {f}"
print("Em-dash check passed.")

def payload_obj(art):
    return {k: art[k] for k in ("title","slug","body","excerpt","category","type",
            "image_url","image_base64","sources","source_type")}

def publish(items):
    body = json.dumps({"articles":[payload_obj(a) for a in items]}, ensure_ascii=False).encode()
    r = requests.post(ENDPOINT, data=body,
        headers={"Content-Type":"application/json","x-agent-secret":SECRET}, timeout=180)
    print("HTTP", r.status_code)
    return r.json()

print("\nPublishing 8 articles…")
resp = publish(A)
results = {x.get("slug"):x for x in resp.get("results",[])}
for a in A:
    # endpoint may append -N; match by base slug prefix
    r = results.get(a["slug"]) or next((v for k,v in results.items() if k.startswith(a["slug"])), None)
    st = r.get("status") if r else "MISSING"
    print(f"  {'OK ' if st=='inserted' else 'XX '} {a['slug']}  [{st}]" + (f"  ERR={r.get('error')}" if r and r.get('error') else ""))

# retry errors
errs = [a for a in A if (lambda r: not r or r.get("status")!="inserted")(results.get(a["slug"]) or next((v for k,v in results.items() if k.startswith(a["slug"])),None))]
if errs:
    print(f"Retrying {len(errs)} failed…")
    time.sleep(3)
    resp2 = publish(errs)
    for x in resp2.get("results",[]):
        results[x.get("slug")] = x
        print("  retry", x.get("slug"), x.get("status"), x.get("error"))

# ── Logs + archive ──────────────────────────────────────────────────────────
ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
hist = os.path.join(ROOT,"logs","articles-history.jsonl")
db_slugs=[]
with open(hist,"a",encoding="utf-8") as f:
    for a in A:
        r = results.get(a["slug"]) or next((v for k,v in results.items() if k.startswith(a["slug"])),None)
        status = r.get("status") if r else "unknown"
        db_slug = r.get("slug") if r else None
        if status=="inserted": db_slugs.append(db_slug)
        entry={"timestamp":ts,"run_id":RUN_ID,"publish_status":status,"db_id":(r or {}).get("id"),
               "db_slug":db_slug,"source_type":a["source_type"],"type":a["type"],
               "title":a["title"],"slug":a["slug"],
               "topic":a["excerpt"][:160],"teams":[],"players":[],
               "image_via":"base64" if a.get("image_base64") else "url",
               "sources":a["sources"]}
        f.write(json.dumps(entry,ensure_ascii=False)+"\n")

with open(os.path.join(ROOT,"logs","last-run.json"),"w",encoding="utf-8") as f:
    json.dump({"run_id":RUN_ID,"generated_at":ts,"count":len(A),
               "news":sum(1 for a in A if a["source_type"]=="news"),
               "trend":sum(1 for a in A if a["source_type"]=="trend"),
               "db_slugs":db_slugs}, f, ensure_ascii=False, indent=2)

# local archive (markdown only, no base64)
for a in A:
    src = "news" if a["source_type"]=="news" else "trend"
    d = os.path.join(ROOT,"articles",f"{src}-{a['slug']}")
    os.makedirs(d,exist_ok=True)
    with open(os.path.join(d,f"{src}-{a['slug']}.md"),"w",encoding="utf-8") as f:
        f.write(f"# {a['title']}\n\n*{a['excerpt']}*\n\n{a['body']}\n")

# manifest for audit (no base64)
manifest={"generated_at":ts,"run_id":RUN_ID,"articles":[
    {**{k:a[k] for k in ("title","slug","body","excerpt","category","type","image_url","sources","source_type")},
     "image_base64": ("<base64 omitted>" if a.get("image_base64") else None)} for a in A]}
with open("/tmp/manifest_20260615.json","w",encoding="utf-8") as f:
    json.dump(manifest,f,ensure_ascii=False,indent=2)

print("\nInserted:",len(db_slugs),"/",len(A))
print("DB slugs:",db_slugs)
