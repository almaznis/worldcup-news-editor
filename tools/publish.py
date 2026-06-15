#!/usr/bin/env python3
"""Assemble the 8 articles, POST to the Sport Arena Hub endpoint, then log."""
import os, sys, json, time, datetime, urllib.request

ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
ROOT = "/home/user/worldcup-news-editor"
RUN_ID = "run-20260615-wc2026-grpstage"

# (slug, dir, body_file, cover_b64, title, excerpt, category, type, source_type, sources, topic, teams, players)
A = [
 ("brazil-1-1-morocco-wc2026-group-c",
  "news-brazil-1-1-morocco-wc2026-group-c", "brazil-morocco",
  "Бразилия – Марокко – 1:1: Винисиус спас «селесао» в стартовом матче ЧМ-2026",
  "Бразилия и Марокко открыли группу C на ЧМ-2026 результативной ничьей 1:1. «Селесао» от поражения спас гол Винисиуса Жуниора на «Метлайф Стэдиум».",
  "Отчёты о матчах", "match_report", "news",
  ["https://www.championat.com/football/article-6505646-braziliya-marokko-1-1-obzor-matcha-1-go-tura-chm-po-futbolu-2026-goly-sajbari-vinisius-zhunior-statistika-14-iyunya-2026-goda.html",
   "https://www.championat.com/football/_worldcup/tournament/6858/match/1310410/",
   "https://www.amny.com/news/brazil-morocco-world-cup/"],
  "Бразилия 1:1 Марокко, 1-й тур группы C ЧМ-2026 (14 июня): голы Сайбари и Винисиуса",
  ["Бразилия","Марокко"], ["Винисиус Жуниор","Исмаэль Сайбари"]),

 ("endo-japan-world-cup-2026-retirement-injury",
  "news-endo-japan-world-cup-2026-retirement-injury", "endo",
  "Капитан Японии Ватару Эндо пропустит ЧМ-2026 и завершил карьеру в сборной",
  "33-летний капитан сборной Японии и полузащитник «Ливерпуля» Ватару Эндо из-за травмы пропустит чемпионат мира 2026 и объявил о завершении выступлений за национальную команду.",
  "Новости игроков", "transfer", "news",
  ["https://www.espn.com/soccer/story/_/id/49032127/japan-captain-wataru-endo-world-cup-injury-announces-retirement",
   "https://cryptobriefing.com/wataru-endo-world-cup-injury-replacement/"],
  "Ватару Эндо (Япония) выбыл из заявки на ЧМ-2026 из-за травмы и завершил карьеру в сборной; замена – Сюто Матино",
  ["Япония"], ["Ватару Эндо","Сюто Матино"]),

 ("germany-7-1-curacao-wc2026-group-e",
  "news-germany-7-1-curacao-wc2026-group-e", "germany",
  "Германия – Кюрасао – 7:1: дубль Хаверца и разгром в первом туре ЧМ-2026",
  "Германия устроила самый крупный разгром стартового тура ЧМ-2026, обыграв дебютанта Кюрасао со счётом 7:1. Кай Хаверц оформил дубль.",
  "Отчёты о матчах", "match_report", "news",
  ["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_E"],
  "Германия 7:1 Кюрасао, 1-й тур группы E ЧМ-2026 (14 июня): дубль Хаверца",
  ["Германия","Кюрасао"], ["Кай Хаверц","Джамал Мусиала","Феликс Нмеча"]),

 ("argentina-algeria-wc2026-preview-messi",
  "news-argentina-algeria-wc2026-preview-messi", "argentina",
  "Аргентина – Алжир: Месси начинает защиту титула на ЧМ-2026",
  "В ночь на 17 июня по Москве Аргентина начнёт защиту титула матчем против Алжира. Для Лионеля Месси этот чемпионат мира почти наверняка станет последним.",
  "ЧМ-2026", "preview", "news",
  ["https://www.sportsmole.co.uk/football/argentina/world-cup/feature/argentina-2026-world-cup-preview-squad-fixtures-and-prediction_599002.html",
   "https://theanalyst.com/articles/argentina-vs-algeria-prediction-world-cup-2026-match-preview"],
  "Превью Аргентина – Алжир, 1-й тур группы J ЧМ-2026 (16 июня), старт Месси",
  ["Аргентина","Алжир"], ["Лионель Месси","Лаутаро Мартинес"]),

 ("sweden-5-1-tunisia-wc2026-group-f",
  "news-sweden-5-1-tunisia-wc2026-group-f", "sweden-tunisia",
  "Швеция – Тунис – 5:1: дубль Аяри и яркий старт скандинавов на ЧМ-2026",
  "Сборная Швеции разгромила Тунис со счётом 5:1 в первом туре группы F. Полузащитник Ясин Аяри оформил дубль дальними ударами.",
  "Отчёты о матчах", "match_report", "news",
  ["https://www.championat.com/football/article-6506946-shveciya-tunis-5-1-obzor-matcha-1-go-tura-chm-po-futbolu-2026-goly-isak-dyokeresh-yairi-15-iyunya-2026.html",
   "https://www.espn.com/soccer/match/_/gameId/760424/tunisia-sweden"],
  "Швеция 5:1 Тунис, 1-й тур группы F ЧМ-2026 (14 июня): дубль Аяри, гол Исака",
  ["Швеция","Тунис"], ["Ясин Аяри","Александр Исак","Виктор Гёкереш"]),

 ("uzbekistan-colombia-wc2026-debut-preview",
  "trend-uzbekistan-colombia-wc2026-debut-preview", "uzbekistan",
  "Узбекистан – Колумбия: исторический дебют на чемпионате мира 2026",
  "В ночь на 18 июня по Москве сборная Узбекистана впервые в истории сыграет на чемпионате мира. Первый соперник в группе K – Колумбия.",
  "Сборные", "preview", "trend",
  ["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_K",
   "https://www.championat.com/football/article-6498674-gruppa-k-na-chm-po-futbolu-2026-portugaliya-dr-kongo-uzbekistan-kolumbiya-razbor-sostavy-trenery-glavnye-zvyozdy-prognoz.html"],
  "Превью Узбекистан – Колумбия, дебют Узбекистана на ЧМ-2026, группа K (17/18 июня)",
  ["Узбекистан","Колумбия"], ["Абдукодир Хусанов","Эльдор Шомуродов","Хамес Родригес"]),

 ("top-7-opening-round-results-wc2026",
  "trend-top-7-opening-round-results-wc2026", "ranking",
  "Топ-7 самых ярких результатов стартового тура ЧМ-2026",
  "Сенсация от Австралии, голы на последних минутах и волевые камбэки: собрали топ-7 самых ярких результатов стартовых дней чемпионата мира 2026.",
  "Тренды", "ranking", "trend",
  ["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_E",
   "https://sports.yahoo.com/soccer/live/2026-world-cup-scores-results-usmnt-throttles-paraguay-canada-earns-draw-with-bosnia-and-herzegovina-145258177.html",
   "https://www.championat.com/football/news-6503408-rezultaty-matchej-chm-po-futbolu-2026-na-11-iyunya-2026.html"],
  "Топ-7 ярких результатов стартового тура ЧМ-2026 (11–14 июня)",
  ["Австралия","Турция","США","Парагвай","Кот-д'Ивуар","Эквадор","Южная Корея","Чехия","Нидерланды","Япония","Мексика","ЮАР","Швейцария","Катар"],
  ["Амад Диалло"]),

 ("belgium-egypt-wc2026-preview-salah",
  "trend-belgium-egypt-wc2026-preview-salah", "belgium-egypt",
  "Бельгия – Египет: Салах против «золотого поколения» в группе G ЧМ-2026",
  "Сегодня вечером Бельгия и Египет откроют группу G на ЧМ-2026. Главная интрига для болельщиков СНГ – игра Мохамеда Салаха.",
  "ЧМ-2026", "preview", "trend",
  ["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_G",
   "https://www.espn.com/soccer/match/_/gameId/760426/egypt-belgium"],
  "Превью Бельгия – Египет, 1-й тур группы G ЧМ-2026 (15 июня), фокус на Салахе",
  ["Бельгия","Египет"], ["Мохамед Салах","Кевин Де Брёйне","Ромелу Лукаку"]),
]

def build_articles():
    arts = []
    for slug, d, cov, title, excerpt, cat, typ, st, sources, topic, teams, players in A:
        body = open(f"{ROOT}/articles/{d}/{d}.md", encoding="utf-8").read().strip()
        b64 = open(f"{ROOT}/covers/{cov}.b64").read().strip()
        arts.append(dict(title=title, slug=slug, body=body, excerpt=excerpt,
                         category=cat, type=typ, image_url=None, image_base64=b64,
                         sources=sources, source_type=st,
                         _topic=topic, _teams=teams, _players=players))
    return arts

def _post_batch(arts, secret):
    payload = {"articles": [{k: v for k, v in a.items() if not k.startswith("_")} for a in arts]}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=data, method="POST",
        headers={"Content-Type": "application/json", "x-agent-secret": secret})
    last = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.getcode(), json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code in (500, 502, 503, 504, 429):  # transient -> retry
                last = "HTTP %s: %s" % (e.code, body[:200])
                if e.code == 401:
                    return e.code, {"_http_error": body}
                time.sleep(min(2 ** (attempt + 1), 30)); continue
            return e.code, {"_http_error": body}
        except Exception as e:
            last = e; time.sleep(min(2 ** (attempt + 1), 30))
    return 0, {"_http_error": "retries exhausted: %s" % last}

def post(arts):
    """Post one article per request (smaller payloads survive the function timeout)."""
    secret = os.environ.get("AGENT_PUBLISH_SECRET")
    if not secret:
        print("FATAL: AGENT_PUBLISH_SECRET missing"); sys.exit(3)
    all_results = []
    for a in arts:
        code, resp = _post_batch([a], secret)
        rs = resp.get("results", []) if isinstance(resp, dict) else []
        if rs:
            all_results.extend(rs)
            print("  ->", a["slug"], code, rs[0].get("status"), rs[0].get("error") or "")
        else:
            all_results.append({"slug": a["slug"], "status": "error",
                                "error": "HTTP %s %s" % (code, str(resp)[:200])})
            print("  ->", a["slug"], code, "ERROR", str(resp)[:160])
        time.sleep(1)
    return 200, {"results": all_results}

if __name__ == "__main__":
    arts = build_articles()
    total = sum(len(json.dumps({k:v for k,v in a.items() if not k.startswith('_')})) for a in arts)
    print(f"Built {len(arts)} articles; payload ~{total//1024} KB")
    for a in arts:
        print(f"  {a['source_type']:5} {a['type']:12} {a['slug']}  (body {len(a['body'])} ch, b64 {len(a['image_base64'])//1024}KB)")
    code, resp = post(arts)
    print("HTTP", code)
    print(json.dumps(resp, ensure_ascii=False)[:2000])
    json.dump(resp, open(f"{ROOT}/build/publish-response.json", "w"), ensure_ascii=False, indent=2)
    # logging on success
    results = resp.get("results", []) if isinstance(resp, dict) else []
    by_slug = {r.get("slug"): r for r in results}
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    inserted = []
    with open(f"{ROOT}/logs/articles-history.jsonl", "a", encoding="utf-8") as log:
        for a in arts:
            r = by_slug.get(a["slug"])
            # match by returned slug possibly suffixed
            if not r:
                for rs, rv in by_slug.items():
                    if rs and rs.startswith(a["slug"]):
                        r = rv; break
            if r and r.get("status") == "inserted":
                entry = dict(timestamp=now, run_id=RUN_ID, source_type=a["source_type"],
                             type=a["type"], title=a["title"], slug=r.get("slug", a["slug"]),
                             topic=a["_topic"], teams=a["_teams"], players=a["_players"],
                             sources=a["sources"])
                log.write(json.dumps(entry, ensure_ascii=False) + "\n")
                inserted.append(r.get("slug", a["slug"]))
    last_run = dict(run_id=RUN_ID, generated_at=now, count=len(inserted),
                    inserted=inserted,
                    errors=[r.get("slug") for r in results if r.get("status") != "inserted"])
    json.dump(last_run, open(f"{ROOT}/logs/last-run.json", "w"), ensure_ascii=False, indent=2)
    print("INSERTED:", len(inserted), inserted)
