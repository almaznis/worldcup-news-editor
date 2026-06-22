# -*- coding: utf-8 -*-
"""
WorldCupNewsAgent run — 2026-06-22.
8 articles (5 news + 3 trend) about FIFA World Cup 2026 group stage.
Covers: Wikimedia Commons (CC), letterboxed to 16:9 JPEG, base64 -> images bucket.
"""
import base64, io, json, os, time, datetime, pathlib
import requests
from PIL import Image, ImageOps, ImageFilter

RUN_ID   = "run-20260622-wc2026-grp"
SECRET   = os.environ["AGENT_PUBLISH_SECRET"]
ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
NOW_ISO  = datetime.datetime.now(datetime.timezone.utc).isoformat()

S = requests.Session()
S.headers.update({"User-Agent": "WorldCupNewsAgent/1.0 (editorial; almaznis1@gmail.com)"})
COMMONS = "https://commons.wikimedia.org/w/api.php"

# ── cover image: Wikimedia file title per slug ───────────────────────────────
COVER_FILE = {
    "spain-4-0-saudi-arabia-yamal-oyarzabal-world-cup-2026":
        "File:Lamine Yamal in 2025.jpg",
    "japan-4-0-tunisia-1000th-world-cup-match-ueda":
        "File:Ayase-ueda.png",
    "germany-2-1-ivory-coast-undav-world-cup-2026":
        "File:Deniz Undav (middle) at BHA 5 v Espanyol 1 pre season 30 07 2022 39 (cropped).jpg",
    "curacao-0-0-ecuador-room-first-world-cup-point-2026":
        "File:Room Eloy Columbus Crew SC Meet the Team 2019.jpg",
    "cabo-verde-first-world-cup-goal-lenini-krasnodar-uruguay-2026":
        "File:Kevin Pina (footballer) 2022.jpg",
    "portugal-uzbekistan-preview-world-cup-2026":
        "File:Cristiano Ronaldo with Al Nassr, 19 September 2023 - 44.jpg",
    "top-7-golden-boot-race-world-cup-2026":
        "File:Lionel Messi 20180626.jpg",
    "top-7-sensations-group-stage-world-cup-2026":
        "File:Fayzullaev, Arthur, Douglas Santos.jpg",
}

def fetch_bytes(title):
    r = S.get(COMMONS, params={"action": "query", "titles": title, "prop": "imageinfo",
              "iiprop": "url", "iiurlwidth": 1600, "format": "json"}, timeout=40).json()
    pg = list(r["query"]["pages"].values())[0]
    url = pg["imageinfo"][0]["thumburl"]
    time.sleep(3)  # respect Wikimedia rate limits
    return S.get(url, timeout=60).content

def make_cover_b64(title):
    raw = fetch_bytes(title)
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    W, H = 1600, 900
    bg = ImageOps.fit(im, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    # darken backdrop a touch
    bg = Image.eval(bg, lambda p: int(p * 0.7))
    fg = im.copy(); fg.thumbnail((W, H), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    out = io.BytesIO(); bg.save(out, "JPEG", quality=82, optimize=True)
    data = out.getvalue()
    print(f"   cover {title[:40]:40s} -> {len(data)//1024} KB")
    return base64.b64encode(data).decode()


# ╔══ ARTICLE BODIES ═════════════════════════════════════════════════════════╗

A1 = """Испания разгромила Саудовскую Аравию со счётом 4:0 в матче группы H чемпионата мира – 2026 и оформила путёвку в плей-офф. Подопечные Луиса де ла Фуэнте провели образцовый первый тайм в Атланте 21 июня и реабилитировались за нулевую ничью с дебютантами из Кабо-Верде в стартовом туре.

«Красная фурия» решила исход встречи ещё до перерыва. Уже на 10-й минуте отличился вернувшийся в стартовый состав Ламин Ямаль, а затем дубль в течение трёх минут оформил Микель Оярсабаль (21-я и 24-я). Испания стала первой сборной со времён Германии образца 2014 года, которой удалось забить три мяча в первые 25 минут матча на чемпионате мира.

## Ход матча

С первых минут испанцы прижали соперника к штрафной и завладели тотальным контролем над мячом. Ямаль открыл счёт точным ударом, после чего инициативу подхватил Оярсабаль, дважды наказавший разобранную оборону саудовцев. Уверенно завершив первую половину, де ла Фуэнте на перерыве снял с игры обоих авторов голов, поберёг лидеров и сохранил их свежесть для решающей стадии турнира.

Четвёртый мяч оказался на счету хозяев поля по воле случая: после розыгрыша углового удар Марка Кукурельи отразил вратарь Аль-Овайс, но мяч от защитника Хассана Аль-Тамбакти влетел в собственные ворота на 49-й минуте.

## Статистика матча

| Показатель | Испания | Саудовская Аравия |
| --- | --- | --- |
| Голы | 4 | 0 |
| Авторы голов | Ямаль (10), Оярсабаль (21, 24), Аль-Тамбакти (49, автогол) | – |
| Итог | Победа и выход в 1/16 финала | Поражение |

## Что дальше

Победа вывела Испанию в 1/16 финала турнира, который впервые принимают США, Канада и Мексика. Команда де ла Фуэнте, считающаяся одним из главных фаворитов чемпионата, набрала ход в нужный момент и подтвердила статус претендента на трофей.

> «Это был наш настоящий старт на турнире», – таков был общий тон испанской прессы после уверенной победы.

Источники: Sky Sports, ESPN, FIFA, Al Jazeera."""

A2 = """Сборная Японии разгромила Тунис со счётом 4:0 в матче группы F чемпионата мира – 2026 и фактически обеспечила себе место в плей-офф. Эта встреча 21 июня в Монтеррее вошла в историю как 1000-й матч в истории чемпионатов мира.

Дубль оформил форвард Аясэ Уэда, ещё по мячу добавили Дайти Камада и Дзюнъя Ито. Япония стала первой азиатской сборной, забившей четыре гола в одном матче на чемпионате мира, и набрала четыре очка, разделив первую строчку группы с Нидерландами.

## Ход матча

Японцы доминировали с первых минут. Уэда воспользовался нерешительностью тунисской обороны, ворвался в штрафную и пробил низом в дальний угол, открыв счёт. Затем своё слово сказали Камада и Ито, а точку в разгроме поставил всё тот же Уэда, головой замкнувший навес Кайсю Сано. Своим дублем с результативной передачей форвард повторил достижение Коди Гакпо – единственного на тот момент игрока турнира, оформившего «гол + гол + пас» в одной встрече.

Для Туниса под руководством Эрве Ренара турнир завершился досрочно: команда выбыла из борьбы за плей-офф за тур до конца группового этапа.

## Статистика матча

| Показатель | Тунис | Япония |
| --- | --- | --- |
| Голы | 0 | 4 |
| Авторы голов | – | Уэда (2), Камада, Ито |
| Положение в группе | Выбыли | 4 очка, дележ 1-го места |

## Исторический контекст

Матч в Монтеррее стал юбилейным, тысячным в истории мировых первенств, и японцы отметили эту веху ярким выступлением. Команда продолжает свой путь по турнирной сетке и подтверждает, что готова навязать борьбу грандам на стадии плей-офф.

Источники: Sky Sports, Al Jazeera, FIFA, The Analyst (Opta)."""

A3 = """Сборная Германии вырвала победу над Кот-д'Ивуаром со счётом 2:1 в матче группы E чемпионата мира – 2026 и досрочно вышла в 1/16 финала. Решающий мяч на 94-й минуте забил вышедший на замену Дениз Ундав, оформивший дубль и принёсший своей команде драматичный успех в Торонто 20 июня.

Подопечные Юлиана Нагельсманна по ходу встречи уступали, но сумели переломить ход игры благодаря замене. Германия присоединилась к США и Мексике в числе сборных, оформивших путёвку в плей-офф за тур до конца группового этапа.

## Ход матча

Первыми повели ивуарийцы: на 30-й минуте отличился капитан африканской команды Франк Кессье. Германия же оживилась после выхода Ундава на 60-й минуте. Сначала, на 68-й минуте, форвард замкнул навес другого запасного, Надима Амири, ударом с лёта пробив голкипера Яхью Фофана. А в компенсированное время Феликс Нмеча выдал точный пас на Ундава, который обработал мяч, развернулся и хлёстким ударом из штрафной принёс победу.

Голы forварда, ставшего супер-джокером, довели его счёт до девяти мячей в 11 матчах за национальную команду.

## Статистика матча

| Показатель | Кот-д'Ивуар | Германия |
| --- | --- | --- |
| Голы | 1 | 2 |
| Авторы голов | Кессье (30) | Ундав (68, 90+4) |
| Зрителей | – | около 43 000 |
| Итог | Поражение | Победа и выход в 1/16 финала |

## Что дальше

Поздний гол Ундава вывел Германию в плей-офф и снял часть вопросов к команде Нагельсманна после непростого старта. «Бундестим» сохраняет статус одного из претендентов на трофей и готовится к решающим матчам турнира.

Источники: Sky Sports, ESPN, CBS Sports, The Analyst (Opta)."""

A4 = """Сборная Кюрасао сотворила одну из главных сенсаций чемпионата мира – 2026, удержав нулевую ничью в матче группы E против Эквадора 20 июня в Канзас-Сити. Для самой маленькой страны в истории мировых первенств это первое очко на турнире.

Главным героем встречи стал голкипер Элой Рум, отразивший 15 ударов – это наибольшее число сейвов вратаря за 90 минут матча чемпионата мира с тех пор, как ведётся официальная статистика (с 1966 года). Эквадор нанёс 28 ударов, но так и не сумел распечатать ворота дебютантов.

## Подвиг вратаря

Эквадорцы провели встречу с тотальным территориальным преимуществом и обрушили на ворота Кюрасао шквал атак. Однако Рум раз за разом выручал свою команду, оставшись всего в одном сейве от рекорда результативности голкипера в отдельном матче мировых первенств. Оборона островитян выстояла под непрерывным давлением и принесла исторический результат.

## Самая маленькая страна в истории

Кюрасао – остров с населением около 156 тысяч человек – стал самой маленькой по числу жителей страной, когда-либо пробивавшейся в финальную стадию чемпионата мира. Нулевая ничья с Эквадором принесла дебютантам первое в истории очко на мундиале и стала символом того, как расширенный до 48 команд турнир открывает дорогу новым участникам.

> Матчи вроде этого напоминают, что на чемпионате мира величие команды измеряется не только размерами страны.

Источники: Al Jazeera, Yahoo Sports, NBC News, ESPN."""

A5 = """Сборная Кабо-Верде забила первый гол в своей истории на чемпионатах мира и завоевала очко в матче против Уругвая – 2:2 в группе H мундиаля-2026. Игра прошла 21 июня в Майами, а автором исторического мяча стал полузащитник «Краснодара» Ленини.

29-летний хавбек, известный в России как игрок «Краснодара» (полное имя – Кевин Пина), отличился уже на 21-й минуте. Со штрафного примерно с 25 метров он пробил низом и застал врасплох голкипера Уругвая Фернандо Муслеру, открыв счёт и вписав своё имя в историю африканской сборной.

## Как развивалась игра

Уругвай ответил до перерыва: на 44-й минуте счёт сравнял Макси Араухо, а в компенсированное время первого тайма (45+6) Агустин Канобьо вывел «Селесте» вперёд. Однако Кабо-Верде не сдался: на 61-й минуте Элио Варела восстановил равновесие – 2:2.

Ничья стала ещё одним ярким эпизодом дебютного для Кабо-Верде чемпионата мира. Ранее островитяне сенсационно сдержали Испанию (0:0), а теперь отобрали очки и у двукратных чемпионов мира.

## Российский след

Особый интерес к матчу в странах СНГ объясняется тем, что автор гола выступает в российской Премьер-лиге за «Краснодар». Болельщики, следящие за РПЛ, увидели знакомого по чемпионату России футболиста в роли творца исторического момента на мировом первенстве.

> Первый гол Кабо-Верде на чемпионатах мира войдёт в историю страны, а его автор – в число знаковых легионеров российского первенства.

Источники: FIFA (протокол матча), Sunday Guardian, Outlook India, Спорт-Экспресс."""

A6 = """Сборная Португалии встретится с Узбекистаном 23 июня в Хьюстоне в матче группы K чемпионата мира – 2026, и эта игра вызывает повышенный интерес в Казахстане и Центральной Азии. Для Узбекистана это исторический дебют на мировом первенстве, а для Криштиану Роналду и его команды – встреча, в которой нельзя терять очки.

После первого тура расклад в группе K выглядит так: Колумбия лидирует с тремя очками, ДР Конго и Португалия имеют по одному, а Узбекистан пока без набранных баллов. Португалия неожиданно сыграла вничью с ДР Конго (1:1), тогда как сборная Узбекистана уступила Колумбии со счётом 1:3, но провела достойный матч.

## Положение в группе K (после 1-го тура)

| Команда | Очки |
| --- | --- |
| Колумбия | 3 |
| ДР Конго | 1 |
| Португалия | 1 |
| Узбекистан | 0 |

## Ставки матча

Португалия не может позволить себе ещё одну осечку: победа вернула бы команду Роберто Мартинеса в борьбу за первое место и сохранила бы её судьбу в собственных руках. Узбекистану же нужна победа, чтобы оставить шансы на плей-офф.

В центре внимания – дуэль полузащиты. Креативным мотором португальцев остаётся Бруну Фернандеш, на счету которого 29 голов в 88 матчах за сборную. Сдерживать его предстоит узбекскому дуэту опорников Одилжона Хамробекова и Достонбека Хамдамова.

Отдельная интрига связана с Криштиану Роналду. 41-летний форвард стал самым возрастным полевым игроком, выходившим в стартовом составе на матч чемпионата мира, но пока остаётся без забитых мячей и под прицелом критики.

## Исторический дебют Узбекистана

Для Узбекистана турнир уже принёс исторический момент: Аббосбек Файзуллаев забил в ворота Колумбии первый гол сборной на чемпионатах мира. Полузащитник, выступающий за московский ЦСКА, стал одним из символов дебютной кампании. Успех соседей по региону вызывает живой отклик у болельщиков Казахстана и всего СНГ.

## Прогноз

Фаворитом встречи считается Португалия, обладающая более звёздным и опытным составом. Однако Узбекистан, которому нужна только победа, способен navязать борьбу и продолжить писать историю своего первого чемпионата мира. Ожидается напряжённый матч с territориальным преимуществом европейцев.

Источники: Sky Sports, Goal.com, FIFA, Yahoo Sports."""

A7 = """Групповой этап чемпионата мира – 2026 в самом разгаре, и борьба за приз лучшему бомбардиру турнира («Золотую бутсу») обещает быть жаркой. Мы собрали топ-7 претендентов на награду по итогам первых туров – от лидеров с тремя мячами до целой группы преследователей. Рейтинг учитывает количество забитых голов на турнире; игроки с равным числом мячей перечислены без учёта дополнительных показателей.

## 1. Лионель Месси (Аргентина) – 3 гола

Капитан действующих чемпионов мира открыл турнир хет-триком в ворота Алжира (3:0) и возглавил гонку бомбардиров. На рекордном для себя шестом чемпионате мира 38-летний Месси доказывает, что по-прежнему способен решать судьбу матчей в одиночку.

## 2. Джонатан Дэвид (Канада) – 3 гола

Форвард сборной Канады ответил Месси собственным хет-триком и делит первую строчку в споре за «Золотую бутсу». Дэвид стал главным открытием стартовых туров и ведёт хозяев турнира вперёд.

## 3. Килиан Мбаппе (Франция) – 2 гола

Лидер сборной Франции продолжает переписывать рекорды: его мячи помогли «трёхцветным» обыграть Сенегал (3:1), а сам Мбаппе обошёл Оливье Жиру и стал лучшим бомбардиром в истории французской национальной команды.

## 4. Эрлинг Холанд (Норвегия) – 2 гола

Дебют на чемпионате мира Холанд отметил дублем в разгромном матче с Ираком (4:1). Норвежец впервые вышел на мундиаль и сразу включился в борьбу за индивидуальный приз.

## 5. Гарри Кейн (Англия) – 2 гола

Капитан сборной Англии остаётся одним из самых стабильных бомбардиров своего поколения и держится в группе преследователей лидеров.

## 6. Винисиус Жуниор (Бразилия) – 2 гола

Вингер «Реала» подключился к гонке и поддерживает атакующую мощь пятикратных чемпионов мира.

## 7. Микель Оярсабаль (Испания) – 2 гола

Форвард «Реал Сосьедада» оформил дубль в ворота Саудовской Аравии (4:0) и ворвался в число лидеров гонки бомбардиров, помогая Испании набирать ход.

## Вывод

Гонка за «Золотую бутсу» только разгорается: Месси и Дэвид задают темп, но плотная группа преследователей с двумя мячами способна перевернуть расклад уже в ближайших турах. Чем дальше по сетке, тем дороже будет каждый гол.

Источники: Goal.com, ESPN, FIFA, NBC Sports."""

A8 = """Расширенный до 48 команд чемпионат мира – 2026 подарил болельщикам уже немало сюрпризов. Дебютанты отбирают очки у грандов, вратари творят чудеса, а карта мирового футбола заметно расширяется. Собрали топ-7 главных сенсаций группового этапа – с акцентом на сюжеты, которые особенно интересны зрителям в Казахстане и СНГ.

## 1. Кюрасао отбирает очко у Эквадора

Самая маленькая страна в истории чемпионатов мира – остров с населением около 156 тысяч человек – удержала нулевую ничью с Эквадором. Голкипер Элой Рум совершил 15 сейвов, наибольшее число для вратаря за 90 минут матча мундиаля с 1966 года, и принёс дебютантам историческое первое очко.

## 2. Кабо-Верде и российский след

Дебютанты из Кабо-Верде сначала сдержали Испанию (0:0), а затем сыграли вничью с Уругваем (2:2). Первый в истории страны гол на чемпионатах мира забил полузащитник «Краснодара» Ленини – знакомый болельщикам РПЛ легионер стал творцом исторического момента.

## 3. Иран сдерживает Бельгию

Сборная Ирана выдала самоотверженный оборонительный матч и удержала нулевую ничью против Бельгии. Дисциплинированная игра в защите позволила иранцам отобрать очки у одного из европейских грандов.

## 4. Первый гол Узбекистана на чемпионатах мира

Узбекистан дебютировал на мундиале и сразу вписал своё имя в историю: Аббосбек Файзуллаев, выступающий за московский ЦСКА, забил первый гол сборной на чемпионатах мира в матче с Колумбией. Для болельщиков Центральной Азии это событие особого значения.

## 5. Норвегия спустя 28 лет

Норвегия вернулась на чемпионат мира впервые за 28 лет и сразу заявила о себе: Эрлинг Холанд оформил дубль в разгромном матче с Ираком (4:1). Возвращение «викингов» с одним из лучших форвардов планеты – одно из главных украшений турнира.

## 6. Пробуксовка Португалии и Роналду

Португалия с Криштиану Роналду неожиданно потеряла очки в стартовом туре, сыграв вничью с ДР Конго (1:1). 41-летний форвард, ставший самым возрастным полевым игроком в стартовых составах в истории мундиалей, пока остаётся без голов.

## 7. Японский рекорд

Сборная Японии стала первой азиатской командой, забившей четыре мяча в одном матче чемпионата мира, разгромив Тунис (4:0) в юбилейной, 1000-й игре в истории мировых первенств.

## Вывод

Групповой этап подтвердил главный тренд расширенного турнира: разрыв между фаворитами и аутсайдерами сокращается, а каждый тур приносит новые сенсации. Впереди – не менее интригующая стадия плей-офф.

Источники: Al Jazeera, FIFA, Sky Sports, Спорт-Экспресс."""

# fix latin-letter typos introduced above (defensive cleanup)
import re
def ru_clean(t):
    return (t.replace("forвард","форвард").replace("navязать","навязать")
             .replace("territориальным","территориальным"))
A3 = ru_clean(A3); A6 = ru_clean(A6)

ARTICLES = [
 {"slug":"spain-4-0-saudi-arabia-yamal-oyarzabal-world-cup-2026",
  "title":"Испания 4:0 Саудовская Аравия: Ямаль и дубль Оярсабаля выводят «Красную фурию» в плей-офф ЧМ-2026",
  "excerpt":"Испания разгромила Саудовскую Аравию 4:0 в Атланте благодаря голам Ямаля и дублю Оярсабаля и вышла в 1/16 финала чемпионата мира – 2026.",
  "category":"Отчёты о матчах","type":"match_report","source_type":"news","body":A1,
  "sources":["https://www.skysports.com/football/news/12098/13553799/world-cup-2026-spain-4-0-saudi-arabia-lamine-yamal-and-mikel-oyarzabal-star-as-la-roja-earn-first-group-h-win",
             "https://www.espn.com/soccer/match/_/gameId/760453/saudi-arabia-spain",
             "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/spain-saudi-arabia-highlights-match-report",
             "https://www.aljazeera.com/sports/liveblog/2026/6/21/spain-vs-saudi-arabia-live-world-cup-2026"]},

 {"slug":"japan-4-0-tunisia-1000th-world-cup-match-ueda",
  "title":"Япония 4:0 Тунис: дубль Уэды в юбилейном 1000-м матче чемпионатов мира",
  "excerpt":"Япония разгромила Тунис 4:0 в 1000-м по счёту матче в истории чемпионатов мира; дубль оформил Аясэ Уэда, а Тунис выбыл из турнира.",
  "category":"Отчёты о матчах","type":"match_report","source_type":"news","body":A2,
  "sources":["https://www.skysports.com/football/news/11095/13553793/world-cup-2026-tunisia-0-4-japan-ayase-ueda-scores-twice-as-tunisias-tournament-ends-in-disappointment",
             "https://www.aljazeera.com/sports/2026/6/21/japan-tunisia-4-0-fifa-world-cup-2026-ayase-ueda-daichi-kamada-junya-ito",
             "https://www.fifa.com/en/match-centre/match/17/285023/289273/400021475",
             "https://theanalyst.com/articles/tunisia-vs-japan-stats-world-cup-2026-live"]},

 {"slug":"germany-2-1-ivory-coast-undav-world-cup-2026",
  "title":"Германия 2:1 Кот-д'Ивуар: дубль Ундава на 94-й минуте выводит «Бундестим» в 1/16 финала",
  "excerpt":"Дениз Ундав вышел на замену и оформил дубль, включая победный гол на 94-й минуте, – Германия обыграла Кот-д'Ивуар 2:1 и вышла в плей-офф ЧМ-2026.",
  "category":"Отчёты о матчах","type":"match_report","source_type":"news","body":A3,
  "sources":["https://www.skysports.com/football/news/12098/13553785/world-cup-2026-germany-2-1-ivory-coast-deniz-undav-scores-94th-minute-winner-in-group-e-clash",
             "https://www.espn.com/soccer/match/_/gameId/760448/ivory-coast-germany",
             "https://www.cbssports.com/soccer/news/germany-vs-ivory-coast-live-updates-world-cup-2026-score-result/live/",
             "https://theanalyst.com/articles/germany-vs-ivory-coast-stats-world-cup-2026"]},

 {"slug":"curacao-0-0-ecuador-room-first-world-cup-point-2026",
  "title":"Кюрасао 0:0 Эквадор: 15 сейвов Рума приносят самой маленькой стране историческое очко на ЧМ-2026",
  "excerpt":"Голкипер Элой Рум отразил 15 ударов, и Кюрасао – самая маленькая страна в истории чемпионатов мира – удержал нулевую ничью с Эквадором и взял первое очко.",
  "category":"ЧМ-2026","type":"transfer","source_type":"news","body":A4,
  "sources":["https://www.aljazeera.com/sports/2026/6/21/room-the-hero-as-tiny-curacao-earn-first-world-cup-point-against-ecuador",
             "https://sports.yahoo.com/soccer/article/2026-world-cup-eloy-rooms-15-save-masterclass-helps-curacao-stun-ecuador-in-0-0-draw-020003395.html",
             "https://www.nbcnews.com/sports/soccer/curacao-smalles-nation-world-cup-rcna348528",
             "https://www.espn.com/soccer/match/_/gameId/760446"]},

 {"slug":"cabo-verde-first-world-cup-goal-lenini-krasnodar-uruguay-2026",
  "title":"Полузащитник «Краснодара» Ленини забил первый гол Кабо-Верде в истории ЧМ: ничья с Уругваем 2:2",
  "excerpt":"Игрок «Краснодара» Ленини со штрафного забил первый в истории Кабо-Верде гол на чемпионатах мира; дебютанты сыграли вничью с Уругваем 2:2.",
  "category":"Новости игроков","type":"transfer","source_type":"news","body":A5,
  "sources":["https://www.fifa.com/en/match-centre/match/17/285023/289273/400021487",
             "https://sundayguardianlive.com/sports/who-is-kevin-pina-29-year-old-midfielder-scores-cabo-verdes-first-ever-fifa-world-cup-goal-in-uruguay-vs-cabo-verde-match-211064/",
             "https://www.outlookindia.com/sports/football/uruguay-vs-cape-verde-live-score-fifa-world-cup-2026-group-h-uru-v-cpv-updates-miami-stadium-highlights",
             "https://www.sport-express.ru/football/world/chempionat-mira-2026/news/chempionat-mira-po-futbolu-2026-raspisanie-i-rezultaty-21-22-iyunya-ispaniya-saudovskaya-araviya-belgiya-iran-urugvay-kabo-verde-2432789/"]},

 {"slug":"portugal-uzbekistan-preview-world-cup-2026",
  "title":"Португалия – Узбекистан: превью матча ЧМ-2026, в котором Роналду нельзя терять очки",
  "excerpt":"23 июня Португалия Роналду сыграет с дебютантом мундиаля Узбекистаном. Разбираем расклад в группе K, ключевых игроков и прогноз на матч ЧМ-2026.",
  "category":"ЧМ-2026","type":"preview","source_type":"trend","body":A6,
  "sources":["https://www.skysports.com/football/news/12040/13543106/world-cup-2026-group-k-guide-fixtures-schedule-standings-and-odds-for-portugal-dr-congo-uzbekistan-and-colombia",
             "https://www.goal.com/en/news/portugal-uzbekistan-world-cup-preview/bltf65b8be15166aad7",
             "https://www.fifa.com/en/match-centre/match/17/285023/289273/400021503",
             "https://sports.yahoo.com/articles/portugal-vs-uzbekistan-picks-predictions-090406819.html"]},

 {"slug":"top-7-golden-boot-race-world-cup-2026",
  "title":"Топ-7 претендентов на «Золотую бутсу» ЧМ-2026: Месси и Дэвид задают темп",
  "excerpt":"Месси и Джонатан Дэвид лидируют с тремя голами, а плотная группа преследователей готова вмешаться в борьбу. Топ-7 претендентов на «Золотую бутсу» ЧМ-2026.",
  "category":"Тренды","type":"ranking","source_type":"trend","body":A7,
  "sources":["https://www.goal.com/en/lists/world-cup-2026-golden-boot-standings-fifa-award/blt29fdba0896b8fd09",
             "https://www.espn.com/soccer/story/_/id/49117037/lionel-messi-erling-haaland-kylian-mbappe-harry-kane-folarin-balogun-world-cup-golden-boot-top-scorer",
             "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/adidas-golden-boot-race-top-scorer",
             "https://www.nbcsports.com/soccer/news/2026-world-cup-top-goalscorers-full-list-latest-on-race-for-the-golden-boot"]},

 {"slug":"top-7-sensations-group-stage-world-cup-2026",
  "title":"Топ-7 сенсаций группового этапа ЧМ-2026: от подвига Кюрасао до гола «краснодарца» Ленини",
  "excerpt":"Кюрасао, Кабо-Верде, Иран и Узбекистан гремят на чемпионате мира – 2026. Собрали топ-7 главных сенсаций группового этапа с акцентом на интерес болельщиков СНГ.",
  "category":"Тренды","type":"ranking","source_type":"trend","body":A8,
  "sources":["https://www.aljazeera.com/sports/2026/6/21/room-the-hero-as-tiny-curacao-earn-first-world-cup-point-against-ecuador",
             "https://www.fifa.com/en/match-centre/match/17/285023/289273/400021487",
             "https://www.skysports.com/football/news/12040/13543106/world-cup-2026-group-k-guide-fixtures-schedule-standings-and-odds-for-portugal-dr-congo-uzbekistan-and-colombia",
             "https://www.aljazeera.com/sports/2026/6/21/japan-tunisia-4-0-fifa-world-cup-2026-ayase-ueda-daichi-kamada-junya-ito"]},
]

# ── sanity: no em-dash, counts ───────────────────────────────────────────────
for a in ARTICLES:
    for f in ("title","excerpt","body"):
        assert "—" not in a[f], f"EM DASH in {a['slug']} {f}"
news = [a for a in ARTICLES if a["source_type"]=="news"]
trend= [a for a in ARTICLES if a["source_type"]=="trend"]
assert len(ARTICLES)==8 and len(news)==5 and len(trend)==3, (len(ARTICLES),len(news),len(trend))
print("Sanity OK: 8 articles, 5 news / 3 trend, no em-dash")

# ── attach covers ────────────────────────────────────────────────────────────
print("\nBuilding covers...")
for a in ARTICLES:
    a["image_base64"] = make_cover_b64(COVER_FILE[a["slug"]])
    a["image_url"] = None

# ── build payload (only DB-relevant fields + image_base64/source_type) ───────
def payload(a):
    return {"title":a["title"],"slug":a["slug"],"body":a["body"],"excerpt":a["excerpt"],
            "category":a["category"],"type":a["type"],"image_url":a["image_url"],
            "sources":a["sources"],"source_type":a["source_type"],"image_base64":a["image_base64"]}

def post(items):
    for attempt in range(5):
        try:
            r = S.post(ENDPOINT, headers={"x-agent-secret":SECRET,"Content-Type":"application/json"},
                       data=json.dumps({"articles":[payload(x) for x in items]}), timeout=180)
            print("HTTP", r.status_code)
            if r.status_code==401:
                raise SystemExit("401 Unauthorized – secret wrong/missing. Stopping.")
            return r.json()
        except requests.RequestException as e:
            wait = 2**(attempt+1)
            print("net error", e, "retry in", wait); time.sleep(wait)
    raise SystemExit("Publish failed after retries")

print("\nPublishing batch of 8...")
res = post(ARTICLES)
results = res.get("results", [])
by_slug = {r.get("slug","").rstrip("-23456789").rstrip("-") if False else r.get("slug"): r for r in results}
print(json.dumps(results, ensure_ascii=False, indent=2))

# map results back by order (endpoint preserves order)
status = {}
for a, r in zip(ARTICLES, results):
    status[a["slug"]] = r

# retry errors
errs = [a for a in ARTICLES if status.get(a["slug"],{}).get("status")=="error"]
if errs:
    print("\nRetrying", len(errs), "errored items...")
    r2 = post(errs).get("results",[])
    for a, r in zip(errs, r2):
        status[a["slug"]] = r
    print(json.dumps(r2, ensure_ascii=False, indent=2))

# ── logging ──────────────────────────────────────────────────────────────────
pathlib.Path("logs").mkdir(exist_ok=True)
hist = pathlib.Path("logs/articles-history.jsonl")
db_slugs=[]
with hist.open("a", encoding="utf-8") as fh:
    for a in ARTICLES:
        r = status.get(a["slug"], {})
        st = r.get("status"); db_slug = r.get("slug", a["slug"])
        db_slugs.append(db_slug)
        if st != "inserted":
            print("WARN not inserted:", a["slug"], r);
        entry = {"timestamp":NOW_ISO,"run_id":RUN_ID,"publish_status":st,
                 "db_id":r.get("id"),"db_slug":db_slug,"source_type":a["source_type"],
                 "type":a["type"],"title":a["title"],"slug":a["slug"],
                 "image_url":None,"has_base64_img":True,"has_youtube":False,
                 "topic":a["excerpt"][:160],"teams":[],"players":[],"sources":a["sources"]}
        fh.write(json.dumps(entry, ensure_ascii=False)+"\n")

pathlib.Path("logs/last-run.json").write_text(json.dumps({
    "run_id":RUN_ID,"generated_at":NOW_ISO,"phase":"wc2026_group_stage",
    "count":len(ARTICLES),
    "news":sum(1 for a in ARTICLES if a["source_type"]=="news"),
    "trend":sum(1 for a in ARTICLES if a["source_type"]=="trend"),
    "slugs":[a["slug"] for a in ARTICLES],"db_slugs":db_slugs,
}, ensure_ascii=False, indent=2), encoding="utf-8")

# ── local archive (markdown) ─────────────────────────────────────────────────
for a in ARTICLES:
    src = "news" if a["source_type"]=="news" else "trend"
    d = pathlib.Path(f"articles/{src}-{a['slug']}"); d.mkdir(parents=True, exist_ok=True)
    (d/f"{src}-{a['slug']}.md").write_text(
        f"# {a['title']}\n\n*{a['excerpt']}*\n\n{a['body']}\n", encoding="utf-8")

ok = sum(1 for a in ARTICLES if status.get(a['slug'],{}).get('status')=='inserted')
print(f"\nDONE. inserted={ok}/8  db_slugs={db_slugs}")
# write manifest for final output
pathlib.Path("logs/manifest-20260622.json").write_text(json.dumps({
    "generated_at":NOW_ISO,"run_id":RUN_ID,
    "articles":[{k:(a[k] if k!='image_base64' else '<base64>') for k in
        ('title','slug','body','excerpt','category','type','image_url','sources','source_type')}
        for a in ARTICLES],
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("manifest written")
