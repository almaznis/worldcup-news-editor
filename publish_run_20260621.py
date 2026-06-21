#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WorldCupNewsAgent run for 2026-06-21. Builds 8 articles, attaches optimized
16:9 cover images (base64) and publishes to the Sport Arena Hub endpoint."""
import base64, io, json, os, sys, time, urllib.request, urllib.parse, datetime

from PIL import Image, ImageFilter

RUN_ID   = "run-20260621-wc2026"
GEN_AT   = "2026-06-21T09:30:00Z"
SECRET   = os.environ["AGENT_PUBLISH_SECRET"]
ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
UA       = {"User-Agent": "WCNewsBot/1.0 (almaznis1@gmail.com)"}

# ── Cover images: Wikimedia Commons file titles (real, CC-licensed photos) ────
IMAGE_TITLES = {
    "germany":   "File:Deniz Undav (middle) at BHA 5 v Espanyol 1 pre season 30 07 2022 39 (cropped).jpg",
    "netherlands":"File:Cody Gakpo 04012026 (1).jpg",
    "schlotterbeck":"File:Nico Schlotterbeck.jpg",
    "messi":     "File:20240204 Hong Kong v Inter Miami 03.png",
    "mbappe":    "File:Kylian Mbappé (46369981091).jpg",
    "yamal":     "File:Lamine Yamal in 2025 (cropped2).jpg",
    "russia":    "File:Russia football team.jpg",
}


def commons_thumb_url(title: str, width: int = 1600) -> str | None:
    params = {"action": "query", "format": "json", "titles": title,
              "prop": "imageinfo", "iiprop": "url", "iiurlwidth": width}
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    for p in data.get("query", {}).get("pages", {}).values():
        ii = p.get("imageinfo", [{}])[0]
        return ii.get("thumburl") or ii.get("url")
    return None


def make_cover_b64(title: str) -> str | None:
    """Download, frame to 1600x900 (16:9) with a blurred fill so the subject's
    face is never cropped, re-encode as JPEG < 500 KB, return base64."""
    try:
        turl = commons_thumb_url(title, 1600)
        if not turl:
            print(f"  ✗ no url for {title}")
            return None
        req = urllib.request.Request(turl, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
        src = Image.open(io.BytesIO(raw)).convert("RGB")
        W, H = 1600, 900
        # blurred cover background
        scale = max(W / src.width, H / src.height)
        bg = src.resize((max(1, int(src.width * scale)), max(1, int(src.height * scale))))
        left = (bg.width - W) // 2
        top = (bg.height - H) // 2
        bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(28))
        # darken background slightly
        dark = Image.new("RGB", (W, H), (0, 0, 0))
        bg = Image.blend(bg, dark, 0.25)
        # sharp contained foreground, centered
        fscale = min(W / src.width, H / src.height)
        fw, fh = max(1, int(src.width * fscale)), max(1, int(src.height * fscale))
        fg = src.resize((fw, fh))
        bg.paste(fg, ((W - fw) // 2, (H - fh) // 2))
        # encode under 500 KB
        for q in (85, 80, 72, 65, 58):
            buf = io.BytesIO()
            bg.save(buf, format="JPEG", quality=q, optimize=True)
            if buf.tell() <= 500_000:
                break
        b = buf.getvalue()
        print(f"  ↓ {title[:40]}… → {len(b)//1024} KB jpeg q{q}")
        return base64.b64encode(b).decode("ascii")
    except Exception as e:
        print(f"  ✗ {title}: {e}")
        return None


SRC = lambda *u: list(u)

# ─────────────────────────── ARTICLES ───────────────────────────
A1 = """## Ундав вырывает победу в компенсированное время

Сборная Германии вырвала драматичную победу над Кот-д'Ивуаром – 2:1 – во втором туре группы E чемпионата мира 2026 года и досрочно вышла в плей-офф. Решающий мяч нападающий Дениз Ундав забил на 90+4-й минуте, когда матч уже катился к ничьей.

«Африканские слоны» повели в счёте: по информации Fox Sports, полузащитник Франк Кесси открыл счёт примерно на 30-й минуте, наказав немцев за вязкую игру в первом тайме. Команда Юлиана Нагельсманна перестроилась после перерыва, и именно вышедший Ундав изменил ход встречи.

## Хроника матча

| Минута | Событие |
|---|---|
| ~30' | Гол. Франк Кесси выводит Кот-д'Ивуар вперёд (0:1) |
| 60' | Гол. Дениз Ундав сравнивает счёт (1:1) |
| 90+4' | Гол. Дениз Ундав приносит победу (2:1) |

Сначала Ундав восстановил равновесие на 60-й минуте, а в добавленное время хладнокровно поразил ворота во второй раз, отправив скамейку запасных Германии в эйфорию. Победа гарантировала «Бундестим» место в 1/8 финала за тур до конца группового этапа.

## Тревожный сигнал в обороне

Радость от выхода в плей-офф омрачила травма центрального защитника Нико Шлоттербека. Как сообщает Bavarian Football Works, игрок «Боруссии» Дортмунд повредил голеностоп уже на 15-й минуте в стыке с Амадом Диалло и был заменён в перерыве – вместо него на поле вышел Антонио Рюдигер. Нагельсманн после матча признал, что ситуация выглядит непросто и игрока ждёт МРТ.

## Что дальше

Германия с шестью очками возглавляет группу E и может позволить себе сэкономить силы в заключительном туре. Кот-д'Ивуар же оказался в сложном положении и сохраняет шансы на выход лишь как одна из лучших команд, занявших третьи места.

Ундав, начинавший турнир в роли резервиста, после этого матча превратился в одного из главных героев немецкой сборной на старте ЧМ-2026.

> Источники: Yahoo Sports, Fox Sports, Bavarian Football Works, OneFootball.
"""

A2 = """## Пять голов «оранье» в Хьюстоне

Сборная Нидерландов разгромила Швецию со счётом 5:1 во втором туре группы F чемпионата мира 2026 года и поднялась на первое место в квартете. Матч в Хьюстоне стал бенефисом дуэта Брайан Броббей – Коди Гакпо: оба форварда оформили по дублю.

После осечки в стартовом туре (ничья 2:2 с Японией) команда Роналда Кумана не оставила скандинавам шансов. По данным ESPN, Броббей дважды поразил ворота уже в первые 17 минут встречи, задав тон разгрому.

## Как развивался матч

В начале второго тайма солировал Гакпо: вингер «Ливерпуля» забил два мяча в первые десять минут после перерыва и снял все вопросы о победителе. Точку в разгроме поставил Кризенсио Сумервилл на 90-й минуте. Единственный мяч шведов на счету Энтони Эланги.

| Команда | Авторы голов |
|---|---|
| Нидерланды | Броббей (2), Гакпо (2), Сумервилл |
| Швеция | Эланга |

Незадолго до перерыва шведы забили ещё один гол, однако арбитры отменили взятие ворот из-за офсайда – иначе интрига могла бы сохраниться чуть дольше.

## Турнирный расклад

Победа вывела Нидерланды на вершину группы F и фактически отдала судьбу путёвки в плей-офф в собственные руки «оранье». В заключительном туре подопечные Кумана сыграют с Тунисом, и даже ничьей с высокой долей вероятности хватит для выхода в 1/8 финала.

Для Швеции поражение стало болезненным ударом: команде теперь нужна победа в последнем матче и благоприятное стечение обстоятельств, чтобы продолжить борьбу.

> Источники: ESPN, FIFA.com, Goal.com, Fox Sports.
"""

A3 = """## Травма в дебюте матча с Кот-д'Ивуаром

Сборная Германии может лишиться одного из основных защитников по ходу чемпионата мира 2026 года. Центральный защитник «Боруссии» Дортмунд Нико Шлоттербек получил повреждение голеностопа в матче второго тура группы E против Кот-д'Ивуара (2:1) и был заменён уже в перерыве.

По информации Bavarian Football Works, эпизод произошёл примерно на 15-й минуте: Шлоттербек неудачно приземлился в борьбе с ивуарийцем Амадом Диалло и подвернул левую ногу. Доиграть тайм защитник не смог – на поле вместо него вышел Антонио Рюдигер, составивший пару Йонатану Та.

## Нагельсманн: «Выглядит не лучшим образом»

Главный тренер немцев Юлиан Нагельсманн после игры подтвердил серьёзность ситуации.

> «У него что-то со внутренней связкой, завтра ему предстоит МРТ. К сожалению, это выглядит не лучшим образом», – приводит слова специалиста OneFootball.

Точный диагноз станет известен после обследования. Если опасения подтвердятся, Шлоттербек рискует пропустить значительную часть турнира, а то и завершить чемпионат мира досрочно.

## Что это значит для Германии

Несмотря на потерю, у Нагельсманна остаётся солидный выбор в центре обороны: Рюдигер и Та готовы закрыть позицию, а сама команда уже обеспечила себе место в плей-офф. Тем не менее травма ключевого левоного защитника накануне стадии на вылет – явно не та новость, которую хотел получить штаб «Бундестим».

Окончательная ясность по состоянию игрока появится после результатов МРТ.

> Источники: Bavarian Football Works, OneFootball, Yahoo Sports.
"""

A4 = """## Месси и Скалони – в шаге от плей-офф

Действующие чемпионы мира из Аргентины 22 июня сыграют против Австрии в матче второго тура группы J на стадионе «АТ&Т Стэдиум» в Арлингтоне (Даллас). Победа практически гарантирует команде Лионеля Скалони выход в 1/8 финала чемпионата мира 2026 года.

Аргентина мощно стартовала на турнире, обыграв Алжир со счётом 3:0. Лионель Месси оформил хет-трик и, по данным ESPN, сравнялся с Мирославом Клозе по числу голов на чемпионатах мира среди всех игроков в истории. Австрия под руководством Ральфа Рангника тоже взяла три очка, переиграв дебютанта Иорданию 3:1.

## Форма команд (1-й тур)

| Команда | Матч | Результат |
|---|---|---|
| Аргентина | – Алжир | 3:0 |
| Австрия | – Иордания | 3:1 |

Обе сборные набрали по три очка и делят лидерство в группе J, тогда как Алжир и Иордания пока идут без набранных баллов. Победитель очной встречи почти наверняка оформит путёвку в плей-офф досрочно.

## Ключевые факторы

Аргентина обладает лучшей разницей мячей и подходит к матчу с уверенностью, подкреплённой глубиной состава: помимо Месси, в предтурнирных встречах отличались Лаутаро Мартинес и Хулиан Альварес. Австрия же Рангника – дисциплинированная и агрессивная команда, способная навязать чемпионам мира борьбу.

## Прогноз

Аргентина выглядит фаворитом, однако австрийцы на старте показали характер и не намерены отдавать очки без боя. Наиболее вероятным выглядит результат, в котором «Альбиселеста» добивается своего, но соперник заставит её провести нервный отрезок. Ориентировочный прогноз – победа Аргентины с разницей в один-два мяча.

> Источники: ESPN, Goal.com, OneFootball.
"""

A5 = """## Холанд ведёт «викингов» к плей-офф

Сборная Норвегии 22 июня встретится с Сенегалом в матче второго тура группы I на «Метлайф Стэдиум» в Ист-Резерфорде. Для скандинавов, впервые за 28 лет вернувшихся на чемпионат мира, победа станет огромным шагом к выходу в плей-офф ЧМ-2026.

В стартовом туре Норвегия уверенно разобралась с Ираком – 4:1, причём Эрлинг Холанд оформил дубль и идёт в числе лучших бомбардиров турнира. Сенегал же, считавшийся одним из фаворитов группы, неожиданно уступил Франции со счётом 1:3 и теперь обязан побеждать, чтобы сохранить шансы.

## Положение в группе I (после 1-го тура)

| Команда | И | О |
|---|---|---|
| Норвегия | 1 | 3 |
| Франция | 1 | 3 |
| Сенегал | 1 | 0 |
| Ирак | 1 | 0 |

В параллельном матче тура Франция сыграет с Ираком. Расклад прост: Норвегия победой выходит в плей-офф, а Сенегалу поражение почти наверняка закрывает дорогу дальше.

## На что обратить внимание

Главная интрига встречи – дуэль атаки Холанда против скоростной и техничной полузащиты африканцев. Сенегал обладает классом, чтобы перевернуть ход группы, но психологическое давление после стартового поражения может сыграть против команды.

## Прогноз

Норвегия на кураже и с Холандом в оптимальной форме выглядит фаворитом домашнего для себя по атмосфере матча. Тем не менее загнанный в угол Сенегал способен выдать свой лучший футбол. Вероятен результативный и открытый матч; небольшое преимущество – на стороне «викингов».

> Источники: Sky Sports, ESPN, Yahoo Sports.
"""

A6 = """Гонка за «Золотой бутсой» чемпионата мира 2026 года разгорелась не на шутку. После двух туров группового этапа сразу несколько звёзд мирового футбола идут плотной группой. Мы собрали топ-7 бомбардиров турнира на данный момент – по данным Goal.com, Fox Sports и Olympics.com.

## 1. Лионель Месси (Аргентина) – 3 гола

Капитан «Альбиселесты» оформил хет-трик в матче с Алжиром (3:0) и сравнялся с Мирославом Клозе как самый результативный игрок в истории чемпионатов мира. В свои годы Месси по-прежнему задаёт тон.

## 2. Жонатан Давид (Канада) – 3 гола

Канадский форвард не отстаёт: его хет-трик помог хозяевам разгромить Катар 6:0. Давид делит первое место в гонке бомбардиров с Месси.

## 3. Сайл Ларин (Канада) – 2 гола

Партнёр Давида по сборной Канады вносит весомый вклад в результативную атаку хозяев турнира и держится в группе лидеров.

## 4. Килиан Мбаппе (Франция) – 2 гола

Капитан сборной Франции традиционно среди лучших снайперов. Два мяча на старте – заявка на то, чтобы побороться за «Золотую бутсу».

## 5. Эрлинг Холанд (Норвегия) – 2 гола

Норвежец вернулся на чемпионаты мира спустя 28 лет вместе со сборной и сразу оформил дубль в ворота Ирака (4:1).

## 6. Гарри Кейн (Англия) – 2 гола

Бессменный бомбардир «Трёх львов» продолжает исправно поражать ворота и остаётся ключевой фигурой английской атаки.

## 7. Кай Хаверц (Германия) – 2 гола

Форвард сборной Германии замыкает нашу семёрку, помогая «Бундестим» уверенно идти по турниру.

В число игроков с двумя голами также входят Фоларин Балогун (США), Элайджа Джаст (Новая Зеландия), Йохан Манзамби (Швейцария) и Ясин Айяри (Швеция). Борьба за «Золотую бутсу» только разгорается.

> Источники: Goal.com, Fox Sports, Olympics.com.
"""

A7 = """Чемпионат мира 2026 года уже подарил болельщикам несколько громких сенсаций. Аутсайдеры дают бой грандам, а дебютанты пишут историю. Мы собрали топ-5 главных сюрпризов группового этапа – по данным Fox Sports, Al Jazeera, FanSided и Yahoo Sports.

## 1. Испания 0:0 Кабо-Верде

Главная сенсация турнира. Один из фаворитов на победу, сборная Испании, не сумела пробить дебютанта Кабо-Верде (67-е место в рейтинге). «Голубые акулы» в первом же матче на чемпионатах мира отобрали очко у топ-команды. По словам наставника Саудовской Аравии Георгиоса Дониса, эта ничья может оказаться крупнейшим сюрпризом турнира.

## 2. Катар 1:1 Швейцария

Сборная Швейцария считалась явным фаворитом, однако Катар сумел зацепиться за ничью и отобрать важное очко у европейцев.

## 3. Босния и Герцеговина 1:1 Канада

Хозяева турнира из Канады при поддержке трибун не смогли дожать Боснию и Герцеговину. Ничья стала неожиданностью на фоне яркого старта канадцев в других матчах.

## 4. Иран 2:2 Новая Зеландия

Результативная ничья в группе G стала сюрпризом: Новая Зеландия проявила характер, а форвард Элайджа Джаст уже оформил два гола на турнире.

## 5. Исторический гол Кюрасао

Крошечный островной дебютант Кюрасао уступил Германии 1:7, но вписал своё имя в историю: Ливано Коменсия на 21-й минуте забил первый в истории страны гол на чемпионатах мира. Символический, но важный момент для футбола Кюрасао.

Групповой этап ЧМ-2026 ещё раз доказал: на чемпионате мира не бывает проходных соперников.

> Источники: Fox Sports, Al Jazeera, FanSided, Yahoo Sports, Wikipedia.
"""

A8 = """## ФИФА делает шаг навстречу

На фоне чемпионата мира 2026 года появилась новость, вызвавшая большой интерес в России и странах СНГ: ФИФА организует новый юношеский турнир для игроков до 15 лет, и участие в нём будет открыто для всех 211 национальных федераций – включая Россию. Об этом сообщает «Спортбокс».

Соревнование, по информации источника, планируется провести в сентябре 2026 года в США. Принципиальный момент – к участию допускаются сборные всех стран-членов ФИФА без исключений.

## Позиция РФС

Генеральный секретарь Российского футбольного союза Максим Митрофанов прокомментировал решение.

> «Ни одна страна-член ФИФА не может находиться под санкциями в рамках этого турнира. ФИФА возвращается к своему базовому принципу: футбол должен оставаться вне политики», – заявил Митрофанов.

## Важное уточнение: о взрослой сборной речи не идёт

Подчеркнём: речь идёт исключительно об участии юношеской команды до 15 лет в новом турнире, а не о возвращении главной сборной России. Взрослые команды и клубы остаются отстранёнными от соревнований под эгидой ФИФА и УЕФА с 2022 года.

Более того, 7 июня УЕФА продлил отстранение российских национальных сборных и клубов на сезон 2026/27, о чём сообщил Euronews. Таким образом, нынешний шаг носит символический и ограниченный характер: он касается лишь юношеского футбола и не означает снятия общих санкций.

Тем не менее в России новость восприняли как потенциальный сигнал к постепенному смягчению позиции международных федераций в отношении отечественного футбола.

> Источники: Спортбокс, Euronews, World Soccer Talk.
"""

ARTICLES = [
    {"key":"germany","source_type":"news","type":"match_report","category":"Отчёты о матчах",
     "title":"Германия 2:1 Кот-д'Ивуар: дубль Ундава в концовке выводит немцев в плей-офф ЧМ-2026",
     "slug":"germany-2-1-ivory-coast-world-cup-2026",
     "excerpt":"Дениз Ундав оформил дубль и на 90+4-й минуте принёс Германии победу над Кот-д'Ивуаром (2:1), досрочно выведя «Бундестим» в плей-офф ЧМ-2026.",
     "body":A1,
     "sources":SRC("https://sports.yahoo.com/soccer/live/world-cup-2026-scores-results-schedule-live-updates-195336732.html",
                   "https://www.foxsports.com/watch/fmc-dp1lx790vjfy42x5",
                   "https://www.bavarianfootballworks.com/germany-international-soccer/219250/germany-vs-ivory-coast-cote-divoire-nico-schlotterbeck-ligament-injury-diallo-kessie-rudiger-nagelsmann-musiala-undav-fifa-world-cup-wc")},
    {"key":"messi","source_type":"news","type":"preview","category":"ЧМ-2026",
     "title":"Аргентина – Австрия (22 июня): Месси и Скалони в шаге от плей-офф ЧМ-2026",
     "slug":"argentina-vs-austria-world-cup-2026-preview",
     "excerpt":"22 июня Аргентина сыграет с Австрией в группе J: победа почти наверняка выведет команду Лионеля Месси и Скалони в плей-офф чемпионата мира 2026.",
     "body":A4,
     "sources":SRC("https://www.espn.com/soccer/story/_/id/49120325/fifa-world-cup-2026-argentina-vs-austria-tv-channel-how-watch-kickoff-live-stream-referee-predicted-line-ups",
                   "https://www.goal.com/en-us/news/argentina-austria-world-cup-preview/blt540bff692d03f5a1",
                   "https://onefootball.com/en/news/argentina-vs-austria-prediction-world-cup-2026-preview-best-bets-43029991")},
    {"key":"schlotterbeck","source_type":"news","type":"transfer","category":"Новости игроков",
     "title":"Шлоттербек под вопросом на ЧМ-2026: травма связок голеностопа, Нагельсманн ждёт МРТ",
     "slug":"schlotterbeck-injury-germany-world-cup-2026",
     "excerpt":"Защитник сборной Германии Нико Шлоттербек повредил голеностоп в матче с Кот-д'Ивуаром и может пропустить часть ЧМ-2026. Нагельсманн ждёт результатов МРТ.",
     "body":A3,
     "sources":SRC("https://www.bavarianfootballworks.com/germany-international-soccer/219250/germany-vs-ivory-coast-cote-divoire-nico-schlotterbeck-ligament-injury-diallo-kessie-rudiger-nagelsmann-musiala-undav-fifa-world-cup-wc",
                   "https://onefootball.com/en/news/not-looking-good-nagelsmann-gives-injury-update-on-schlotterbeck-43036902",
                   "https://sports.yahoo.com/articles/germany-nico-schlotterbeck-suspected-ligament-230218352.html")},
    {"key":"mbappe","source_type":"trend","type":"ranking","category":"Тренды",
     "title":"Топ-7 бомбардиров ЧМ-2026: Месси сравнялся с Клозе, Жонатан Давид не отстаёт",
     "slug":"top-7-scorers-golden-boot-world-cup-2026",
     "excerpt":"Лионель Месси и Жонатан Давид с тремя голами возглавляют гонку за «Золотой бутсой» ЧМ-2026. Разбираем топ-7 лучших бомбардиров турнира.",
     "body":A6,
     "sources":SRC("https://www.goal.com/en/lists/world-cup-2026-golden-boot-standings-fifa-award/blt29fdba0896b8fd09",
                   "https://www.foxsports.com/stories/soccer/2026-fifa-world-cup-golden-boot-tracker",
                   "https://www.olympics.com/en/news/fifa-world-cup-2026-race-golden-boot-football-top-scorer-full-list")},
    {"key":"netherlands","source_type":"news","type":"match_report","category":"Отчёты о матчах",
     "title":"Нидерланды 5:1 Швеция: дубли Броббея и Гакпо отправляют «оранье» на вершину группы F",
     "slug":"netherlands-5-1-sweden-world-cup-2026",
     "excerpt":"Брайан Броббей и Коди Гакпо оформили по дублю, и Нидерланды разгромили Швецию 5:1, возглавив группу F на чемпионате мира 2026 года.",
     "body":A2,
     "sources":SRC("https://www.espn.com/soccer/story/_/id/49126635/netherlands-sweden-live-world-cup-2026-latest-updates-commentary-score-result",
                   "https://www.fifa.com/en/match-centre/match/17/285023/289273/400021472",
                   "https://www.foxsports.com/watch/fmc-4lygzu9o07pvbahv")},
    {"key":"schlotterbeck","source_type":"news","type":"preview","category":"ЧМ-2026",
     "title":"Норвегия – Сенегал (22 июня): Холанд ведёт «викингов» к плей-офф ЧМ-2026",
     "slug":"norway-vs-senegal-world-cup-2026-preview",
     "excerpt":"22 июня Норвегия с Эрлингом Холандом встретится с Сенегалом в группе I: на кону – путёвка в плей-офф чемпионата мира 2026 года.",
     "body":A5,
     "img_override":"russia" if False else None,
     "sources":SRC("https://www.skysports.com/football/news/12098/13543102/world-cup-2026-group-i-guide-fixtures-schedule-standings-and-odds-for-france-senegal-iraq-and-norway",
                   "https://www.espn.com/soccer/story/_/id/49082534/group-2026-world-cup-teams-records-stats-know-france-senegal-iraq-norway",
                   "https://sports.yahoo.com/soccer/article/2026-world-cup-results-standings-and-schedule-live-scores-group-stage-updates-and-how-to-watch-050724193.html")},
    {"key":"russia","source_type":"trend","type":"transfer","category":"Тренды",
     "title":"ФИФА открывает двери: Россия сможет сыграть на новом юношеском турнире U-15 в США",
     "slug":"fifa-u15-tournament-russia-eligibility-2026",
     "excerpt":"ФИФА допускает все 211 федераций, включая Россию, к новому юношескому турниру U-15 в сентябре 2026 года. При этом отстранение взрослых сборных остаётся в силе.",
     "body":A8,
     "sources":SRC("https://news.sportbox.ru/Vidy_sporta/Futbol/spbnews_NI2335639_FIFA_vernula_sbornuju_Rossii_na_mezhdunarodnuju_arenu_Smelyj_shag_vo_vrema_ChM_2026",
                   "https://www.euronews.com/my-europe/2026/06/07/uefa-extends-ban-on-russian-national-teams-and-clubs-from-competitions-for-202627-season",
                   "https://worldsoccertalk.com/world-cup/why-russia-is-missing-the-2026-world-cup-fifa-ban-explained/")},
    {"key":"yamal","source_type":"trend","type":"ranking","category":"Тренды",
     "title":"Топ-5 сенсаций группового этапа ЧМ-2026: Кабо-Верде остановила Испанию",
     "slug":"top-5-sensations-group-stage-world-cup-2026",
     "excerpt":"Ничья Испании с дебютантом Кабо-Верде, осечки Швейцарии и Канады, исторический гол Кюрасао – собираем топ-5 сенсаций группового этапа ЧМ-2026.",
     "body":A7,
     "sources":SRC("https://www.foxsports.com/stories/soccer/biggest-upsets-world-cup-history-where-does-spain-vs-cape-verde-rank",
                   "https://fansided.com/soccer/spain-stunned-ronaldo-ruined-biggest-shocks-world-cup-standings-so-far",
                   "https://sports.yahoo.com/articles/fit-tied-big-upsets-world-070134728.html")},
]

# fix: norway preview should use schlotterbeck? no -> use messi? give it its own image (russia team not apt).
# Use the Norway/Haaland-less; assign messi image is wrong. We'll map norway preview to 'mbappe' image? better generic.
IMG_MAP = {
    "germany-2-1-ivory-coast-world-cup-2026":"germany",
    "argentina-vs-austria-world-cup-2026-preview":"messi",
    "schlotterbeck-injury-germany-world-cup-2026":"schlotterbeck",
    "top-7-scorers-golden-boot-world-cup-2026":"mbappe",
    "netherlands-5-1-sweden-world-cup-2026":"netherlands",
    "norway-vs-senegal-world-cup-2026-preview":"russia",  # placeholder, overridden below
    "fifa-u15-tournament-russia-eligibility-2026":"russia",
    "top-5-sensations-group-stage-world-cup-2026":"yamal",
}


def main():
    # Build cover images
    print("Building cover images…")
    needed = set(IMG_MAP.values())
    # Norway preview: use a Haaland landscape if available, else fall back. We'll
    # resolve a Haaland image specifically.
    IMAGE_TITLES["haaland"] = "File:Erling Haaland 2023.jpg"
    IMG_MAP["norway-vs-senegal-world-cup-2026-preview"] = "haaland"
    needed = set(IMG_MAP.values())
    covers = {}
    for k in needed:
        covers[k] = make_cover_b64(IMAGE_TITLES[k])
        time.sleep(3)

    payload = []
    for a in ARTICLES:
        imgkey = IMG_MAP[a["slug"]]
        b64 = covers.get(imgkey)
        obj = {"title":a["title"],"slug":a["slug"],"body":a["body"],
               "excerpt":a["excerpt"],"category":a["category"],"type":a["type"],
               "image_url":None,"image_base64":b64,"sources":a["sources"],
               "source_type":a["source_type"]}
        payload.append(obj)

    missing = [p["slug"] for p in payload if not p["image_base64"]]
    if missing:
        print("WARNING: missing cover images for:", missing)

    body = json.dumps({"articles":payload}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST",
        headers={"Content-Type":"application/json","x-agent-secret":SECRET})
    print(f"\nPOSTing {len(payload)} articles…")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.load(r)
            print("HTTP", r.status)
    except urllib.error.HTTPError as e:
        print("HTTP ERROR", e.code, e.read().decode("utf-8")[:500]); sys.exit(1)
    print(json.dumps(resp, ensure_ascii=False, indent=2))

    # Save results + payload (without base64) for manifest/logging
    with open("/tmp/run_results.json","w") as f:
        json.dump({"resp":resp,
                   "articles":[{k:v for k,v in p.items() if k!="image_base64"}
                               for p in payload],
                   "img_map":IMG_MAP,
                   "generated_at":GEN_AT,"run_id":RUN_ID}, f, ensure_ascii=False, indent=2)
    print("\nSaved /tmp/run_results.json")


if __name__ == "__main__":
    main()
