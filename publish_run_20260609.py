# -*- coding: utf-8 -*-
"""WorldCupNewsAgent run 2026-06-09. Builds 8 articles, optimizes Wikimedia covers
to base64, POSTs to the Sport Arena Hub publish endpoint, logs results."""
import os, io, json, base64, time, uuid, datetime, re, sys
import requests
from PIL import Image

ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
SECRET = os.environ.get("AGENT_PUBLISH_SECRET")
UA = {"User-Agent": "WorldCupNewsAgent/1.0 (editorial; almaznis1@gmail.com)"}
S = requests.Session(); S.headers.update(UA)
RUN_ID = "run-20260609-" + uuid.uuid4().hex[:8]
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

def commons_thumb(file_title, width=1600):
    """Return a thumbnail URL for a Commons File: title."""
    params = {"action": "query", "format": "json", "titles": file_title,
              "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": str(width)}
    r = S.get("https://commons.wikimedia.org/w/api.php", params=params, timeout=40)
    pages = r.json().get("query", {}).get("pages", {})
    for p in pages.values():
        ii = p.get("imageinfo", [{}])[0]
        return ii.get("thumburl") or ii.get("url")
    return None

def make_cover_b64(file_title):
    """Download, fit to 16:9 landscape, recompress JPEG <300KB, return base64."""
    url = commons_thumb(file_title, 1600)
    if not url:
        raise RuntimeError("no thumb for " + file_title)
    raw = S.get(url, timeout=60).content
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    w, h = im.size
    target = 16 / 9
    # Pad to 16:9 if needed (so a centre-crop never chops faces)
    if abs((w / h) - target) > 0.04:
        if w / h < target:           # too tall/narrow -> widen canvas
            nw = int(round(h * target)); nh = h
        else:                          # too wide -> heighten canvas
            nw = w; nh = int(round(w / target))
        canvas = Image.new("RGB", (nw, nh), (16, 16, 18))
        canvas.paste(im, ((nw - w) // 2, (nh - h) // 2))
        im = canvas
    # resize longest side to ~1600
    if im.size[0] > 1600:
        im = im.resize((1600, int(round(1600 * im.size[1] / im.size[0]))), Image.LANCZOS)
    q = 84
    while True:
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=q, optimize=True)
        data = buf.getvalue()
        if len(data) <= 300_000 or q <= 60:
            break
        q -= 6
    print(f"  cover {file_title[:40]:42s} {im.size[0]}x{im.size[1]} {len(data)//1024}KB q{q}")
    return base64.b64encode(data).decode("ascii")

# ---- inline image URLs (direct, name-verified Commons files) -------------
IMG = {
 "ronaldo":   "https://upload.wikimedia.org/wikipedia/commons/5/5b/Cristiano_Ronaldo_with_Al_Nassr%2C_19_September_2023_-_44.jpg",
 "mbappe":    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Kylian_Mbapp%C3%A9_receives_the_best_young_player_award_at_the_2018_Football_World_Cup_Russia.jpg/1280px-Kylian_Mbapp%C3%A9_receives_the_best_young_player_award_at_the_2018_Football_World_Cup_Russia.jpg",
 "haaland":   "https://upload.wikimedia.org/wikipedia/commons/7/71/Erling_Haaland_June_2025.jpg",
 "yamal":     "https://upload.wikimedia.org/wikipedia/commons/4/4f/Lamine_Yamal_%282025%29.png",
 "bellingham":"https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Jude_Bellingham_during_an_EA_Sports_event_in_September_2024.jpg/1280px-Jude_Bellingham_during_an_EA_Sports_event_in_September_2024.jpg",
 "shomurodov":"https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Eldor_Shomurodov_14_%C4%B0stanbul_Ba%C5%9Fak%C5%9Fehir_FK_20250731_%285%29.jpg/1280px-Eldor_Shomurodov_14_%C4%B0stanbul_Ba%C5%9Fak%C5%9Fehir_FK_20250731_%285%29.jpg",
 "messi":     "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/FWC_2018_-_Group_D_-_ARG_v_ISL_-_Messi_penalty_kick.jpg/1280px-FWC_2018_-_Group_D_-_ARG_v_ISL_-_Messi_penalty_kick.jpg",
}

from articles_data_20260609 import ARTICLES

def build_payload():
    """Attach optimized base64 covers; return list of API article objects + meta."""
    payload = []
    for a in ARTICLES:
        b64 = make_cover_b64(a["cover"])
        payload.append({
            "title": a["title"], "slug": a["slug"], "body": a["body"],
            "excerpt": a["excerpt"], "category": a["category"], "type": a["type"],
            "image_url": None, "image_base64": b64,
            "sources": a["sources"], "source_type": a["source_type"],
        })
    return payload

def post(articles):
    r = requests.post(ENDPOINT, headers={"Content-Type": "application/json",
                                         "x-agent-secret": SECRET},
                      data=json.dumps({"articles": articles}), timeout=180)
    return r

def main():
    if not SECRET:
        print("FATAL: AGENT_PUBLISH_SECRET missing"); sys.exit(1)
    print(f"RUN {RUN_ID}  building {len(ARTICLES)} articles ...")
    payload = build_payload()

    print("POSTing batch ...")
    r = post(payload)
    print("HTTP", r.status_code)
    if r.status_code == 401:
        print("FATAL 401 unauthorized - secret rejected"); sys.exit(1)
    results = r.json().get("results", [])
    by_slug = {x.get("slug"): x for x in results}

    # retry errored items once
    errored = [p for p in payload if by_slug.get(p["slug"], {}).get("status") == "error"
               or p["slug"] not in by_slug]
    if errored:
        print(f"Retrying {len(errored)} errored item(s) ...")
        time.sleep(3)
        r2 = post(errored)
        for x in r2.json().get("results", []):
            by_slug[x.get("slug")] = x

    # report + write logs
    hist_lines = []
    inserted = 0
    last_slugs = []
    for a, p in zip(ARTICLES, payload):
        res = by_slug.get(p["slug"], {})
        status = res.get("status", "missing")
        db_slug = res.get("slug", p["slug"])
        last_slugs.append(db_slug)
        if status == "inserted":
            inserted += 1
        suffixed = bool(re.search(r"-\d+$", db_slug)) and db_slug != p["slug"]
        print(f"  [{status}] {db_slug}{'  (SLUG SUFFIXED!)' if suffixed else ''}")
        hist_lines.append({
            "timestamp": NOW, "run_id": RUN_ID, "publish_status": status,
            "db_id": res.get("id"), "db_slug": db_slug,
            "source_type": a["source_type"], "type": a["type"],
            "title": a["title"], "slug": a["slug"],
            "image_via": "base64", "category": a["category"],
            "topic": a["excerpt"], "teams": [], "players": [],
            "sources": a["sources"], "error": res.get("error"),
        })

    # append only successfully inserted lines to history
    with open("logs/articles-history.jsonl", "a", encoding="utf-8") as f:
        for line in hist_lines:
            if line["publish_status"] == "inserted":
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
    with open("logs/last-run.json", "w", encoding="utf-8") as f:
        json.dump({"run_id": RUN_ID, "generated_at": NOW, "phase": "news+trend_v1",
                   "count": len(ARTICLES), "inserted": inserted,
                   "db_slugs": last_slugs}, f, ensure_ascii=False, indent=2)

    # local archive
    for a, p in zip(ARTICLES, payload):
        src = "news" if a["source_type"] == "news" else "trend"
        d = f"articles/{src}-{a['slug']}"
        os.makedirs(d, exist_ok=True)
        with open(f"{d}/{src}-{a['slug']}.md", "w", encoding="utf-8") as f:
            f.write(f"# {a['title']}\n\n*{a['excerpt']}*\n\n"
                    f"- type: {a['type']}\n- category: {a['category']}\n"
                    f"- source_type: {a['source_type']}\n- cover: {a['cover']}\n\n---\n\n"
                    + a["body"] + "\n")

    print(f"\nDONE: {inserted}/{len(ARTICLES)} inserted.")
    # final manifest (no base64, no secret) for auditing
    manifest = {"generated_at": NOW, "run_id": RUN_ID, "articles": [
        {"title": a["title"], "slug": a["slug"], "excerpt": a["excerpt"],
         "category": a["category"], "type": a["type"], "source_type": a["source_type"],
         "image_url": by_slug.get(a["slug"], {}).get("image_url"),
         "status": by_slug.get(a["slug"], {}).get("status"),
         "sources": a["sources"]} for a in ARTICLES]}
    with open("logs/manifest-20260609.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    return inserted

if __name__ == "__main__":
    main()
