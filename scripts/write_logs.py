#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, datetime, os

BASE="/home/user/worldcup-news-editor"
man=json.load(open(f"{BASE}/logs/run-manifest.json"))
resp=json.load(open(f"{BASE}/logs/publish-response.json"))
id_by_slug={r["slug"]:r["id"] for r in resp["results"]}
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
RUN=man["run_id"]

META={
 "germany-7-1-curacao-world-cup-2026-group-e":{"topic":"Германия 7:1 Кюрасао, группа E, рекорд бомбардиров ЧМ","teams":["Германия","Кюрасао"],"players":["Кай Хаверц","Джамал Мусиала","Ливано Коменсия"]},
 "spain-cape-verde-preview-world-cup-2026-group-h":{"topic":"Превью Испания – Кабо-Верде, группа H","teams":["Испания","Кабо-Верде"],"players":["Ламине Ямаль","Педри","Гарри Родригеш"]},
 "netherlands-2-2-japan-world-cup-2026-group-f":{"topic":"Нидерланды 2:2 Япония, группа F, поздняя ничья","teams":["Нидерланды","Япония"],"players":["Вирджил ван Дейк","Дайти Камада","Крисенсио Саммервилл"]},
 "belgium-egypt-preview-world-cup-2026-group-g":{"topic":"Превью Бельгия – Египет, группа G, Салах","teams":["Бельгия","Египет"],"players":["Мохамед Салах","Кевин де Брёйне","Омар Мармуш"]},
 "australia-2-0-turkiye-world-cup-2026-group-d":{"topic":"Австралия 2:0 Турция, группа D","teams":["Австралия","Турция"],"players":["Нестори Иранкунда","Коннор Меткалф","Патрик Бич"]},
 "uzbekistan-colombia-preview-world-cup-2026-group-k":{"topic":"Превью Узбекистан – Колумбия, дебют Узбекистана на ЧМ, группа K","teams":["Узбекистан","Колумбия"],"players":["Абдукодир Хусанов","Эльдор Шомуродов"]},
 "top-7-sobytiy-startovoy-nedeli-chm-2026":{"topic":"Рейтинг: топ-7 событий стартовой недели ЧМ-2026 (рекап)","teams":["Германия","Кюрасао","США","Парагвай","Нидерланды","Япония","Австралия","Турция"],"players":["Кай Хаверц","Фоларин Балогун","Дайти Камада","Нестори Иранкунда"]},
 "portugal-dr-congo-preview-ronaldo-world-cup-2026-group-k":{"topic":"Превью Португалия – ДР Конго, шестой ЧМ Роналду, группа K","teams":["Португалия","ДР Конго"],"players":["Криштиану Роналду"]},
}

lines=[]
for a in man["articles"]:
    s=a["slug"]; m=META[s]
    lines.append({"timestamp":NOW,"run_id":RUN,"source_type":a["source_type"],"type":a["type"],
        "title":a["title"],"slug":s,"topic":m["topic"],"teams":m["teams"],"players":m["players"],
        "sources":a["sources"],"db_id":id_by_slug.get(s)})

with open(f"{BASE}/logs/articles-history.jsonl","a") as f:
    for ln in lines:
        f.write(json.dumps(ln,ensure_ascii=False)+"\n")

last={"run_id":RUN,"generated_at":NOW,"phase":"published_v4_groupstage",
      "counts":{"total":8,"news":5,"trend":3},
      "slugs":[a["slug"] for a in man["articles"]],
      "db_ids":id_by_slug}
json.dump(last,open(f"{BASE}/logs/last-run.json","w"),ensure_ascii=False,indent=2)

# local archive
for a in man["articles"]:
    src = "news-" if a["source_type"]=="news" else "trend-"
    folder=f"{BASE}/articles/{src}{a['slug']}"
    os.makedirs(folder,exist_ok=True)
    md=f"# {a['title']}\n\n_{a['excerpt']}_\n\n- Категория: {a['category']}\n- Тип: {a['type']}\n- Slug: {a['slug']}\n\n---\n\n{a['body']}\n"
    open(f"{folder}/{src}{a['slug']}.md","w").write(md)

print("appended",len(lines),"log lines; updated last-run.json; archived",len(man['articles']),"articles")
print("run_id",RUN)
