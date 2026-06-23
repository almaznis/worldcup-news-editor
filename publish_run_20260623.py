#!/usr/bin/env python3
"""Build, optimize images, publish 8 WC2026 articles to Sport Arena Hub, then log."""
import os, io, sys, json, base64, time, datetime, re
import requests
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
RUN_ID = "run-20260623-b79e2947"
UA = {"User-Agent": "WorldCupNewsAgent/1.0 (editorial use; contact almaznis1@gmail.com)"}

ARTICLES = [
 dict(folder="news-argentina-austria-messi-world-cup-record-2026",
   title="Аргентина – Австрия 2:0: Месси стал лучшим бомбардиром в истории чемпионатов мира",
   slug="argentina-austria-messi-world-cup-record-2026",
   excerpt="Лионель Месси оформил дубль в Арлингтоне, довёл число своих голов на чемпионатах мира до 18 и побил рекорд Мирослава Клозе. Аргентина обыграла Австрию 2:0 и вышла в плей-офф ЧМ-2026.",
   category="Отчёты о матчах", type="match_report", source_type="news",
   teams=["Аргентина","Австрия"], players=["Лионель Месси","Тиаго Алмада"],
   topic="Аргентина обыграла Австрию 2:0, Месси дублем побил рекорд Клозе и стал лучшим бомбардиром в истории ЧМ (18 голов).",
   img="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/FWC_2018_-_Group_D_-_ARG_v_ISL_-_Messi_penalty_kick.jpg/1920px-FWC_2018_-_Group_D_-_ARG_v_ISL_-_Messi_penalty_kick.jpg",
   sources=["https://www.espn.com/soccer/story/_/id/49144198/argentina-austria-live-world-cup-2026-latest-updates-commentary-score-result",
            "https://www.cbssports.com/soccer/news/argentina-austria-live-updates-world-cup-2026-score-result/live/",
            "https://www.nbcnews.com/sports/soccer/lionel-messi-breaks-record-career-goals-scored-world-cup-rcna351168",
            "https://www.fifa.com/en/match-centre/match/17/285023/289273/400021494"]),
 dict(folder="news-raphinha-hamstring-injury-brazil-world-cup-2026",
   title="Рафинья травмировал бедро: Бразилия надеется вернуть форварда к плей-офф ЧМ-2026",
   slug="raphinha-hamstring-injury-brazil-world-cup-2026",
   excerpt="У Рафиньи диагностировано повреждение задней поверхности бедра. Бразильская конфедерация футбола не списала форварда с турнира, но сроки возвращения остаются под вопросом.",
   category="Новости игроков", type="transfer", source_type="news",
   teams=["Бразилия"], players=["Рафинья"],
   topic="CBF подтвердила травму задней поверхности бедра у Рафиньи; ориентир возвращения – 1/8 финала ЧМ-2026.",
   img="https://upload.wikimedia.org/wikipedia/commons/0/0d/Brazil_vs_Serbia_WC2022_Raphinha_and_Pavlovic.jpg",
   sources=["https://www.espn.com/soccer/story/_/id/49129032/brazil-confirm-raphinha-hamstring-injury-world-cup-2026-return-uncertain-group-c",
            "https://www.si.com/soccer/raphinha-injury-uncertainty-distress-over-brazilian-star-world-cup-status",
            "https://www.washingtonpost.com/sports/soccer/2026/06/20/raphinha-injury-brazil-world-cup/e859f4bc-6ce8-11f1-830e-133d20cadd28_story.html",
            "https://heavy.com/sports/soccer/world-cup/raphinha-injury-update-brazil-knockout-hopes/"]),
 dict(folder="news-mbappe-100-caps-france-iraq-storm-world-cup-2026",
   title="Мбаппе забил в 100-м матче за Францию, но игру с Ираком прервала гроза в Филадельфии",
   slug="mbappe-100-caps-france-iraq-storm-world-cup-2026",
   excerpt="Килиан Мбаппе отметил юбилейный, сотый матч за сборную Франции голом в ворота Ирака. Встречу группы I прервала гроза – это первый матч ЧМ-2026, остановленный из-за погоды.",
   category="ЧМ-2026", type="transfer", source_type="news",
   teams=["Франция","Ирак"], players=["Килиан Мбаппе"],
   topic="Мбаппе провёл 100-й матч за Францию и забил Ираку; игра прервана грозой – первый погодный перерыв ЧМ-2026.",
   img="https://upload.wikimedia.org/wikipedia/commons/b/b8/France_WC2018_final.jpg",
   sources=["https://www.cbssports.com/soccer/news/france-vs-iraq-weather-delay-world-cup-2026/",
            "https://www.espn.com/soccer/story/_/id/49141065/world-cup-daily-crying-belgium-fan-saved-var-messi-mbappe-haaland-action",
            "https://www.outlookindia.com/sports/football/france-vs-iraq-live-score-fifa-world-cup-2026-group-i-fra-v-irq-updates-philadelphia-stadium-highlights",
            "https://www.nbcnews.com/sports/soccer/live-blog/fifa-world-cup-games-2026-june-22-live-updates-rcna351129"]),
 dict(folder="news-england-ghana-preview-kane-record-world-cup-2026",
   title="Англия – Гана (23 июня): Кейн в одном голе от рекорда Линекера",
   slug="england-ghana-preview-kane-record-world-cup-2026",
   excerpt="В матче группы L Англия сыграет с Ганой. Гарри Кейну достаточно одного гола, чтобы обойти Гари Линекера и стать лучшим бомбардиром сборной Англии в истории чемпионатов мира.",
   category="Сборные", type="preview", source_type="news",
   teams=["Англия","Гана"], players=["Гарри Кейн","Джуд Беллингем","Антуан Семеньо"],
   topic="Превью Англия – Гана (группа L, 23 июня): Кейн в погоне за рекордом Линекера, обе команды по 3 очка.",
   img="https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/The_Prime_Minister_speaks_to_Harry_Kane_%2852770172531%29.jpg/1920px-The_Prime_Minister_speaks_to_Harry_Kane_%2852770172531%29.jpg",
   sources=["https://theanalyst.com/articles/england-vs-ghana-prediction-world-cup-2026-match-preview",
            "https://www.englandfootball.com/england/mens-senior-team/fixtures-results/2025-26/World-Cup/england-v-ghana-fifa-world-cup-tuesday-23-june-2026-match-centre",
            "https://www.sportsmole.co.uk/football/england/world-cup-2026/preview/england-vs-ghana-prediction-team-news-lineups_599721.html"]),
 dict(folder="news-jordan-algeria-preview-world-cup-2026",
   title="Иордания – Алжир: матч на выживание в группе J ЧМ-2026",
   slug="jordan-algeria-preview-world-cup-2026",
   excerpt="После поражений в стартовом туре Иордания и Алжир проведут очный матч группы J, в котором проигравший почти наверняка лишится шансов на плей-офф чемпионата мира.",
   category="Сборные", type="preview", source_type="news",
   teams=["Иордания","Алжир"], players=[],
   topic="Превью Иордания – Алжир (группа J, 23 июня): матч на выживание, обе команды без очков после первого тура.",
   img="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Alg%C3%A9rie_-_Arm%C3%A9nie_-_20140531_-_14.jpg/1920px-Alg%C3%A9rie_-_Arm%C3%A9nie_-_20140531_-_14.jpg",
   sources=["https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/jordan-algeria-feature",
            "https://www.espn.com/soccer/story/_/id/49124571/jordan-vs-algeria-fifa-world-cup-2026-tv-channel-how-watch-kick-live-stream-injury-predicted-line-ups",
            "https://www.goal.com/en/news/jordan-algeria-world-cup-preview/bltddae6909cf8922c4"]),
 dict(folder="trend-portugal-uzbekistan-preview-world-cup-2026",
   title="Португалия – Узбекистан: дебютант Центральной Азии бросает вызов фавориту на ЧМ-2026",
   slug="portugal-uzbekistan-preview-world-cup-2026",
   excerpt="23 июня в Хьюстоне сборная Узбекистана, первый дебютант ЧМ из Центральной Азии, сыграет с Португалией. Для болельщиков СНГ это один из самых ожидаемых матчей турнира.",
   category="Сборные", type="preview", source_type="trend",
   teams=["Португалия","Узбекистан"], players=["Бруну Фернандеш","Криштиану Роналду","Достонбек Хамдамов"],
   topic="Превью Португалия – Узбекистан (группа K, 23 июня): дебют Узбекистана против фаворита, интерес болельщиков СНГ.",
   img="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Bruno_Fernandes_USMNT_v_Portugal_Mar_31_2026-127.jpg/1920px-Bruno_Fernandes_USMNT_v_Portugal_Mar_31_2026-127.jpg",
   sources=["https://theanalyst.com/articles/portugal-vs-uzbekistan-prediction-world-cup-2026-match-preview",
            "https://www.skysports.com/football/news/12040/13543106/world-cup-2026-group-k-guide-fixtures-schedule-standings-and-odds-for-portugal-dr-congo-uzbekistan-and-colombia",
            "https://sports.yahoo.com/articles/portugal-vs-uzbekistan-picks-predictions-090406819.html",
            "https://www.goal.com/en/news/portugal-uzbekistan-world-cup-preview/bltf65b8be15166aad7"]),
 dict(folder="trend-top-7-world-cup-2026-group-stage-stories",
   title="Топ-7 историй и сенсаций группового этапа ЧМ-2026",
   slug="top-7-world-cup-2026-group-stage-stories",
   excerpt="Кюрасао и Кабо-Верде творят историю, Иран сдержал Бельгию, а Норвегия вернулась спустя 28 лет. Собрали семь главных историй стартового отрезка чемпионата мира 2026 года.",
   category="Тренды", type="ranking", source_type="trend",
   teams=["Кюрасао","Иран","Бельгия","Норвегия","Узбекистан","Кабо-Верде","Иордания"], players=["Эрлинг Холанд","Элой Рум"],
   topic="Рейтинг семи главных историй и сенсаций группового этапа ЧМ-2026: дебютанты, Иран, возвращение Норвегии.",
   img="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Met_Life_Stadium.jpg/1920px-Met_Life_Stadium.jpg",
   sources=["https://www.espn.com/soccer/story/_/id/49132616/world-cup-2026-today-blog-21-06-2026-live-updates-news-fixtures-schedule-results-curacao-make-history-germany-ivory-coast",
            "https://www.aljazeera.com/sports/2026/6/21/iran-belgium-wc-mehdi-taremi-score-los-angeles-draw",
            "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/debutants-cabo-verde-curacao-jordan-uzbekistan",
            "https://www.espn.com/soccer/story/_/id/48322228/meet-2026-world-cup-debutants-cape-verde-curacao-jordan-uzbekistan"]),
 dict(folder="trend-top-7-all-time-world-cup-goalscorers-messi",
   title="Топ-7 бомбардиров в истории чемпионатов мира: Месси возглавил вечный список",
   slug="top-7-all-time-world-cup-goalscorers-messi",
   excerpt="Лионель Месси с 18 голами стал лучшим бомбардиром в истории чемпионатов мира. Вспоминаем семёрку лучших снайперов мундиалей – от Месси и Клозе до Пеле.",
   category="Тренды", type="ranking", source_type="trend",
   teams=[], players=["Лионель Месси","Мирослав Клозе","Роналдо","Килиан Мбаппе","Герд Мюллер","Жюст Фонтен","Пеле"],
   topic="Рейтинг семи лучших бомбардиров в истории ЧМ после рекорда Месси (18 голов).",
   img="https://upload.wikimedia.org/wikipedia/commons/c/c8/Lionel_Messi_WC2022.jpg",
   sources=["https://sports.yahoo.com/articles/most-goals-in-world-cup-history-where-messi-mbappe-rank-among-fifas-top-scorers-all-time-214600114.html",
            "https://www.foxsports.com/stories/soccer/most-world-cup-goals-all-time-messi-mbappe",
            "https://www.olympics.com/en/news/fifa-world-cup-messi-mbappe-goal-record-klose-football",
            "https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_top_goalscorers"]),
]

def make_cover_b64(url):
    r = requests.get(url, headers=UA, timeout=60); r.raise_for_status()
    src = Image.open(io.BytesIO(r.content)).convert("RGB")
    W, H = 1600, 900
    # blurred cover background
    sc = max(W/src.width, H/src.height)
    bg = src.resize((max(1,int(src.width*sc)), max(1,int(src.height*sc))), Image.LANCZOS)
    left = (bg.width - W)//2; top = (bg.height - H)//2
    bg = bg.crop((left, top, left+W, top+H)).filter(ImageFilter.GaussianBlur(28))
    dark = Image.new("RGB", (W, H), (0,0,0)); bg = Image.blend(bg, dark, 0.25)
    # contained foreground
    fs = min(W/src.width, H/src.height)
    fw, fh = max(1,int(src.width*fs)), max(1,int(src.height*fs))
    fg = src.resize((fw, fh), Image.LANCZOS)
    bg.paste(fg, ((W-fw)//2, (H-fh)//2))
    for q in (84, 78, 72, 66, 60):
        buf = io.BytesIO(); bg.save(buf, "JPEG", quality=q, optimize=True)
        data = buf.getvalue()
        if len(data) <= 300_000:
            break
    return base64.b64encode(data).decode(), len(data)

def load_body(folder):
    p = os.path.join(ROOT, "articles", folder, folder + ".md")
    lines = open(p, encoding="utf-8").read().splitlines()
    kept = [ln for ln in lines if "IMAGE_URL" not in ln]
    body = "\n".join(kept)
    body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"
    open(p, "w", encoding="utf-8").write(body)  # clean archive too
    return body

def build_payload():
    arts = []
    for i, a in enumerate(ARTICLES):
        body = load_body(a["folder"])
        b64, sz = make_cover_b64(a["img"])
        print(f"  img {a['slug']}: {sz//1024} KB")
        arts.append(dict(title=a["title"], slug=a["slug"], body=body, excerpt=a["excerpt"],
                         category=a["category"], type=a["type"], image_url=None,
                         image_base64=b64, sources=a["sources"], source_type=a["source_type"]))
        if i < len(ARTICLES)-1:
            time.sleep(3.5)  # wikimedia rate limit
    return arts

def main():
    secret = os.environ.get("AGENT_PUBLISH_SECRET")
    if not secret:
        print("FATAL: AGENT_PUBLISH_SECRET missing"); sys.exit(2)
    print("Building payload + optimizing images...")
    arts = build_payload()
    payload = {"articles": arts}
    headers = {"Content-Type": "application/json", "x-agent-secret": secret}
    print("POSTing", len(arts), "articles...")
    resp = requests.post(ENDPOINT, headers=headers, data=json.dumps(payload), timeout=180)
    print("HTTP", resp.status_code)
    out = resp.json()
    results = out.get("results", [])
    by_slug = {r.get("slug"): r for r in results}
    # retry errors once
    errs = [a for a in arts if by_slug.get(a["slug"], {}).get("status") == "error"]
    if errs:
        print("Retrying", len(errs), "errored items...")
        time.sleep(3)
        r2 = requests.post(ENDPOINT, headers=headers, data=json.dumps({"articles": errs}), timeout=180)
        for r in r2.json().get("results", []):
            by_slug[r.get("slug")] = r
    # log
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    histp = os.path.join(ROOT, "logs", "articles-history.jsonl")
    inserted = []
    with open(histp, "a", encoding="utf-8") as fh:
        for a in ARTICLES:
            res = by_slug.get(a["slug"], {})
            status = res.get("status", "unknown")
            entry = dict(timestamp=now, run_id=RUN_ID, publish_status=status,
                         db_id=res.get("id"), db_slug=res.get("slug"),
                         source_type=a["source_type"], type=a["type"], title=a["title"],
                         slug=a["slug"], topic=a["topic"], teams=a["teams"],
                         players=a["players"], sources=a["sources"],
                         image_via="base64")
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            if status == "inserted":
                inserted.append(res.get("slug"))
            print(f"  {a['slug']}: {status} (db_slug={res.get('slug')}, err={res.get('error')})")
    lastp = os.path.join(ROOT, "logs", "last-run.json")
    json.dump(dict(run_id=RUN_ID, generated_at=now, count=len(ARTICLES),
                   inserted=len(inserted), slugs=[a["slug"] for a in ARTICLES],
                   db_slugs=[by_slug.get(a["slug"],{}).get("slug") for a in ARTICLES]),
              open(lastp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"DONE. inserted={len(inserted)}/{len(ARTICLES)}")
    # write manifest for final output
    manifest = dict(generated_at=now, run_id=RUN_ID,
        articles=[dict(title=a["title"], slug=a["slug"], excerpt=a["excerpt"],
                       category=a["category"], type=a["type"],
                       image_url=by_slug.get(a["slug"],{}).get("image_url") or by_slug.get(a["slug"],{}).get("imageUrl"),
                       sources=a["sources"], source_type=a["source_type"],
                       db_slug=by_slug.get(a["slug"],{}).get("slug"),
                       status=by_slug.get(a["slug"],{}).get("status")) for a in ARTICLES])
    json.dump(manifest, open(os.path.join(ROOT, "logs", "run-manifest-20260623.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(out, open(os.path.join(ROOT, "logs", "raw-response-20260623.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
