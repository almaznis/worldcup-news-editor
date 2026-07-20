# -*- coding: utf-8 -*-
"""Append history log lines, write last-run.json, and archive markdown for run 2."""
import json, os
from datetime import datetime, timezone
from run2_articles import ARTICLES, RUN_ID, GENERATED_AT

results = json.load(open("run2_results.json"))["results"]
res_by_slug = {}
# results preserve order of payload; map by requested slug order
for a, x in zip(ARTICLES, results):
    res_by_slug[a["slug"]] = x

TOPICS = {
    "spain-argentina-world-cup-2026-final-report": ("Финал ЧМ-2026: Испания обыграла Аргентину 1:0 (Ф. Торрес 106'), второй титул чемпиона мира", ["Испания","Аргентина"], ["Ферран Торрес","Нико Уильямс","Лионель Месси"]),
    "world-cup-2026-individual-awards": ("Индивидуальные награды ЧМ-2026: Родри – Золотой мяч, Мбаппе – Золотая бутса, Симон, Кубарси", [], ["Родри","Килиан Мбаппе","Унаи Симон","Пау Кубарси"]),
    "messi-argentina-future-after-world-cup-2026": ("Будущее Месси в сборной Аргентины после поражения в финале ЧМ-2026", ["Аргентина"], ["Лионель Месси"]),
    "joao-gomes-aston-villa-transfer-july-2026": ("Трансфер: Жоао Гомес перешёл из Вулверхэмптона в Астон Виллу за ~38 млн фунтов (20 июля)", ["Астон Вилла","Вулверхэмптон"], ["Жоао Гомес"]),
    "emiliano-martinez-world-cup-2026-final-saves-record": ("Эмилиано Мартинес – рекорд по сейвам в финале ЧМ (11), играл со сломанным пальцем", ["Аргентина"], ["Эмилиано Мартинес"]),
    "top-7-summer-2026-transfers": ("Топ-7 трансферов лета 2026 (Андерсон, Тонали, Фернандеш, Гордон, Рамуш, Роджерс, Гримальдо)", [], ["Эллиот Андерсон","Сандро Тонали","Антони Гордон","Гонсалу Рамуш","Алекс Гримальдо"]),
    "community-shield-2026-arsenal-manchester-city-preview": ("Превью Суперкубка Англии 2026: Арсенал – Манчестер Сити, 16 августа, Кардифф", ["Арсенал","Манчестер Сити"], []),
    "world-cup-2026-in-numbers-records": ("Рекорды ЧМ-2026 в цифрах: 48 команд, 104 матча, посещаемость, результативность, 21 гол Месси", [], ["Лионель Месси","Энсо Фернандес"]),
}

now = datetime.now(timezone.utc).isoformat()
os.makedirs("logs", exist_ok=True)
lines = []
for a in ARTICLES:
    x = res_by_slug[a["slug"]]
    topic, teams, players = TOPICS[a["slug"]]
    entry = {
        "timestamp": now,
        "run_id": RUN_ID,
        "source_type": a["source_type"],
        "type": a["type"],
        "title": a["title"],
        "slug": a["slug"],
        "db_slug": x.get("slug"),
        "db_id": x.get("id"),
        "publish_status": x.get("status"),
        "topic": topic,
        "teams": teams,
        "players": players,
        "sources": a["sources"],
    }
    lines.append(json.dumps(entry, ensure_ascii=False))

with open("logs/articles-history.jsonl", "a", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

last_run = {
    "run_id": RUN_ID,
    "generated_at": GENERATED_AT,
    "count": len(ARTICLES),
    "news_count": sum(1 for a in ARTICLES if a["source_type"] == "news"),
    "trend_count": sum(1 for a in ARTICLES if a["source_type"] == "trend"),
    "inserted": sum(1 for x in results if x.get("status") == "inserted"),
    "db_slugs": [res_by_slug[a["slug"]].get("slug") for a in ARTICLES],
}
json.dump(last_run, open("logs/last-run.json", "w"), ensure_ascii=False, indent=2)

# Archive markdown
for a in ARTICLES:
    src = "news" if a["source_type"] == "news" else "trend"
    folder = f"articles/{src}-{a['slug']}"
    os.makedirs(folder, exist_ok=True)
    md = f"# {a['title']}\n\n> {a['excerpt']}\n\n*Категория: {a['category']} · Тип: {a['type']} · {a['source_type']}*\n\n{a['body']}\n"
    with open(f"{folder}/{src}-{a['slug']}.md", "w", encoding="utf-8") as f:
        f.write(md)

print("appended", len(lines), "log lines; wrote last-run.json; archived", len(ARTICLES), "articles")
print("last-run:", json.dumps(last_run, ensure_ascii=False))
