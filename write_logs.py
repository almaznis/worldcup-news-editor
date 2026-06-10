#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, datetime
run = json.load(open("/tmp/run_result.json"))
imgs = json.load(open("/tmp/images.json"))
results = {r["slug"]: r for r in run["results"]}
arts = {a["slug"]: a for a in run["articles"]}
ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

META = {
 "usa-paraguay-world-cup-2026-opener-preview": ("Превью стартового матча группы D США – Парагвай (12 июня), хозяева ЧМ-2026", ["США","Парагвай"], ["Кристиан Пулишич","Маурисио Почеттино"]),
 "iran-world-cup-2026-tickets-revoked-supporters": ("США отозвали билетную квоту сборной Ирана за 3 дня до ЧМ-2026; визовый скандал", ["Иран"], []),
 "spain-3-1-peru-world-cup-2026-warmup": ("Товарищеский матч Перу 1:3 Испания (8/9 июня), последний спарринг перед ЧМ, без Ямаля", ["Испания","Перу"], ["Микель Ойярсабаль","Педри","Ламин Ямаль"]),
 "netherlands-timber-out-world-cup-2026": ("Юрриен Тимбер выбыл с ЧМ-2026 из-за травмы паха, вызван Гертрёйда", ["Нидерланды"], ["Юрриен Тимбер","Лютсхарел Гертрёйда","Рональд Куман"]),
 "world-cup-2026-golden-boot-favourites-ranking": ("Топ-7 претендентов на Золотую бутсу ЧМ-2026 по котировкам букмекеров", [], ["Килиан Мбаппе","Харри Кейн","Эрлинг Холанд","Лионель Месси"]),
 "england-saka-fitness-world-cup-2026": ("Тухель о неполной готовности Букайо Саки к старту Англии на ЧМ-2026 (пресс-конф. 9 июня)", ["Англия"], ["Букайо Сака","Томас Тухель"]),
 "uzbekistan-debut-vs-colombia-world-cup-2026": ("Превью первого в истории матча Узбекистана на ЧМ – против Колумбии 17 июня, группа K", ["Узбекистан","Колумбия"], ["Эльдор Шомуродов","Абдукодир Хусанов","Фабио Каннаваро"]),
 "world-cup-2026-last-dance-legends-ranking": ("Топ-7 ветеранов, для которых ЧМ-2026 станет последним (Роналду, Месси, Модрич и др.)", [], ["Криштиану Роналду","Лионель Месси","Лука Модрич"]),
}

with open("logs/articles-history.jsonl", "a", encoding="utf-8") as f:
    for slug, (topic, teams, players) in META.items():
        a = arts[slug]; r = results[slug]; im = imgs.get(slug) or {}
        entry = {
            "timestamp": ts, "run_id": run["run_id"], "publish_status": r["status"],
            "db_id": r["id"], "source_type": a["source_type"], "type": a["type"],
            "title": a["title"], "slug": slug, "topic": topic,
            "teams": teams, "players": players, "sources": a["sources"],
            "image_title": im.get("title"), "has_base64_img": bool(im.get("b64")),
        }
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

summary = {
    "run_id": run["run_id"], "generated_at": run["generated_at"],
    "counts": {"total": 8, "news": 5, "trend": 3,
               "inserted": sum(1 for r in results.values() if r["status"]=="inserted")},
    "slugs": list(META.keys()),
}
json.dump(summary, open("logs/last-run.json", "w"), ensure_ascii=False, indent=2)
print("logs updated. inserted:", summary["counts"]["inserted"])
