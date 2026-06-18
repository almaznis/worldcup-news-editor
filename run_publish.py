#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, base64, datetime, uuid, time, urllib.request

RUN_ID = "run-20260618-" + uuid.uuid4().hex[:8]
NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
SECRET = os.environ.get("AGENT_PUBLISH_SECRET")

def cover(slug):
    with open(f"/tmp/cover_{slug}.b64") as f:
        return f.read().strip()

# ---- ranking inline images ----
IMG = {
 "messi":"https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/LIONEL_MESSI_-_BRESH_MIAMI_%28Cropped%29.jpg/960px-LIONEL_MESSI_-_BRESH_MIAMI_%28Cropped%29.jpg",
 "mbappe":"https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Kylian_Mbapp%C3%A9_%28cropped%29.jpg/960px-Kylian_Mbapp%C3%A9_%28cropped%29.jpg",
 "haaland":"https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Erling_Haaland_2023.jpg/960px-Erling_Haaland_2023.jpg",
 "kane":"https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Harry_Kane_%2824685589756%29_%28cropped%29.jpg/960px-Harry_Kane_%2824685589756%29_%28cropped%29.jpg",
 "havertz":"https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/1_kai_havertz_2026_%28cropped%29.jpg/960px-1_kai_havertz_2026_%28cropped%29.jpg",
 "balogun":"https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Folarin_Balogun_USMNT_v_Belgium_Mar_28_2026-69.jpg/960px-Folarin_Balogun_USMNT_v_Belgium_Mar_28_2026-69.jpg",
 "ayari":"https://upload.wikimedia.org/wikipedia/commons/d/d8/Yasin_Ayari_%28Sweden_U21_vs_Moldova_U21%2C_13_October_2023%29.jpg",
}

articles = []

# ============ 1. Argentina 3-0 Algeria (news / match_report) ============
articles.append({
"title":"Месси оформил первый хет-трик на чемпионатах мира: Аргентина разгромила Алжир 3:0",
"slug":"argentina-3-0-algeria-messi-hat-trick",
"category":"Отчёты о матчах","type":"match_report","source_type":"news",
"excerpt":"Лионель Месси забил три мяча в стартовом матче группы J и догнал Мирослава Клозе в списке лучших бомбардиров в истории чемпионатов мира. Аргентина уверенно начала защиту титула.",
"sources":[
 "https://www.skysports.com/football/news/17364/13552724/world-cup-2026-argentina-3-0-algeria-lionel-messi-scores-stunning-hat-trick-to-draw-level-in-all-time-world-cup-scoring-charts",
 "https://www.aljazeera.com/sports/2026/6/17/messi-fires-argentina-to-win-against-algeria-in-world-cup-defence-opener",
 "https://www.espn.com/soccer/story/_/id/49086753/argentina-algeria-live-world-cup-2026-latest-updates-commentary-score-result"],
"image_base64":cover("argentina-3-0-algeria-messi-hat-trick"),
"body":"""**Аргентина победила Алжир со счётом 3:0** в стартовом матче группы J на чемпионате мира 2026 года, и все три мяча действующих чемпионов записал на свой счёт Лионель Месси. Хет-трик на «Эрроухед-Стэдиум» в Канзас-Сити, где собрались около 70 тысяч зрителей, стал первым в карьере аргентинца на мировых первенствах.

## Месси переписал историю

37-летний капитан открыл счёт на 17-й минуте дальним ударом, удвоил преимущество на 60-й минуте и поставил точку на 76-й минуте точным ударом в дальний угол. Эти голы довели Месси до отметки в 16 мячей на чемпионатах мира – столько же на счету немца Мирослава Клозе, рекордсмена в истории турнира.

Матч против Алжира стал для Месси 200-м в составе сборной Аргентины, а сам он, по информации Sky Sports и ESPN, превратился в первого футболиста, выходившего на поле на шести чемпионатах мира.

## Хроника голов

| Минута | Команда | Автор гола |
| --- | --- | --- |
| 17' | Аргентина | Месси |
| 60' | Аргентина | Месси |
| 76' | Аргентина | Месси |

## Уверенный старт чемпионов

Аргентина, выигравшая титул в 2022 году, полностью контролировала ход встречи и не позволила Алжиру создать серьёзных угроз у своих ворот. Победа выводит подопечных Лионеля Скалони в лидеры группы J уже после первого тура.

> «Месси снова напомнил всем, кто здесь главный», – отмечает Al Jazeera в отчёте о матче.

Следующий матч группового этапа станет проверкой того, способна ли Аргентина удержать набранный темп в защите чемпионского титула.

Источники: Sky Sports, Al Jazeera, ESPN."""
})

# ============ 2. Zwane ban (news / transfer) ============
articles.append({
"title":"ФИФА дисквалифицировала Темба Зване на три матча за удаление в игре с Мексикой",
"slug":"fifa-zwane-three-match-ban-wc2026",
"category":"Новости игроков","type":"transfer","source_type":"news",
"excerpt":"Дисциплинарный комитет ФИФА наказал полузащитника сборной ЮАР тремя матчами дисквалификации после прямой красной карточки в стартовом матче против Мексики.",
"sources":[
 "https://africasoccer.com/world-cup-2026-fifa-hands-themba-zwane-three-match-suspension-following-red-card-incident/",
 "https://www.voiceofemirates.com/en/sport/2026/06/18/official-fifa-suspends-south-african-player-for-3-matches-following-world-cup-red-card/"],
"image_base64":cover("fifa-zwane-three-match-ban-wc2026"),
"body":"""**Полузащитник сборной ЮАР Темба Зване дисквалифицирован на три матча чемпионата мира 2026 года.** По информации ряда африканских и ближневосточных изданий, такое решение принял Дисциплинарный комитет ФИФА после прямой красной карточки, которую игрок получил в стартовом матче группы A против хозяев турнира – сборной Мексики.

## Что произошло

ЮАР проиграла Мексике со счётом 0:2 в первом туре, причём южноафриканцы завершили встречу вдвоём в меньшинстве – по ходу матча поле досрочно покинули сразу два игрока. Удаление Зване обернулось не только автоматическим пропуском следующей игры, но и дополнительными санкциями со стороны ФИФА.

## Почему три матча, а не один

По регламенту чемпионата мира прямая красная карточка влечёт за собой как минимум одноматчевую дисквалификацию. Однако ФИФА оставляет за собой право ужесточить наказание, если сочтёт нарушение грубым. В случае с Зване, как сообщают источники, комитет назначил три матча – это означает, что опытный хавбек, скорее всего, не сыграет до конца группового этапа.

## Удар по сборной ЮАР

Потеря Зване ослабляет атакующий потенциал команды в решающих матчах группы A. Уже 18 июня ЮАР проведёт принципиальную встречу с Чехией, где обеим сборным после стартовых поражений необходима только победа, чтобы сохранить шансы на выход в плей-офф.

> На момент публикации официальный комментарий футбольной ассоциации ЮАР по поводу возможной апелляции отсутствует.

Источники: AfricaSoccer, Voice of Emirates."""
})

# ============ 3. England 4-2 Croatia (news / match_report) ============
articles.append({
"title":"Англия обыграла Хорватию 4:2 на старте ЧМ-2026: дубль Кейна, голы Беллингема и Рэшфорда",
"slug":"england-4-2-croatia-wc2026",
"category":"Отчёты о матчах","type":"match_report","source_type":"news",
"excerpt":"Сборная Англии под руководством Томаса Тухеля начала чемпионат мира с яркой победы над Хорватией. Гарри Кейн оформил дубль, ещё забили Джуд Беллингем и Маркус Рэшфорд.",
"sources":[
 "https://www.skysports.com/football/news/32461/13552729/world-cup-2026-england-4-2-croatia-harry-kane-jude-bellingham-and-marcus-rashford-on-target-as-three-lions-make-winning-start",
 "https://www.espn.com/soccer/story/_/id/49099495/england-croatia-world-cup-2026-recap-score-harry-kane-jude-bellingham-marcus-rashford",
 "https://www.france24.com/en/sport/20260617-world-cup-2026-kane-bellingham-and-rashford-fire-england-past-croatia"],
"image_base64":cover("england-4-2-croatia-wc2026"),
"body":"""**Сборная Англии победила Хорватию со счётом 4:2** в стартовом матче группы L чемпионата мира 2026 года и сразу заявила о своих чемпионских амбициях. Встреча в Арлингтоне получилась результативной и нервной, но команда Томаса Тухеля доказала превосходство во втором тайме.

## Кейн повёл команду за собой

Капитан Гарри Кейн открыл счёт уже на 12-й минуте, реализовав пенальти, а перед перерывом, на 42-й минуте, оформил дубль. После перерыва преимущество «трёх львов» стало неоспоримым: на 47-й минуте отличился Джуд Беллингем, ворвавшийся в штрафную и пробивший в дальний угол.

На 85-й минуте точку поставил вышедший на замену Маркус Рэшфорд, которому ассистировал Букайо Сака. Хорватия отыграла два мяча усилиями Мартина Батурины и Петара Мусы, но этого оказалось недостаточно.

## Хроника матча

| Минута | Команда | Автор гола |
| --- | --- | --- |
| 12' (пен.) | Англия | Кейн |
| 42' | Англия | Кейн |
| 47' | Англия | Беллингем |
| 85' | Англия | Рэшфорд |
| – | Хорватия | Батурина |
| – | Хорватия | Муса |

## Реванш за 2018 год

Для Англии эта встреча имела особый подтекст: предыдущий матч с Хорватией на чемпионатах мира состоялся в полуфинале 2018 года, когда хорваты победили 2:1 в дополнительное время. На этот раз преимущество было на стороне англичан, которые возглавили группу L после первого тура.

> «Электрический второй тайм обеспечил Англии уверенный старт», – пишет Sky Sports.

Источники: Sky Sports, ESPN, France 24."""
})

# ============ 4. Mexico vs South Korea preview (news / preview) ============
articles.append({
"title":"Мексика – Южная Корея: превью матча группы A на ЧМ-2026",
"slug":"mexico-south-korea-preview-wc2026",
"category":"ЧМ-2026","type":"preview","source_type":"news",
"excerpt":"Хозяева турнира Мексика и сборная Южной Кореи во главе с Сон Хын Мином выиграли стартовые матчи и встречаются в очной игре за единоличное лидерство в группе A.",
"sources":[
 "https://www.skysports.com/football/news/12098/13540670/world-cup-2026-group-a-guide-fixtures-schedule-standings-and-odds-for-mexico-south-africa-south-korea-and-czech-republic",
 "https://www.espn.com/soccer/story/_/id/48939282/2026-fifa-world-cup-fixtures-results-match-schedule-group-stage-knockout-rounds-bracket",
 "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_A"],
"image_base64":cover("mexico-south-korea-preview-wc2026"),
"body":"""**Сборные Мексики и Южной Кореи проведут центральный матч второго тура группы A** на чемпионате мира 2026 года. Игра пройдёт 18 июня на стадионе «Акрон» в Сапопане, и для обеих команд это шанс оформить досрочный выход в плей-офф.

## Что на кону

Обе команды одержали победы в стартовом туре: Мексика как хозяин турнира обыграла ЮАР со счётом 2:0, а Южная Корея переиграла Чехию 2:1. Победитель очной встречи фактически гарантирует себе место в следующем раунде и поведёт борьбу за первое место в группе.

## Положение в группе A после первого тура

| Команда | И | О |
| --- | --- | --- |
| Мексика | 1 | 3 |
| Южная Корея | 1 | 3 |
| Чехия | 1 | 0 |
| ЮАР | 1 | 0 |

## Ключевые фигуры

Главная звезда корейцев – капитан Сон Хын Мин, чья скорость и удар поставят перед обороной Мексики серьёзные задачи. Хозяева же сделают ставку на поддержку трибун и быстрые фланговые атаки: «Эль Три» традиционно силён на домашнем чемпионате мира.

| Сборная | Игрок в фокусе |
| --- | --- |
| Мексика | атака хозяев, поддержка трибун |
| Южная Корея | Сон Хын Мин |

## Прогноз

Преимущество своего поля и поддержка зрителей делают Мексику фаворитом, однако опыт и индивидуальное мастерство Сона способны склонить чашу весов в пользу Кореи. Ожидается равная и напряжённая игра, в которой решающим может стать один эпизод. Параллельно в этот же день Чехия и ЮАР проведут матч на выживание в Атланте.

Источники: Sky Sports, ESPN, Wikipedia (Group A)."""
})

# ============ 5. Portugal 1-1 DR Congo (news / match_report) ============
articles.append({
"title":"Роналду без голевого дебюта: Португалия упустила победу над ДР Конго – 1:1",
"slug":"portugal-1-1-dr-congo-ronaldo-wc2026",
"category":"Отчёты о матчах","type":"match_report","source_type":"news",
"excerpt":"Португалия повела в счёте уже на 6-й минуте, но ДР Конго отыгралась перед перерывом и забила первый гол в своей истории на чемпионатах мира. Криштиану Роналду провёл дебютный матч турнира без результативных действий.",
"sources":[
 "https://www.espn.com/soccer/story/_/id/49096146/portugal-dr-congo-live-world-cup-2026-latest-updates-commentary-score-result",
 "https://theanalyst.com/articles/portugal-vs-dr-congo-stats-world-cup-2026-live",
 "https://bolavip.com/en/world-cup/portugal-vs-dr-congo-live-cristiano-ronaldo-makes-2026-world-cup-debut"],
"image_base64":cover("portugal-1-1-dr-congo-ronaldo-wc2026"),
"body":"""**Португалия и ДР Конго сыграли вничью 1:1** в матче группы K чемпионата мира 2026 года в Хьюстоне. «Леопарды» вырвали исторический результат и заработали первое очко в своей истории на мировых первенствах, омрачив дебют Криштиану Роналду на этом турнире.

## Быстрый гол и ответ «Леопардов»

Португалия повела уже на 6-й минуте: Жоау Невеш точно пробил головой после навеса Педру Нету. Однако ДР Конго не дрогнула и в компенсированное к первому тайму время (45+5) сравняла счёт – Йоан Висса замкнул головой подачу Артура Масуаку. Этот мяч стал первым голом сборной ДР Конго в истории чемпионатов мира.

## Хроника голов

| Минута | Команда | Автор гола |
| --- | --- | --- |
| 6' | Португалия | Невеш |
| 45+5' | ДР Конго | Висса |

## Упущенные шансы и сэйвы

Во втором тайме игра шла на встречных курсах. По данным аналитического портала Opta, ДР Конго была близка к сенсационному камбэку: Седрик Бакамбу после сольного прохода попал в штангу. Португалия же владела инициативой и до последних секунд искала победный мяч, но так и не сумела дожать соперника.

## Роналду пока без голов

Для Криштиану Роналду матч стал стартовым на чемпионате мира 2026 года, однако записать на свой счёт результативное действие ему не удалось. Ничья осложняет положение Португалии в группе K, где конкуренция оказалась плотнее, чем ожидалось.

> «Леопарды» заработали историческое очко и расстроили португальцев», – отмечает Opta Analyst.

Источники: ESPN, Opta Analyst, Bolavip."""
})

# ============ 6. Uzbekistan 1-3 Colombia (trend / match_report) ============
articles.append({
"title":"Дебют Узбекистана на ЧМ-2026 омрачён поражением: Колумбия победила 3:1",
"slug":"uzbekistan-1-3-colombia-wc2026",
"category":"Отчёты о матчах","type":"match_report","source_type":"trend",
"excerpt":"Сборная Узбекистана впервые в истории сыграла на чемпионате мира, но уступила Колумбии 1:3 на легендарном «Ацтеке». Аббосбек Файзуллаев забил исторический гол за свою команду.",
"sources":[
 "https://www.espn.com/soccer/match/_/gameId/760436/colombia-uzbekistan",
 "https://www.outlookindia.com/sports/football/uzbekistan-vs-colombia-fifa-world-cup-2026-group-k-uzb-v-col-estadio-aztec-match-report",
 "https://www.fifa.com/en/match-centre/match/17/285023/289273/400021504"],
"image_base64":cover("uzbekistan-1-3-colombia-wc2026"),
"body":"""**Сборная Узбекистана уступила Колумбии со счётом 1:3** в дебютном для себя матче на чемпионатах мира. Историческая игра группы K прошла на знаменитом стадионе «Ацтека» в Мехико и вызвала огромный интерес в Центральной Азии и странах СНГ.

## Исторический дебют

Для Узбекистана выход на мировое первенство стал главным достижением в истории национального футбола. Несмотря на поражение, команда не затерялась на фоне опытного соперника и отметилась голом, который надолго останется в памяти болельщиков.

## Как развивался матч

Колумбия открыла счёт на 40-й минуте: защитник Даниэль Муньос первым успел на добивание. Во втором тайме Узбекистан сумел сравнять – Аббосбек Файзуллаев забил первый в истории сборной гол на чемпионатах мира. Однако радость болельщиков продлилась недолго: на 65-й минуте Луис Диас вернул колумбийцам преимущество, а уже в добавленное время Хаминтон Кампас головой установил окончательный счёт.

## Хроника голов

| Минута | Команда | Автор гола |
| --- | --- | --- |
| 40' | Колумбия | Муньос |
| 2-й тайм | Узбекистан | Файзуллаев |
| 65' | Колумбия | Диас |
| 90+9' | Колумбия | Кампас |

## Что дальше

Поражение осложняет задачу Узбекистана в борьбе за плей-офф, но дебютантам ещё предстоят матчи, в которых они смогут побороться за очки. Гол Файзуллаева на «Ацтеке» уже стал символом исторического прорыва узбекского футбола.

> По данным ESPN и Outlook, Колумбия благодаря яркой игре Луиса Диаса захватила лидерство в группе K.

Источники: ESPN, Outlook India, FIFA."""
})

# ============ 7. Top-7 scorers ranking (trend / ranking) ============
articles.append({
"title":"Топ-7 бомбардиров старта ЧМ-2026: Месси возглавил гонку за «Золотой бутсой»",
"slug":"top-7-bombardirov-start-chm-2026",
"category":"Тренды","type":"ranking","source_type":"trend",
"excerpt":"Первые туры чемпионата мира 2026 года подарили россыпь голов от звёзд мирового футбола. Собрали семь форвардов, которые ярче всех начали турнир и поборются за «Золотую бутсу».",
"sources":[
 "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/adidas-golden-boot-race-top-scorer",
 "https://www.olympics.com/en/news/fifa-world-cup-2026-race-golden-boot-football-top-scorer-full-list",
 "https://www.npr.org/2026/06/17/nx-s1-5861412/2026-world-cup-fifa-goals-golden-boot"],
"image_base64":cover("top-7-bombardirov-start-chm-2026"),
"body":"""Старт чемпионата мира 2026 года получился по-настоящему голевым: уже в первом туре сразу несколько звёзд оформили дубли, а одному удался хет-трик. Гонка за «Золотую бутсу» обещает быть жаркой. Мы собрали семь футболистов, которые ярче всех проявили себя на старте турнира, опираясь на данные ФИФА и трекеры лучших бомбардиров. Рейтинг построен по числу забитых мячей в стартовых матчах.

## 1. Лионель Месси (Аргентина) – 3 гола

![Лионель Месси, капитан сборной Аргентины](%(messi)s)

Капитан действующих чемпионов возглавил список бомбардиров, оформив хет-трик в ворота Алжира (3:0). Эти голы вывели Месси на уровень рекордсмена мировых первенств Мирослава Клозе по числу забитых мячей на чемпионатах мира.

## 2. Килиан Мбаппе (Франция) – 2 гола

![Килиан Мбаппе, нападающий сборной Франции](%(mbappe)s)

Лидер сборной Франции отметился дублем в победном матче против Сенегала (3:1). Мбаппе подтвердил статус одного из главных фаворитов в борьбе за приз лучшему снайперу турнира.

## 3. Эрлинг Холанд (Норвегия) – 2 гола

![Эрлинг Холанд, форвард сборной Норвегии](%(haaland)s)

Норвегия впервые за 28 лет вышла на чемпионат мира, и Холанд сразу напомнил о себе дублем в разгромной игре с Ираком (4:1). Мощный форвард намерен бороться за бомбардирскую корону.

## 4. Гарри Кейн (Англия) – 2 гола

![Гарри Кейн, капитан сборной Англии](%(kane)s)

Капитан сборной Англии оформил дубль в результативном матче против Хорватии (4:2), один из мячей забив с пенальти. Кейн остаётся ключевой фигурой атаки «трёх львов».

## 5. Кай Хаверц (Германия) – 2 гола

![Кай Хаверц, нападающий сборной Германии](%(havertz)s)

Форвард сборной Германии записал на свой счёт два мяча в стартовом матче и помог своей команде уверенно начать турнир.

## 6. Фоларин Балогун (США) – 2 гола

![Фоларин Балогун, нападающий сборной США](%(balogun)s)

Нападающий хозяев турнира из США забил дубль в первом туре, став одним из героев старта для американской команды на домашнем чемпионате мира.

## 7. Ясин Аяри (Швеция) – 2 гола

![Ясин Аяри, полузащитник сборной Швеции](%(ayari)s)

Замкнул нашу семёрку швед Ясин Аяри, неожиданно отметившийся дублем в дебютной игре своей сборной на турнире.

## Итог

Месси задал тон бомбардирской гонке, но преследователи дышат ему в спину. Согласно правилам ФИФА, при равенстве голов учитываются результативные передачи, а затем – меньшее игровое время. Впереди ещё два тура группового этапа, и расклад в борьбе за «Золотую бутсу» наверняка не раз изменится.

Источники: FIFA, Olympics.com, NPR.""" % IMG
})

# ============ 8. Switzerland vs Bosnia preview (trend / preview) ============
articles.append({
"title":"Швейцария – Босния и Герцеговина: превью матча группы B, Джеко против фаворита",
"slug":"shveycariya-bosniya-preview-wc2026",
"category":"Сборные","type":"preview","source_type":"trend",
"excerpt":"Во втором туре группы B сборная Швейцарии встречается с Боснией и Герцеговиной, которую ведёт за собой 40-летний капитан Эдин Джеко. Обе команды стартовали с ничьих.",
"sources":[
 "https://www.skysports.com/football/news/12098/13543085/world-cup-2026-group-b-guide-fixtures-schedule-standings-and-odds-for-canada-bosnia-herzegovina-qatar-and-switzerland",
 "https://theanalyst.com/articles/world-cup-2026-group-b-predictions-preview",
 "https://www.uefa.com/european-qualifiers/news/02a6-20d1594a5469-659bdc40eca9-1000--bosnia-and-herzegovina-at-the-world-cup-2026-squad-fixtur/"],
"image_base64":cover("shveycariya-bosniya-preview-wc2026"),
"body":"""**Сборные Швейцарии и Боснии и Герцеговины проведут матч второго тура группы B** на чемпионате мира 2026 года. Игра состоится 18 июня на «СоФай-Стэдиум» в Лос-Анджелесе, и обеим командам нужна победа, чтобы вырваться вперёд в плотной группе.

## Равный старт

После первого тура все четыре сборные группы B набрали по одному очку – стартовые матчи завершились вничью. Это означает, что очная встреча Швейцарии и Боснии приобретает особое значение: победитель сделает серьёзную заявку на выход в плей-офф, тогда как параллельно Канада и Катар выяснят отношения в Ванкувере.

## Положение в группе B после первого тура

| Команда | И | О |
| --- | --- | --- |
| Швейцария | 1 | 1 |
| Босния и Герцеговина | 1 | 1 |
| Канада | 1 | 1 |
| Катар | 1 | 1 |

## Швейцария – фаворит

Швейцария подходит к матчу в статусе фаворита группы. По оценкам аналитиков, у команды самые высокие шансы на выход из группы благодаря стабильному составу и богатому опыту: это уже шестой подряд чемпионат мира для «нати», а в недавних плей-офф крупных турниров швейцарцы выбивали Францию, Италию и Испанию.

## Ставка Боснии – Джеко

Главная фигура боснийцев – капитан Эдин Джеко, которому в марте исполнилось 40 лет. Бессменный лидер атаки и рекордсмен сборной по числу голов (73 мяча) остаётся главной угрозой для любой обороны. Для Боснии и Герцеговины это лишь второй крупный турнир в истории, поэтому каждое очко на вес золота.

| Сборная | Ключевой фактор |
| --- | --- |
| Швейцария | опыт, стабильность, шестой ЧМ подряд |
| Босния и Герцеговина | капитан и бомбардир Эдин Джеко |

## Прогноз

Швейцария выглядит предпочтительнее по составу и турнирному опыту, но опыт и хладнокровие Джеко способны принести Боснии нужный результат. Если боснийцам удастся реализовать свои моменты, матч может завершиться сенсацией. По информации Sky Sports и UEFA, под вопросом участие защитника Сеада Колашинаца, получившего повреждение в стартовом туре.

Источники: Sky Sports, The Analyst, UEFA."""
})

# ---- normalize shape (endpoint requires image_url key present) ----
for a in articles:
    a.setdefault("image_url", None)

# ---- validation ----
assert len(articles)==8, len(articles)
assert sum(1 for a in articles if a["source_type"]=="news")==5
assert sum(1 for a in articles if a["source_type"]=="trend")==3
for a in articles:
    for f in ("title","slug","body","excerpt","category","type"):
        assert a[f].strip(), (a["slug"],f)
    assert a["sources"], a["slug"]
    assert "—" not in a["title"] and "—" not in a["excerpt"], a["slug"]
    assert "—" not in a["body"], a["slug"]
print("VALIDATION OK; 8 articles,", sum(len(a['body'].split()) for a in articles), "total words")

# ---- local archive + manifest ----
manifest={"generated_at":NOW,"run_id":RUN_ID,"articles":[]}
for a in articles:
    src = "news" if a["source_type"]=="news" else "trend"
    folder=f"articles/{src}-{a['slug']}"
    os.makedirs(folder,exist_ok=True)
    with open(f"{folder}/{src}-{a['slug']}.md","w") as f:
        f.write(f"# {a['title']}\n\n")
        f.write(f"> {a['excerpt']}\n\n")
        f.write(f"- Категория: {a['category']}\n- Тип: {a['type']}\n\n")
        f.write(a["body"].strip()+"\n")
    manifest["articles"].append({
        "title":a["title"],"slug":a["slug"],"body":a["body"],"excerpt":a["excerpt"],
        "category":a["category"],"type":a["type"],"image_url":a.get("image_url"),
        "image_base64":None,"sources":a["sources"],"source_type":a["source_type"]})
with open("logs/run-manifest-latest.json","w") as f:
    json.dump(manifest,f,ensure_ascii=False,indent=1)
print("archive + manifest written")

if os.environ.get("ARCHIVE_ONLY"):
    raise SystemExit(0)

# ---- publish ----
def post(items):
    payload=json.dumps({"articles":items}).encode("utf-8")
    req=urllib.request.Request(ENDPOINT, data=payload, method="POST",
        headers={"Content-Type":"application/json","x-agent-secret":SECRET})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, json.loads(r.read().decode())

if not SECRET:
    raise SystemExit("MISSING AGENT_PUBLISH_SECRET")

status, resp = post(articles)
print("HTTP", status)
print(json.dumps(resp, ensure_ascii=False, indent=1)[:2000])

results = resp.get("results", [])
# retry errors
errs = [r for r in results if r.get("status")=="error"]
if errs:
    slugs={r["slug"] for r in errs}
    retry=[a for a in articles if a["slug"] in slugs]
    print("RETRYING", slugs)
    time.sleep(3)
    s2,resp2=post(retry)
    print("retry HTTP",s2)
    # merge
    by={r["slug"]:r for r in results}
    for r in resp2.get("results",[]):
        by[r["slug"]]=r
    results=list(by.values())

# save results mapping
with open("/tmp/publish_results.json","w") as f:
    json.dump(results,f,ensure_ascii=False,indent=1)

# ---- logging ----
os.makedirs("logs",exist_ok=True)
team_map={
 "argentina-3-0-algeria-messi-hat-trick":(["Аргентина","Алжир"],["Лионель Месси"]),
 "fifa-zwane-three-match-ban-wc2026":(["ЮАР","Мексика"],["Темба Зване"]),
 "england-4-2-croatia-wc2026":(["Англия","Хорватия"],["Гарри Кейн","Джуд Беллингем","Маркус Рэшфорд"]),
 "mexico-south-korea-preview-wc2026":(["Мексика","Южная Корея"],["Сон Хын Мин"]),
 "portugal-1-1-dr-congo-ronaldo-wc2026":(["Португалия","ДР Конго"],["Криштиану Роналду","Жоау Невеш","Йоан Висса"]),
 "uzbekistan-1-3-colombia-wc2026":(["Узбекистан","Колумбия"],["Аббосбек Файзуллаев","Луис Диас"]),
 "top-7-bombardirov-start-chm-2026":([],["Лионель Месси","Килиан Мбаппе","Эрлинг Холанд","Гарри Кейн"]),
 "shveycariya-bosniya-preview-wc2026":(["Швейцария","Босния и Герцеговина"],["Эдин Джеко"]),
}
res_by={r["slug"].rstrip("0123456789-") if False else r["slug"]:r for r in results}
inserted=[r for r in results if r.get("status")=="inserted"]
with open("logs/articles-history.jsonl","a") as f:
    for a in articles:
        # find matching result (slug may be suffixed)
        rr=None
        for r in results:
            if r["slug"]==a["slug"] or r["slug"].startswith(a["slug"]+"-"):
                rr=r; break
        topic_full=a["excerpt"]
        teams,players=team_map.get(a["slug"],([],[]))
        entry={
          "timestamp":NOW,"run_id":RUN_ID,"source_type":a["source_type"],
          "type":a["type"],"title":a["title"],"slug":(rr or {}).get("slug",a["slug"]),
          "topic":topic_full,"teams":teams,"players":players,"sources":a["sources"],
          "status":(rr or {}).get("status","unknown")
        }
        f.write(json.dumps(entry,ensure_ascii=False)+"\n")

final_slugs=[(rr.get("slug") if (rr:=next((r for r in results if r["slug"]==a["slug"] or r["slug"].startswith(a["slug"]+"-")),None)) else a["slug"]) for a in articles]
with open("logs/last-run.json","w") as f:
    json.dump({"run_id":RUN_ID,"generated_at":NOW,"count":len(articles),
       "inserted":len(inserted),"db_slugs":final_slugs},f,ensure_ascii=False,indent=2)

print("\nINSERTED", len(inserted), "of", len(articles))
for r in results:
    print(" ", r.get("status"), r.get("slug"), r.get("error") or "")
EOF_MARKER_UNUSED = None
