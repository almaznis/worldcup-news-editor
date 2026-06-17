#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, datetime, importlib.util

spec=importlib.util.spec_from_file_location("bp","/home/user/worldcup-news-editor/build_publish_md7.py")
bp=importlib.util.module_from_spec(spec)
# prevent main() execution: module guarded by __name__=="__main__"
spec.loader.exec_module(bp)

ARTS=bp.ARTICLES
RUN_ID=bp.RUN_ID
results=json.load(open("/tmp/results_md7.json"))["results"]

META={
 "argentina-3-0-algeria-messi-hat-trick-world-cup-2026":{"teams":["Аргентина","Алжир"],"players":["Лионель Месси"],"topic":"Аргентина 3:0 Алжир, хет-трик Месси, 16 голов на ЧМ = рекорд Клозе"},
 "england-croatia-world-cup-2026-preview-june-17":{"teams":["Англия","Хорватия"],"players":["Гарри Кейн","Лука Модрич"],"topic":"Превью Англия–Хорватия (17 июня), реванш за ЧМ-2018"},
 "france-3-1-senegal-mbappe-record-world-cup-2026":{"teams":["Франция","Сенегал"],"players":["Килиан Мбаппе"],"topic":"Франция 3:1 Сенегал, Мбаппе лучший бомбардир сборной Франции (58)"},
 "england-livramento-injury-out-world-cup-2026":{"teams":["Англия"],"players":["Тино Ливраменто","Тревор Чалоба"],"topic":"Ливраменто выбыл с ЧМ-2026, травма икры, замена Чалоба"},
 "norway-4-1-iraq-haaland-brace-world-cup-2026":{"teams":["Норвегия","Ирак"],"players":["Эрлинг Холанд"],"topic":"Норвегия 4:1 Ирак, дубль Холанда в дебютном матче на ЧМ"},
 "uzbekistan-colombia-world-cup-2026-debut-preview":{"teams":["Узбекистан","Колумбия"],"players":["Эльдор Шомуродов","Луис Диас"],"topic":"Превью Узбекистан–Колумбия, дебют Узбекистана на ЧМ (тренд СНГ)"},
 "top-7-records-first-week-world-cup-2026":{"teams":[],"players":["Месси","Мбаппе","Холанд"],"topic":"Топ-7 рекордов первой недели ЧМ-2026"},
 "portugal-dr-congo-ronaldo-last-dance-world-cup-2026":{"teams":["Португалия","ДР Конго"],"players":["Криштиану Роналду"],"topic":"Превью Португалия–ДР Конго, шестой ЧМ Роналду (тренд)"},
}

now=datetime.datetime.now(datetime.timezone.utc).isoformat()
logpath="/home/user/worldcup-news-editor/logs/articles-history.jsonl"
lines=[]
for a,r in zip(ARTS,results):
    m=META[a["slug"]]
    entry={
      "timestamp":now,"run_id":RUN_ID,"publish_status":r["status"],
      "db_id":r["id"],"db_slug":r["slug"],"slug_collision":r["slug"]!=a["slug"],
      "source_type":a["source_type"],"type":a["type"],"category":a["category"],
      "title":a["title"],"slug":a["slug"],"topic":m["topic"],
      "teams":m["teams"],"players":m["players"],"sources":a["sources"],
      "cover":bp.COVERS[a["_cover"]],"has_base64_img":True,"has_youtube":False,
    }
    lines.append(json.dumps(entry,ensure_ascii=False))
with open(logpath,"a",encoding="utf-8") as f:
    f.write("\n".join(lines)+"\n")

# last-run.json
last={"run_id":RUN_ID,"generated_at":now,"phase":"wc2026_md7_results_previews",
      "counts":{"total":8,"news":5,"trend":3,"inserted":sum(1 for r in results if r["status"]=="inserted")},
      "slug_collisions":[r["slug"] for a,r in zip(ARTS,results) if r["slug"]!=a["slug"]],
      "db_slugs":[r["slug"] for r in results]}
json.dump(last,open("/home/user/worldcup-news-editor/logs/last-run.json","w"),ensure_ascii=False,indent=2)

# local archive md
for a in ARTS:
    src="news" if a["source_type"]=="news" else "trend"
    d=f"/home/user/worldcup-news-editor/articles/{src}-{a['slug']}"
    os.makedirs(d,exist_ok=True)
    md=f"# {a['title']}\n\n*{a['excerpt']}*\n\n*Категория: {a['category']} | Тип: {a['type']} | Обложка: {bp.COVERS[a['_cover']]}*\n\n{a['body']}\n"
    open(f"{d}/{src}-{a['slug']}.md","w",encoding="utf-8").write(md)

print("logged",len(lines),"entries; collisions:",last["slug_collisions"])
