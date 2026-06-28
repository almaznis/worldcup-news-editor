# -*- coding: utf-8 -*-
"""Append history log, write last-run.json, and local archive for the run."""
import json, os
from run_20260628 import articles, RUN_ID, GENERATED_AT

results = json.load(open("publish_results.json"))

# per-article dedup metadata (teams / players / topic)
META = {
 "spain-1-0-uruguay-baena-world-cup-2026-group-h":
   {"topic":"Испания обыграла Уругвай 1:0 (гол Баэны после ошибки Муслеры) и выиграла группу H; Уругвай вылетел.",
    "teams":["Испания","Уругвай"],"players":["Алекс Баэна","Фернандо Муслера","Марсело Бьелса"]},
 "van-hecke-tottenham-brighton-transfer-june-2026":
   {"topic":"Трансфер: Тоттенхэм подписал защитника сборной Нидерландов Яна Пауля ван Хекке из Брайтона за ~52 млн фунтов.",
    "teams":["Тоттенхэм","Брайтон","Нидерланды"],"players":["Ян Пауль ван Хекке"]},
 "argentina-3-1-jordan-messi-world-cup-2026-group-j":
   {"topic":"Аргентина обыграла Иорданию 3:1 (Ло Сельсо, Л.Мартинес, Месси), 9 очков, 1-е место в группе J.",
    "teams":["Аргентина","Иордания"],"players":["Лионель Месси","Джовани Ло Сельсо","Лаутаро Мартинес","Муса Аль-Тамари"]},
 "world-cup-2026-round-of-32-knockouts-begin-june-28":
   {"topic":"Превью: старт плей-офф (1/16 финала) ЧМ-2026 28 июня, матч открытия ЮАР – Канада, расписание раунда.",
    "teams":["ЮАР","Канада"],"players":[]},
 "england-2-0-panama-kane-record-world-cup-2026-group-l":
   {"topic":"Англия обыграла Панаму 2:0 (Беллингем + Кейн); Кейн 11-м голом установил рекорд сборной на ЧМ. 1-е место в группе L.",
    "teams":["Англия","Панама"],"players":["Джуд Беллингем","Гарри Кейн"]},
 "top-7-title-favourites-world-cup-2026-knockouts":
   {"topic":"Рейтинг (тренд): топ-7 претендентов на титул ЧМ-2026 перед плей-офф после завершения группового этапа.",
    "teams":["Испания","Аргентина","Франция","Англия","Бразилия","Германия","Португалия"],"players":[]},
 "dr-congo-3-1-uzbekistan-world-cup-2026-debut-ends":
   {"topic":"ДР Конго обыграла Узбекистан 3:1 (камбэк, дубль Виссы); Узбекистан завершил дебютный ЧМ без очков. Тренд КЗ/СНГ.",
    "teams":["ДР Конго","Узбекистан"],"players":["Эльдор Шомуродов","Йоан Висса","Фистон Майеле"]},
 "portugal-vs-croatia-round-of-32-preview-world-cup-2026":
   {"topic":"Превью (тренд): Португалия – Хорватия в 1/16 финала ЧМ-2026 (2 июля, Торонто), дуэль Роналду и Модрича.",
    "teams":["Португалия","Хорватия"],"players":["Криштиану Роналду","Лука Модрич"]},
}

hist_path="logs/articles-history.jsonl"
os.makedirs("logs",exist_ok=True)
returned_slugs=[]
with open(hist_path,"a",encoding="utf-8") as f:
    for art in articles:
        base=art["slug"]
        res=results.get(base) or next((v for k,v in results.items() if k.startswith(base)),{})
        ret=res.get("slug",base)
        returned_slugs.append(ret)
        dup = ret!=base  # suffix appended => base already existed (partial-insert duplicate)
        m=META[base]
        entry={
          "timestamp":GENERATED_AT,"run_id":RUN_ID,"source_type":art["source_type"],
          "type":art["type"],"title":art["title"],"slug":base,"returned_slug":ret,
          "topic":m["topic"],"teams":m["teams"],"players":m["players"],
          "sources":art["sources"],
          "publish_status":res.get("status","unknown"),"db_id":res.get("id"),
          "duplicate_of_base_slug": dup,
        }
        f.write(json.dumps(entry,ensure_ascii=False)+"\n")

last={
 "run_id":RUN_ID,"generated_at":GENERATED_AT,"phase":"r32_knockouts_news_trends",
 "count":len(articles),
 "news":sum(1 for a in articles if a["source_type"]=="news"),
 "trend":sum(1 for a in articles if a["source_type"]=="trend"),
 "returned_slugs":returned_slugs,
 "incident":{
   "type":"partial_batch_insert_duplicates",
   "detail":"First batch POST returned HTTP 546 WORKER_RESOURCE_LIMIT after inserting the first 6 articles. The one-by-one retry then re-inserted those 6, which the endpoint stored with a -2 suffix (duplicates). 2 articles (dr-congo, portugal) inserted once and are clean.",
   "duplicated_stories":[s for s in returned_slugs if s.endswith("-2")],
   "manual_cleanup_needed":"Delete one copy of each of the 6 duplicated stories from public.articles (e.g. remove the 6 '-2' rows, or the 6 base-slug rows). No delete endpoint is available to the agent.",
   "prevention":"Publish one article per request (publish_run.py), never batch, to avoid partial-insert duplicates.",
 },
}
json.dump(last,open("logs/last-run.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)

# local archive
for art in articles:
    src = "news" if art["source_type"]=="news" else "trend"
    folder=f"articles/{src}-{art['slug']}"
    os.makedirs(folder,exist_ok=True)
    fp=f"{folder}/{src}-{art['slug']}.md"
    with open(fp,"w",encoding="utf-8") as f:
        f.write(f"# {art['title']}\n\n")
        f.write(f"> {art['excerpt']}\n\n")
        f.write(f"- type: {art['type']}\n- category: {art['category']}\n- image: {art['image_url']}\n")
        f.write(f"- sources: {', '.join(art['sources'])}\n\n---\n\n")
        f.write(art["body"]+"\n")

print("history appended, last-run.json + archive written")
print("returned slugs:", returned_slugs)
PY=""
