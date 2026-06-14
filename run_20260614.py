# -*- coding: utf-8 -*-
"""WorldCupNewsAgent run for 2026-06-14: build 8 articles, attach optimized
16:9 base64 cover images from Wikimedia Commons, publish to Sport Arena Hub,
then append logs."""
import os, sys, io, json, time, base64, datetime, uuid, urllib.parse
import requests
from PIL import Image, ImageFilter

ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
SECRET = os.environ.get("AGENT_PUBLISH_SECRET")
if not SECRET:
    print("FATAL: AGENT_PUBLISH_SECRET not set"); sys.exit(1)

RUN_ID = "run-20260614-" + uuid.uuid4().hex[:8]
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
UA = {"User-Agent": "WorldCupNewsAgent/1.0 (almaznis1@gmail.com) editorial-image-fetch"}

# --------------------------------------------------------------------------
# ARTICLES
# --------------------------------------------------------------------------
A1_BODY = """США уверенно открыли домашний чемпионат мира: на «SoFi Stadium» в Лос-Анджелесе хозяева разгромили Парагвай со счётом 4:1 в первом туре группы D ЧМ-2026. Дубль оформил Фоларин Балогун, а тон всей игре задал Кристиан Пулишич.

Перед 70 492 зрителями подопечные Маурисио Почеттино с первых минут захватили инициативу. Уже на 7-й минуте после прострела Пулишича защитник Парагвая Дамиан Бобадилья срезал мяч в собственные ворота. К перерыву хозяева вели 2:0 благодаря Балогуну, а во втором тайме довели дело до разгрома.

## Ход матча

| Минута | Команда | Событие |
|---|---|---|
| 7' | США | Автогол Бобадильи (1:0) |
| 31' | США | Гол Балогуна (2:0) |
| 45+5' | США | Балогун оформляет дубль (3:0) |
| 73' | Парагвай | Гол Маурисио Магальяэса Прадо (3:1) |
| 90+8' | США | Гол Джованни Рейны (4:1) |

Парагвай сумел отыграть один мяч усилиями Маурисио Магальяэса Прадо на 73-й минуте, однако на исход встречи это не повлияло: на исходе компенсированного времени точку поставил вышедший на замену Джованни Рейна.

## Балогун – герой вечера

Рождённый в Бруклине Фоларин Балогун, прошедший академию «Арсенала» и аренды в «Мидлсбро» и «Реймсе», провёл образцовый матч в атаке. По данным Sky Sports, на счету форварда теперь 11 голов в 28 матчах за сборную США. Кристиан Пулишич отдал передачи и создавал моменты, однако был заменён в перерыве из-за дискомфорта в икре – тренерский штаб не стал рисковать ведущим игроком.

## Что сказал Почеттино

Главный тренер сборной США остался доволен реакцией команды на давление статуса хозяев.

> «То, как они справились с давлением... Первые 45 минут были потрясающими», – сказал Маурисио Почеттино, чьи слова приводит Sky Sports. Специалист подчеркнул, что это лишь старт турнира.

## Турнирная ситуация

Победа вывела США на первое место в группе D с тремя очками – столько же набрала Австралия, обыгравшая Турцию. Парагвай и Турция пока без очков.

Источники: Sky Sports, NBC News, FIFA.com."""

A2_BODY = """Сборная Бельгии начнёт чемпионат мира 2026 года матчем против Египта: команды встретятся 15 июня на «Lumen Field» в Сиэтле в первом туре группы G. Это противостояние атакующей мощи «красных дьяволов» во главе с Кевином Де Брёйне и египетской команды, построенной вокруг Мохамеда Салаха.

Бельгия подходит к турниру в роли фаворита группы. Накануне старта команда разгромила Тунис со счётом 5:0 в товарищеском матче, и теперь рассчитывает уверенно начать и официальный турнир.

## Группа G ЧМ-2026

| Сборная | Статус |
|---|---|
| Бельгия | Фаворит группы |
| Египет | Лидер – Мохамед Салах |
| Иран | Опытный участник ЧМ |
| Новая Зеландия | Аутсайдер |

## Ключевые игроки

В составе Бельгии – Кевин Де Брёйне, быстрый вингер Жереми Доку и вернувшийся в ворота Тибо Куртуа, обладающий огромным опытом крупных турниров. Египет, как отмечает Squawka, делает ставку на компактную оборону и реализацию моментов через Салаха.

## Котировки букмекеров

| Исход | Котировка (bet365) |
|---|---|
| Победа Бельгии | -150 |
| Ничья | +280 |
| Победа Египта | +400 |

По данным прогнозного рынка Kalshi, вероятность победы Бельгии оценивается в 61%, ничьей – в 24%, успеха Египта – в 17%.

## Чего ждать

План Египта понятен: сыграть плотно, измотать более сильного соперника и наказать его за любую ошибку через Салаха. У Бельгии класснее исполнители почти на каждой позиции, поэтому в стартовом матче против обороняющегося соперника логичнее ждать контролируемой победы, чем результативной перестрелки. Победа в первом туре позволит победителю держать судьбу группы в своих руках.

Источники: Squawka, FIFA.com, Wikipedia (Group G)."""

A3_BODY = """Бразилия без травмированного Неймара лишь чудом не проиграла свой стартовый матч на чемпионате мира 2026 года: на «MetLife Stadium» в Нью-Джерси «селесао» сыграли вничью 1:1 с Марокко. От поражения команду спас Винисиус Жуниор.

Марокко открыло счёт после быстрой контратаки – отличился Исмаэль Саиби. Бразилия большую часть встречи владела инициативой, однако до перелома смог довести дело именно Винисиус, забивший эффектный мяч-ответ.

## Ход матча

| Команда | Автор гола |
|---|---|
| Марокко | Исмаэль Саиби |
| Бразилия | Винисиус Жуниор |

Несмотря на обилие моментов у обеих команд, больше забитых мячей зрители не увидели. Марокко действовало дисциплинированно в обороне и было опасно на контратаках, а бразильцам не хватило точности в завершении.

## Винисиус выходит из тени Неймара

Перед турниром Бразилия лишилась Неймара: МРТ подтвердило у форварда разрыв мышцы голени, и капитан остался вне заявки. На этом фоне особое значение приобрела игра Винисиуса Жуниора. Как отмечает ESPN, вингер «вышел из тени Неймара» и стал главной фигурой атаки команды Карло Анчелотти, спасая «селесао» от стартового поражения.

## Турнирная ситуация

В группе C, помимо Бразилии и Марокко, играют Шотландия и Гаити. В параллельном матче шотландцы обыграли Гаити 1:0, поэтому после первого тура расклад в квартете остаётся плотным, а Бразилии предстоит исправлять положение в следующих играх.

Источники: ESPN, Yahoo Sports, Wikipedia (Group C)."""

A4_BODY = """ФИФА признала технический сбой, повлиявший на спорный эпизод в матче группы B чемпионата мира 2026 года между Катаром и Швейцарией. По информации ESPN, во время проверки VAR, после которой швейцарцам назначили пенальти, полуавтоматическая система определения офсайда не работала.

Встреча на «Levi's Stadium» в Санта-Кларе завершилась вничью 1:1 и принесла Катару первое очко в истории выступлений на чемпионатах мира. Однако главной темой стал именно технологический сбой.

## Что произошло

На 17-й минуте Брель Эмболо реализовал пенальти, назначенный после проверки VAR: арбитры решили, что в момент фола вратаря Махмуда Абунады на Ремо Фройлере никто из игроков Швейцарии не находился в офсайде. Эпизод выглядел крайне спорным.

> По данным ESPN, ФИФА объяснила ситуацию «техническим сбоем»: полуавтоматическая система офсайда была недоступна именно для этого решения, а зрителям так и не показали итоговую картинку с технологии.

Спортивный эксперт Гари Невилл, как сообщают Sports Mole и 101 Great Goals, раскритиковал организацию, назвав происходящее «нелепым» и поставив под сомнение прозрачность и надёжность технологий ФИФА.

## Исторический момент для Катара

На 94-й минуте Буалем Хухи головой сравнял счёт и принёс своей сборной первое в истории очко на чемпионатах мира. Для Катара, проигравшего все матчи на домашнем турнире 2022 года, этот результат стал знаковым, пусть и оказался в тени судейско-технологического скандала.

Источники: ESPN, Sports Mole, 101 Great Goals."""

A5_BODY = """Главная сенсация стартовых дней чемпионата мира 2026 года произошла в группе D: сборная Австралии переиграла Турцию со счётом 2:0. Голы Нестори Иранкунды и Коннора Меткалфа принесли «соккеруз» уверенную победу над более титулованным соперником.

Австралийцы открыли счёт ещё в первом тайме и грамотно довели матч до победы, выстояв под давлением турецкой команды во втором тайме.

## Ход матча

| Минута | Автор гола | Счёт |
|---|---|---|
| 27' | Нестори Иранкунда | 1:0 |
| 75' | Коннор Меткалф | 2:0 |

На 27-й минуте Иранкунда воспользовался выпадом в контратаке: первоклассная обработка мяча и точный удар вывели Австралию вперёд. Во втором тайме Коннор Меткалф пробился к штрафной и нанёс мощный удар с отскоком от газона из-за пределов штрафной, окончательно решив исход встречи.

## Сенсация в группе D

После уверенной игры в обороне Австралия набрала три очка и сравнялась по этому показателю с США, также победившими в стартовом туре. Турция и Парагвай пока остались без набранных очков. Для «соккеруз» это идеальный старт турнира, ведь Турция считалась фаворитом пары.

Источники: Yahoo Sports, ESPN, SBS News."""

A6_BODY = """Сборная Узбекистана впервые в своей истории сыграет на чемпионате мира: дебют состоится 17 июня на легендарном «Эстадио Ацтека» в Мехико в матче против Колумбии. Для всей Центральной Азии это историческое событие, за которым будут пристально следить болельщики в Казахстане и других странах региона.

«Белые волки» пробились на мундиаль впервые и попали в группу K, где их соперниками станут Португалия, Колумбия и ДР Конго.

## Календарь Узбекистана на групповом этапе

| Дата | Соперник | Стадион |
|---|---|---|
| 17 июня | Колумбия | «Эстадио Ацтека», Мехико |
| 23 июня | Португалия | «NRG Stadium», Хьюстон |
| 27 июня | ДР Конго | «Mercedes-Benz Stadium», Атланта |

## Чего ждать от дебютанта

Жеребьёвка свела узбекистанцев с одним из фаворитов турнира – Португалией, а также с крепкой Колумбией и физически мощной ДР Конго. Стартовый матч против колумбийцев на «Ацтеке» сразу проверит дебютанта на прочность. Ведущим игроком сборной остаётся форвард Эльдор Шомуродов, выступающий в итальянской Серии A.

## Почему это важно для региона

Выход Узбекистана на чемпионат мира – прорыв не только для самой команды, но и для футбола всей Центральной Азии. Успех «белых волков» вдохновляет соседей по региону, включая Казахстан, и доказывает, что сборные постсоветского пространства способны пробиваться на главный турнир планеты.

Источники: Squawka, FOX Sports, FIFA.com."""

A7_BODY = """Первые дни чемпионата мира 2026 года уже подарили болельщикам яркие голы, исторические достижения и громкие сенсации. Мы отобрали семёрку героев и главных сюжетов стартового тура – от снайперов хозяев до дебютных очков аутсайдеров. Критерий прост: вклад в результат и значимость момента для своей сборной.

## 1. Фоларин Балогун (США)

Форвард хозяев турнира оформил дубль в разгромном матче против Парагвая (4:1) на «SoFi Stadium». Балогун стал главным action-героем стартового вечера ЧМ-2026 и задал тон всей кампании сборной Маурисио Почеттино.

## 2. Винисиус Жуниор (Бразилия)

Без травмированного Неймара именно Винисиус вытащил «селесао» в матче с Марокко (1:1). Его эффектный гол спас Бразилию от стартового поражения, а сам вингер, по выражению ESPN, окончательно «вышел из тени Неймара».

## 3. Буалем Хухи (Катар)

Защитник Катара забил головой на 94-й минуте в матче со Швейцарией (1:1) и принёс своей сборной первое в истории очко на чемпионатах мира. Для команды, проигравшей все матчи на домашнем ЧМ-2022, это огромный шаг вперёд.

## 4. Сенсационная Австралия

«Соккеруз» переиграли Турцию 2:0 благодаря голам Иранкунды и Меткалфа и устроили одну из главных сенсаций первого тура. Австралия набрала три очка и возглавила группу D вместе с США.

## 5. Шотландия возвращается

Сборная Шотландии обыграла Гаити 1:0 (гол Джона Макгинна на 28-й минуте) в своём первом матче на чемпионате мира впервые с 1998 года. Долгожданное возвращение «тартановой армии» на мундиаль обернулось победой.

## 6. Канада берёт историческое очко

Канада сыграла вничью 1:1 с Боснией и Герцеговиной и впервые в истории набрала очко на чемпионате мира. Вышедший на замену Сайл Ларин забил спасительный мяч и вписал своё имя в историю канадского футбола.

## 7. Кристиан Пулишич (США)

Лидер хозяев не забил, но стал дирижёром разгрома Парагвая: именно с его передач и проходов рождались голы. Пулишича заменили в перерыве из соображений предосторожности после дискомфорта в икре, но его влияние на игру было решающим.

Источники: Sky Sports, ESPN, Yahoo Sports, SBS News."""

A8_BODY = """Действующие чемпионы мира стартуют на ЧМ-2026: 16 июня сборная Аргентины во главе с Лионелем Месси сыграет против Алжира на «Arrowhead Stadium» в Канзас-Сити в первом туре группы J. Для Месси этот турнир станет шестым чемпионатом мира в карьере.

Аргентина подходит к матчу в роли явного фаворита, однако Алжир под руководством Владимира Петковича способен преподнести сюрприз.

## Группа J ЧМ-2026

| Сборная | Тренер / лидер |
|---|---|
| Аргентина | Лидер – Лионель Месси |
| Алжир | Владимир Петкович |
| Австрия | Претендент на плей-офф |
| Иордания | Аутсайдер группы |

## Месси идёт на рекорд

По данным Yahoo Sports, Месси с 26 матчами удерживает рекорд по количеству игр на чемпионатах мира, а в отборочном цикле он стал лучшим бомбардиром с восемью голами. Капитан «альбиселесте» проведёт уже шестой мундиаль.

## Форма команд

Аргентина прибыла в Канзас-Сити в отличной форме: пять побед подряд, 15 забитых мячей и лишь один пропущенный, а в последнем контрольном матче 7 июня была обыграна Гондурас (2:0). Алжир, как отмечает Sports Mole, тоже на ходу: команда разгромила Гватемалу 7:0 и обыграла Нидерланды 1:0 в товарищеском матче в июне 2026 года.

## Прогноз

Аргентина – безоговорочный фаворит и должна побеждать, однако Алжир – неудобный соперник с реальной атакующей угрозой и попытается зацепиться за результат, если чемпионы мира позволят себе расслабиться. Обе команды поведут борьбу с Австрией и Иорданией за две путёвки в плей-офф.

Источники: Goal.com, Sports Mole, Yahoo Sports."""

ARTICLES = [
    {  # 1
        "title": "США 4:1 Парагвай: дубль Балогуна и шоу Пулишича открыли ЧМ-2026 для хозяев",
        "slug": "usa-4-1-paraguay-world-cup-2026-balogun",
        "body": A1_BODY,
        "excerpt": "Сборная США уверенно стартовала на домашнем чемпионате мира, разгромив Парагвай 4:1 на «SoFi Stadium». Дубль оформил Фоларин Балогун, а Кристиан Пулишич стал дирижёром атак Маурисио Почеттино.",
        "category": "Отчёты о матчах",
        "type": "match_report",
        "source_type": "news",
        "sources": [
            "https://www.skysports.com/football/united-states-of-america-vs-paraguay/report/549769",
            "https://www.nbcnews.com/sports/soccer/live-blog/fifa-world-cup-2026-june-12-live-updates-rcna349721",
            "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/usa-paraguay-highlights-match-report",
        ],
        "img_queries": ["Folarin Balogun", "Christian Pulisic 2024", "Christian Pulisic"],
        "topic": "США разгромили Парагвай 4:1 в стартовом матче ЧМ-2026, дубль Балогуна, ассисты Пулишича, тренер Почеттино",
        "teams": ["США", "Парагвай"], "players": ["Фоларин Балогун", "Кристиан Пулишич", "Джованни Рейна"],
    },
    {  # 2
        "title": "Бельгия – Египет: Салах против Де Брёйне в стартовом туре группы G ЧМ-2026 (15 июня)",
        "slug": "belgium-egypt-world-cup-2026-preview-group-g",
        "body": A2_BODY,
        "excerpt": "15 июня на «Lumen Field» в Сиэтле Бельгия Кевина Де Брёйне начнёт ЧМ-2026 матчем против Египта, который делает ставку на Мохамеда Салаха. Превью, котировки и расклад в группе G.",
        "category": "ЧМ-2026",
        "type": "preview",
        "source_type": "news",
        "sources": [
            "https://www.squawka.com/us/news/world-cup/match-preview-belgium-vs-egypt-06-15-26-world-cup-2026/",
            "https://www.fifa.com/en/match-centre/match/17/285023/289273/400021478",
            "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_G",
        ],
        "img_queries": ["Mohamed Salah 2023", "Mohamed Salah", "Kevin De Bruyne 2024"],
        "topic": "Превью стартового матча группы G ЧМ-2026 Бельгия – Египет 15 июня, Де Брёйне против Салаха",
        "teams": ["Бельгия", "Египет"], "players": ["Кевин Де Брёйне", "Мохамед Салах", "Жереми Доку"],
    },
    {  # 3
        "title": "Бразилия 1:1 Марокко: Винисиус спасает «селесао» без Неймара на старте ЧМ-2026",
        "slug": "brazil-1-1-morocco-vinicius-world-cup-2026",
        "body": A3_BODY,
        "excerpt": "Бразилия без травмированного Неймара лишь спаслась в стартовом матче ЧМ-2026 против Марокко (1:1) на «MetLife Stadium». Решающий гол на счету Винисиуса Жуниора.",
        "category": "Отчёты о матчах",
        "type": "match_report",
        "source_type": "news",
        "sources": [
            "https://www.espn.in/football/story/_/id/49047601/world-cup-2026-today-blog-13-06-2026-live-updates-news-fixtures-schedule-results-usmnt-dream-start",
            "https://sports.yahoo.com/soccer/live/2026-world-cup-scores-results-usmnt-throttles-paraguay-canada-earns-draw-with-bosnia-and-herzegovina-145258177.html",
            "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_C",
        ],
        "img_queries": ["Vinicius Junior 2023", "Vinícius Júnior", "Vinicius Junior"],
        "topic": "Бразилия без Неймара сыграла 1:1 с Марокко на старте ЧМ-2026, спасительный гол Винисиуса Жуниора",
        "teams": ["Бразилия", "Марокко"], "players": ["Винисиус Жуниор", "Исмаэль Саиби"],
    },
    {  # 4
        "title": "ФИФА признала технический сбой в матче Катар – Швейцария: VAR остался без автоматического офсайда",
        "slug": "fifa-technical-outage-qatar-switzerland-var-world-cup-2026",
        "body": A4_BODY,
        "excerpt": "ФИФА объяснила спорный пенальти в матче ЧМ-2026 Катар – Швейцария (1:1) техническим сбоем: полуавтоматическая система офсайда не работала. Катар при этом взял первое историческое очко.",
        "category": "ЧМ-2026",
        "type": "transfer",
        "source_type": "news",
        "sources": [
            "https://www.espn.com/soccer/story/_/id/49059323/fifa-blames-technical-outage-world-cup-var-controversy-qatar-switzerland",
            "https://www.sportsmole.co.uk/football/switzerland/world-cup-2026/feature/prove-me-different-offside-controversy-overshadows-historic-qatar-result_599131.html",
            "https://www.101greatgoals.com/football/world-cup-news/world-cup-2026-qatar-switzerland-report-result-goals/",
            "https://www.espn.com/soccer/story/_/id/49051620/qatar-vs-switzerland-live-2026-world-cup-updates-score-commentary",
        ],
        "img_queries": ["Breel Embolo", "Levi's Stadium", "Breel Embolo Switzerland"],
        "topic": "ФИФА признала технический сбой полуавтоматического офсайда в матче ЧМ-2026 Катар – Швейцария 1:1, первое очко Катара",
        "teams": ["Катар", "Швейцария"], "players": ["Брель Эмболо", "Буалем Хухи"],
    },
    {  # 5
        "title": "Австралия 2:0 Турция: Иранкунда и Меткалф добывают сенсацию на старте ЧМ-2026",
        "slug": "australia-2-0-turkiye-world-cup-2026-upset",
        "body": A5_BODY,
        "excerpt": "Сборная Австралии сенсационно обыграла Турцию 2:0 в первом туре группы D ЧМ-2026. Голами отметились Нестори Иранкунда и Коннор Меткалф.",
        "category": "Отчёты о матчах",
        "type": "match_report",
        "source_type": "news",
        "sources": [
            "https://sports.yahoo.com/soccer/live/2026-world-cup-scores-results-usmnt-throttles-paraguay-canada-earns-draw-with-bosnia-and-herzegovina-145258177.html",
            "https://www.espn.in/football/story/_/id/49047601/world-cup-2026-today-blog-13-06-2026-live-updates-news-fixtures-schedule-results-usmnt-dream-start",
            "https://www.sbs.com.au/news/article/fifa-world-cup-2026-results-june-13/vcv3xxpnf",
        ],
        "img_queries": ["Australia national soccer team", "Mathew Ryan footballer", "Socceroos"],
        "topic": "Австралия сенсационно обыграла Турцию 2:0 на старте ЧМ-2026, голы Иранкунды и Меткалфа, группа D",
        "teams": ["Австралия", "Турция"], "players": ["Нестори Иранкунда", "Коннор Меткалф"],
    },
    {  # 6
        "title": "Узбекистан дебютирует на ЧМ-2026: первый в истории матч против Колумбии 17 июня",
        "slug": "uzbekistan-world-cup-2026-debut-colombia-preview",
        "body": A6_BODY,
        "excerpt": "Сборная Узбекистана впервые сыграет на чемпионате мира: дебют состоится 17 июня против Колумбии на «Эстадио Ацтека». Историческое событие для всего футбола Центральной Азии.",
        "category": "Сборные",
        "type": "preview",
        "source_type": "trend",
        "sources": [
            "https://www.squawka.com/en/news/world-cup/uzbekistan-world-cup-2026-fixtures-squad-analysis/",
            "https://www.foxsports.com/stories/soccer/uzbekistan-world-cup-2026-schedule-locations-dates-times",
            "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/teams/uzbekistan/fixtures",
        ],
        "img_queries": ["Eldor Shomurodov", "Uzbekistan national football team", "Eldor Shomurodov Roma"],
        "topic": "Исторический дебют Узбекистана на ЧМ-2026, группа K, первый матч против Колумбии 17 июня, интерес в Центральной Азии",
        "teams": ["Узбекистан", "Колумбия", "Португалия", "ДР Конго"], "players": ["Эльдор Шомуродов"],
    },
    {  # 7
        "title": "Топ-7 героев и сенсаций стартовых дней ЧМ-2026",
        "slug": "top-7-heroes-opening-round-world-cup-2026",
        "body": A7_BODY,
        "excerpt": "Дубль Балогуна, спасение Винисиуса, исторические очки Катара и Канады и сенсация Австралии: собрали семёрку главных героев и сюжетов стартовых дней чемпионата мира 2026 года.",
        "category": "Тренды",
        "type": "ranking",
        "source_type": "trend",
        "sources": [
            "https://www.skysports.com/football/united-states-of-america-vs-paraguay/report/549769",
            "https://www.espn.in/football/story/_/id/49047601/world-cup-2026-today-blog-13-06-2026-live-updates-news-fixtures-schedule-results-usmnt-dream-start",
            "https://sports.yahoo.com/soccer/live/2026-world-cup-scores-results-usmnt-throttles-paraguay-canada-earns-draw-with-bosnia-and-herzegovina-145258177.html",
            "https://www.espn.com/soccer/story/_/id/49059323/fifa-blames-technical-outage-world-cup-var-controversy-qatar-switzerland",
            "https://www.sbs.com.au/news/article/fifa-world-cup-2026-results-june-13/vcv3xxpnf",
        ],
        "img_queries": ["SoFi Stadium", "MetLife Stadium", "SoFi Stadium Inglewood"],
        "topic": "Рейтинг топ-7 героев и сенсаций стартовых дней ЧМ-2026: Балогун, Винисиус, Хухи, Австралия, Шотландия, Канада, Пулишич",
        "teams": ["США", "Бразилия", "Катар", "Австралия", "Шотландия", "Канада"], "players": ["Фоларин Балогун", "Винисиус Жуниор", "Буалем Хухи", "Кристиан Пулишич"],
    },
    {  # 8
        "title": "Аргентина – Алжир: Месси выводит чемпионов мира на старт ЧМ-2026 (16 июня)",
        "slug": "argentina-algeria-world-cup-2026-preview-messi",
        "body": A8_BODY,
        "excerpt": "16 июня действующие чемпионы мира из Аргентины во главе с Лионелем Месси стартуют на ЧМ-2026 матчем против Алжира в Канзас-Сити. Превью, форма команд и расклад в группе J.",
        "category": "ЧМ-2026",
        "type": "preview",
        "source_type": "trend",
        "sources": [
            "https://www.goal.com/en/news/argentina-algeria-world-cup-preview/blt877acb33aa4b3693",
            "https://www.sportsmole.co.uk/football/argentina/world-cup-2026/preview/argentina-vs-algeria-prediction-team-news-lineups_599163.html",
            "https://sports.yahoo.com/articles/argentina-vs-algeria-prediction-world-142000489.html",
        ],
        "img_queries": ["Lionel Messi 2022", "Lionel Messi", "Lionel Messi Argentina"],
        "topic": "Превью стартового матча группы J ЧМ-2026 Аргентина – Алжир 16 июня, шестой чемпионат мира Месси",
        "teams": ["Аргентина", "Алжир"], "players": ["Лионель Месси"],
    },
]

# --------------------------------------------------------------------------
# IMAGE HANDLING
# --------------------------------------------------------------------------
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

def commons_search_files(query, limit=8):
    params = {"action": "query", "format": "json", "list": "search",
              "srnamespace": "6", "srsearch": query, "srlimit": str(limit)}
    r = requests.get(COMMONS_API, params=params, headers=UA, timeout=30)
    r.raise_for_status()
    return [it["title"] for it in r.json().get("query", {}).get("search", [])]

def commons_imageinfo(title, width=1600):
    params = {"action": "query", "format": "json", "titles": title,
              "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": str(width)}
    r = requests.get(COMMONS_API, params=params, headers=UA, timeout=30)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    for _, p in pages.items():
        ii = p.get("imageinfo")
        if ii:
            return ii[0]
    return None

def pick_image_url(queries):
    """Return (thumburl, descurl) for first usable raster image."""
    for q in queries:
        try:
            titles = commons_search_files(q)
        except Exception as e:
            print(f"   search error '{q}': {e}"); continue
        for t in titles:
            low = t.lower()
            if not (low.endswith(".jpg") or low.endswith(".jpeg") or low.endswith(".png")):
                continue
            if any(bad in low for bad in ["logo", "emblem", "icon", "flag", "map", "crest", "badge"]):
                continue
            try:
                ii = commons_imageinfo(t)
            except Exception as e:
                print(f"   imageinfo error {t}: {e}"); continue
            if not ii:
                continue
            w = ii.get("width", 0)
            if w and w < 600:
                continue
            thumb = ii.get("thumburl") or ii.get("url")
            if thumb:
                print(f"   picked: {t}")
                return thumb, ii.get("descriptionurl", "")
            time.sleep(0.5)
        time.sleep(1.0)
    return None, None

def build_169_base64(img_bytes):
    """Fit image into 1600x900 with blurred fill background, JPEG q82."""
    src = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    TW, TH = 1600, 900
    # blurred cover background
    sw, sh = src.size
    scale_bg = max(TW / sw, TH / sh)
    bg = src.resize((max(1, int(sw * scale_bg)), max(1, int(sh * scale_bg))), Image.LANCZOS)
    left = (bg.width - TW) // 2; top = (bg.height - TH) // 2
    bg = bg.crop((left, top, left + TW, top + TH)).filter(ImageFilter.GaussianBlur(28))
    # contained foreground
    scale_fg = min(TW / sw, TH / sh)
    fg = src.resize((max(1, int(sw * scale_fg)), max(1, int(sh * scale_fg))), Image.LANCZOS)
    fx = (TW - fg.width) // 2; fy = (TH - fg.height) // 2
    canvas = bg.copy(); canvas.paste(fg, (fx, fy))
    out = io.BytesIO()
    q = 85
    while True:
        out.seek(0); out.truncate()
        canvas.save(out, format="JPEG", quality=q, optimize=True)  # no exif -> stripped
        if out.tell() <= 300 * 1024 or q <= 60:
            break
        q -= 5
    data = out.getvalue()
    print(f"   image {len(data)//1024} KB at q{q}")
    return base64.b64encode(data).decode("ascii")

def attach_images():
    for i, a in enumerate(ARTICLES, 1):
        print(f"[img {i}/8] {a['slug']}")
        a["image_base64"] = None
        a["image_url"] = None
        thumb, _ = pick_image_url(a["img_queries"])
        if not thumb:
            print("   !! no image found");
            time.sleep(3.5); continue
        try:
            ib = requests.get(thumb, headers=UA, timeout=60)
            ib.raise_for_status()
            a["image_base64"] = build_169_base64(ib.content)
        except Exception as e:
            print(f"   base64 build failed ({e}); falling back to image_url")
            a["image_url"] = thumb
        time.sleep(3.5)  # Wikimedia rate-limit courtesy

# --------------------------------------------------------------------------
# PUBLISH
# --------------------------------------------------------------------------
def payload_obj(a):
    return {
        "title": a["title"], "slug": a["slug"], "body": a["body"],
        "excerpt": a["excerpt"], "category": a["category"], "type": a["type"],
        "image_url": a.get("image_url"), "image_base64": a.get("image_base64"),
        "sources": a["sources"], "source_type": a["source_type"],
    }

def publish(objs):
    headers = {"Content-Type": "application/json", "x-agent-secret": SECRET}
    r = requests.post(ENDPOINT, headers=headers, data=json.dumps({"articles": objs}), timeout=180)
    print("HTTP", r.status_code)
    if r.status_code == 401:
        print("401 unauthorized - stopping"); sys.exit(1)
    try:
        return r.json()
    except Exception:
        print("non-JSON response:", r.text[:500]); return {}

# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
def main():
    attach_images()
    objs = [payload_obj(a) for a in ARTICLES]
    # save manifest (without base64 in chat, but full to disk)
    os.makedirs("logs", exist_ok=True)
    with open("logs/manifest-20260614.json", "w", encoding="utf-8") as f:
        json.dump({"generated_at": NOW, "run_id": RUN_ID,
                   "articles": [{k: (("<base64 %d b>" % len(v)) if k == "image_base64" and v else v)
                                 for k, v in o.items()} for o in objs]},
                  f, ensure_ascii=False, indent=2)

    by_slug = {a["slug"]: a for a in ARTICLES}
    print("\n=== PUBLISH (batch of 8) ===")
    resp = publish(objs)
    results = resp.get("results", [])
    status = {}
    for res in results:
        status[res.get("slug")] = res
        print(f"  {res.get('status')}: {res.get('slug')} {res.get('error') or ''}")

    # retry errors once
    errored = [a["slug"] for a in ARTICLES if status.get(a["slug"], {}).get("status") != "inserted"]
    # match by original slug OR appended suffix is treated as already-present; only retry true errors
    retry_objs = [payload_obj(by_slug[s]) for s in errored if s in by_slug and
                  status.get(s, {}).get("status") == "error"]
    if retry_objs:
        print("\n=== RETRY errored ===", [o["slug"] for o in retry_objs])
        time.sleep(3)
        resp2 = publish(retry_objs)
        for res in resp2.get("results", []):
            status[res.get("slug")] = res
            print(f"  {res.get('status')}: {res.get('slug')} {res.get('error') or ''}")

    # logging
    log_lines = []
    inserted_slugs = []
    for a in ARTICLES:
        res = status.get(a["slug"], {})
        st = res.get("status", "unknown")
        ret_slug = res.get("slug", a["slug"])
        if st == "inserted":
            inserted_slugs.append(ret_slug)
        entry = {
            "timestamp": NOW, "run_id": RUN_ID, "source_type": a["source_type"],
            "type": a["type"], "title": a["title"], "slug": a["slug"],
            "db_slug": ret_slug, "publish_status": st, "db_id": res.get("id"),
            "topic": a["topic"], "teams": a["teams"], "players": a["players"],
            "image_attached": bool(a.get("image_base64") or a.get("image_url")),
            "image_via": ("base64" if a.get("image_base64") else ("url" if a.get("image_url") else "none")),
            "sources": a["sources"],
        }
        log_lines.append(json.dumps(entry, ensure_ascii=False))

    with open("logs/articles-history.jsonl", "a", encoding="utf-8") as f:
        for ln in log_lines:
            f.write(ln + "\n")

    with open("logs/last-run.json", "w", encoding="utf-8") as f:
        json.dump({"run_id": RUN_ID, "generated_at": NOW,
                   "counts": {"total": len(ARTICLES),
                              "news": sum(1 for a in ARTICLES if a["source_type"] == "news"),
                              "trend": sum(1 for a in ARTICLES if a["source_type"] == "trend"),
                              "inserted": len(inserted_slugs)},
                   "slugs": [a["slug"] for a in ARTICLES],
                   "db_slugs": inserted_slugs}, f, ensure_ascii=False, indent=2)

    print("\n=== SUMMARY ===")
    print("inserted:", len(inserted_slugs), "/ 8")
    for a in ARTICLES:
        res = status.get(a["slug"], {})
        print(f"  [{res.get('status','?'):8}] {res.get('slug', a['slug'])} via {('base64' if a.get('image_base64') else ('url' if a.get('image_url') else 'NONE'))}")

if __name__ == "__main__":
    main()
