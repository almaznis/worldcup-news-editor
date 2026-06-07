#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re-publish all 8 articles with face-cropped portrait images (base64 → Supabase
images bucket) and Russian-language YouTube video sections.
New slugs will get a -3 suffix (originals = base, -2 = English media run).
"""
import base64, json, os, urllib.request, urllib.error

RUN_ID   = "run-20260607-c2721e42-v3"
SECRET   = os.environ["AGENT_PUBLISH_SECRET"]
ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"

# ── Portrait images (Wikimedia Commons, CC-licensed, all < 1.1 MB) ───────────
IMAGES = {
    # Neymar — 402 KB portrait crop
    "neymar":   "https://upload.wikimedia.org/wikipedia/commons/7/7d/Neymar_cropped_image.png",
    # Kevin De Bruyne — 126 KB portrait (WC 2022)
    "debruyne": "https://upload.wikimedia.org/wikipedia/commons/c/c1/Kevin_De_Bruyne_WC2022.jpg",
    # Jamal Musiala — 435 KB cropped portrait (Germany)
    "musiala":  "https://upload.wikimedia.org/wikipedia/commons/4/44/Jamal_Musiala_2022_%28cropped%29.jpg",
    # Harry Kane — 458 KB cropped portrait
    "kane":     "https://upload.wikimedia.org/wikipedia/commons/6/69/Harry_Kane_2023_%28cropped%29.jpg",
    # Lionel Messi — 565 KB portrait
    "messi":    "https://upload.wikimedia.org/wikipedia/commons/c/c1/Lionel_Messi_20180626.jpg",
    # 2026 WC emblem — SVG kept as URL (no base64 for SVG)
    "wc_emblem_url": "https://upload.wikimedia.org/wikipedia/commons/1/17/2026_FIFA_World_Cup_emblem.svg",
    # Erling Haaland — 1 MB cropped portrait
    "haaland":  "https://upload.wikimedia.org/wikipedia/commons/0/07/Erling_Haaland_2023_%28cropped%29.jpg",
    # Hirving "Chucky" Lozano — 509 KB portrait (Mexico)
    "lozano":   "https://upload.wikimedia.org/wikipedia/commons/e/e3/Hirving_Lozano.png",
}

# ── Russian-language YouTube video IDs ───────────────────────────────────────
YT = {
    # "Сможет НЕЙМАР взять ЧМ 2026 и СТАТЬ ЛЕГЕНДОЙ БРАЗИЛИИ?"
    "neymar_brazil":   "qeAmSDjLhiE",
    # "Бельгия - Тунис. Видеообзор матча"
    "belgium_tunisia": "3kPJfrTIM2M",
    # "США — Германия | Товарищеский матч 2026: немцы не остановятся"
    "germany_usa":     "Ean5PR3oU3k",
    # "Англия – Новая Зеландия | Товарищеский матч. Обзор"
    "england_nz":      "Pfr7mzQsWMQ",
    # "МЕССИ ОБЪЯВИЛ О ЗАВЕРШЕНИИ КАРЬЕРЫ: ЗВЕЗДЫ ФУТБОЛА В ШОКЕ"
    "messi_argentina": "0m2vVhT-XDE",
    # "ТОП-10 Главные ФАВОРИТЫ ЧМ 2026! Кто из них выиграет?"
    "wc_predictions":  "lLdfDEJiKjg",
    # "Группа I. Франция, Сенегал, Норвегия, Ирак [ЧМ-2026]"
    "norway_haaland":  "Ipl0BqeySs4",
    # "Группа А: Мексика, ЮАР, Чехия, Южная Корея [ЧМ-2026]"
    "mexico_sa":       "BpbQDkSPjSc",
}


def download_base64(url: str) -> str | None:
    """Download image from URL and return base64-encoded string, or None on error."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        encoded = base64.b64encode(data).decode("ascii")
        print(f"  ↓ {url.split('/')[-1]}  ({len(data)//1024} KB → {len(encoded)//1024} KB b64)")
        return encoded
    except Exception as exc:
        print(f"  ✗ Failed to download {url}: {exc}")
        return None


def yt_section(video_id: str, label: str) -> str:
    thumb = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    link  = f"https://www.youtube.com/watch?v={video_id}"
    return (
        f"\n\n## Видео по теме\n\n"
        f"[![{label}]({thumb})]({link})\n\n"
        f"[Смотреть на YouTube →]({link})"
    )


# ── Pre-download all portrait images ─────────────────────────────────────────
print("Downloading portrait images…")
b64 = {key: download_base64(url) for key, url in IMAGES.items()
       if not key.endswith("_url")}

# ── Load original articles ────────────────────────────────────────────────────
with open("/tmp/articles_payload.json", "r", encoding="utf-8") as f:
    originals = json.load(f)["articles"]

# ── Build updated articles ────────────────────────────────────────────────────
updated = []
for a in originals:
    art  = dict(a)
    slug = a["slug"]

    # strip any YouTube section added in a previous run
    body = art["body"]
    if "\n\n## Видео по теме" in body:
        body = body[:body.index("\n\n## Видео по теме")]
    art["body"] = body.rstrip()

    # reset media fields
    art["image_url"]    = None
    art["image_base64"] = None

    if "neymar" in slug:
        art["image_base64"] = b64.get("neymar")
        yt_id, yt_label = YT["neymar_brazil"], "Неймар и Бразилия на ЧМ-2026"

    elif "belgium" in slug:
        art["image_base64"] = b64.get("debruyne")
        yt_id, yt_label = YT["belgium_tunisia"], "Бельгия — Тунис: видеообзор матча"

    elif "germany" in slug:
        art["image_base64"] = b64.get("musiala")
        yt_id, yt_label = YT["germany_usa"], "США — Германия: товарищеский матч 2026"

    elif "england" in slug:
        art["image_base64"] = b64.get("kane")
        yt_id, yt_label = YT["england_nz"], "Англия — Новая Зеландия: обзор матча"

    elif "messi" in slug:
        art["image_base64"] = b64.get("messi")
        yt_id, yt_label = YT["messi_argentina"], "Месси объявил о завершении карьеры"

    elif "top-7" in slug:
        # SVG not suitable for base64; keep as image_url
        art["image_url"]    = IMAGES["wc_emblem_url"]
        art["image_base64"] = None
        yt_id, yt_label = YT["wc_predictions"], "ТОП-10 фаворитов ЧМ-2026"

    elif "norway" in slug:
        art["image_base64"] = b64.get("haaland")
        yt_id, yt_label = YT["norway_haaland"], "Группа I ЧМ-2026: Норвегия и Холанн"

    elif "mexico" in slug:
        art["image_base64"] = b64.get("lozano")
        yt_id, yt_label = YT["mexico_sa"], "Группа А ЧМ-2026: Мексика и ЮАР"

    else:
        yt_id, yt_label = None, None

    if yt_id:
        art["body"] = art["body"] + yt_section(yt_id, yt_label)

    updated.append(art)

# ── Publish ───────────────────────────────────────────────────────────────────
payload = json.dumps({"articles": updated}, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(ENDPOINT, data=payload, method="POST")
req.add_header("Content-Type", "application/json")
req.add_header("x-agent-secret", SECRET)

print(f"\nPublishing {len(updated)} articles ({len(payload)//1024} KB payload)…")
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read().decode())
    print("Response:")
    results = resp.get("results", [])
    for item in results:
        status = item.get("status")
        slug   = item.get("slug")
        err    = item.get("error")
        mark   = "✓" if status == "inserted" else "✗"
        print(f"  {mark} {slug}  [{status}]" + (f"  ERROR: {err}" if err else ""))
except urllib.error.HTTPError as e:
    body_err = e.read().decode()[:600]
    print(f"HTTP Error {e.code}: {body_err}")
    results = []

# ── Log ───────────────────────────────────────────────────────────────────────
with open("/tmp/articles_v3.json", "w", encoding="utf-8") as f:
    json.dump({"run_id": RUN_ID, "articles": updated}, f, ensure_ascii=False, indent=2)
print("\nPayload saved to /tmp/articles_v3.json")

# Append to history log
log_path = "/home/user/worldcup-news-editor/logs/articles-history.jsonl"
os.makedirs(os.path.dirname(log_path), exist_ok=True)
from datetime import datetime, timezone
ts = datetime.now(timezone.utc).isoformat()
for art in updated:
    entry = {
        "timestamp":      ts,
        "run_id":         RUN_ID,
        "phase":          "media_v3_ru_portrait",
        "slug":           art["slug"],
        "title":          art.get("title"),
        "has_base64_img": art.get("image_base64") is not None,
        "image_url":      art.get("image_url"),
        "has_youtube":    "## Видео по теме" in art.get("body", ""),
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# Update last-run.json
db_slugs = [r.get("slug") for r in results if r.get("status") == "inserted"]
last_run = {
    "run_id":   RUN_ID,
    "phase":    "media_v3_ru_portrait",
    "count":    len(updated),
    "db_slugs": db_slugs,
}
with open("/home/user/worldcup-news-editor/logs/last-run.json", "w", encoding="utf-8") as f:
    json.dump(last_run, f, ensure_ascii=False, indent=2)
print("Logs updated.")
