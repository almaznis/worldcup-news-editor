#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re-publish all 8 articles with cover images and YouTube video sections.
Because the publish endpoint is INSERT-only, the endpoint will append -2 to each slug.
The -2 versions become the canonical updated articles; originals can be deleted.
"""
import json, os, urllib.request, urllib.error

RUN_ID     = "run-20260607-c2721e42"
SECRET     = os.environ["AGENT_PUBLISH_SECRET"]
ENDPOINT   = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"

# ── Images (Wikimedia Commons, CC-licensed) ─────────────────────────────────
IMAGES = {
    "neymar":    "https://upload.wikimedia.org/wikipedia/commons/7/7d/Neymar_cropped_image.png",
    "debruyne":  "https://upload.wikimedia.org/wikipedia/commons/c/c1/Kevin_De_Bruyne_WC2022.jpg",
    "wc_emblem": "https://upload.wikimedia.org/wikipedia/commons/1/17/2026_FIFA_World_Cup_emblem.svg",
    "messi":     "https://upload.wikimedia.org/wikipedia/commons/c/c1/Lionel_Messi_20180626.jpg",
    "haaland":   "https://upload.wikimedia.org/wikipedia/commons/7/71/Erling_Haaland_June_2025.jpg",
    "azteca":    "https://upload.wikimedia.org/wikipedia/commons/0/07/Vista_a%C3%A9rea_del_Estadio_Azteca_-_2026_-_02.jpg",
}

# ── YouTube video IDs ─────────────────────────────────────────────────────────
YT = {
    "neymar_brazil":   "nBsDhI_PubM",   # "Neymar's Last Dance? Brazil FIFA World Cup 2026 Squad Preview"
    "belgium_tunisia": "bTBJNWjlQlk",   # "Belgium v Tunisia | Highlights | International Friendly"
    "germany_usa":     "2CcSe1TpsZI",   # "Successful dress rehearsal | USA 1-2 Germany | Official German FA"
    "england_nz":      "OTfxv7maySo",   # "HIGHLIGHTS - Kane scores 67th goal! England v New Zealand"
    "messi_argentina": "yhTRnnsx99g",   # "Lionel Messi's Last Dance | Argentina WC 2026 Squad Analysis"
    "wc_predictions":  "R9wzwNlQzow",   # "2026 FIFA World Cup Super Preview: FULL Bracket Predictions"
    "norway_haaland":  "zldEDHQFllw",   # "How far can Norway go? | FIFA WC 2026 Norway Preview"
    "mexico_sa":       "UoKvrLA6tMI",   # FIFA Mexico vs South Africa match preview
}

def yt_section(video_id, label):
    thumb = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    link  = f"https://www.youtube.com/watch?v={video_id}"
    return (
        f"\n\n## Видео по теме\n\n"
        f"[![{label}]({thumb})]({link})\n\n"
        f"[Смотреть на YouTube →]({link})"
    )

# ── Load original articles ────────────────────────────────────────────────────
with open("/tmp/articles_payload.json", "r", encoding="utf-8") as f:
    originals = json.load(f)["articles"]

# ── Build updated articles ────────────────────────────────────────────────────
updated = []
for a in originals:
    art = dict(a)
    slug = a["slug"]

    # --- IMAGE ---
    if "neymar" in slug:
        art["image_url"] = IMAGES["neymar"]
        yt_id, yt_label = YT["neymar_brazil"], "Бразилия на ЧМ-2026: превью"
    elif "belgium" in slug:
        art["image_url"] = IMAGES["debruyne"]
        yt_id, yt_label = YT["belgium_tunisia"], "Бельгия 5:0 Тунис — хайлайты"
    elif "germany" in slug:
        art["image_url"] = IMAGES["wc_emblem"]
        yt_id, yt_label = YT["germany_usa"], "США 1:2 Германия — хайлайты (официальный канал DFB)"
    elif "england" in slug:
        art["image_url"] = None          # no good CC image found for Kane
        yt_id, yt_label = YT["england_nz"], "Англия 1:0 Новая Зеландия — хайлайты (Кейн — 67-й гол в сезоне!)"
    elif "messi" in slug:
        art["image_url"] = IMAGES["messi"]
        yt_id, yt_label = YT["messi_argentina"], "Месси на ЧМ-2026: последний шанс Аргентины?"
    elif "top-7" in slug:
        art["image_url"] = IMAGES["wc_emblem"]
        yt_id, yt_label = YT["wc_predictions"], "Полный прогноз ЧМ-2026: кто победит?"
    elif "norway" in slug:
        art["image_url"] = IMAGES["haaland"]
        yt_id, yt_label = YT["norway_haaland"], "Как далеко зайдёт Норвегия на ЧМ-2026?"
    elif "mexico" in slug:
        art["image_url"] = IMAGES["azteca"]
        yt_id, yt_label = YT["mexico_sa"], "Мексика против ЮАР — превью открытия ЧМ-2026"
    else:
        art["image_url"] = None
        yt_id, yt_label = None, None

    # --- YOUTUBE ---
    if yt_id:
        art["body"] = art["body"].rstrip() + yt_section(yt_id, yt_label)

    art["image_base64"] = None
    updated.append(art)

# ── Publish ───────────────────────────────────────────────────────────────────
payload = json.dumps({"articles": updated}, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(ENDPOINT, data=payload, method="POST")
req.add_header("Content-Type", "application/json")
req.add_header("x-agent-secret", SECRET)

print(f"Publishing {len(updated)} updated articles ({len(payload)//1024}KB payload)…")
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read().decode())
    print("Response:")
    for item in resp.get("results", []):
        status = item.get("status")
        slug   = item.get("slug")
        err    = item.get("error")
        mark   = "✓" if status == "inserted" else "✗"
        print(f"  {mark} {slug}  [{status}]" + (f"  ERROR: {err}" if err else ""))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()[:400]}")

# ── Save updated payload for logging ─────────────────────────────────────────
with open("/tmp/articles_updated.json", "w", encoding="utf-8") as f:
    json.dump({"run_id": RUN_ID, "articles": updated}, f, ensure_ascii=False, indent=2)
print("\nUpdated payload saved to /tmp/articles_updated.json")
