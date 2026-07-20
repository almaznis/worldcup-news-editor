# -*- coding: utf-8 -*-
"""Fetch landscape cover images from Wikimedia Commons, optimize to 16:9 JPEG,
base64-encode, and assemble the publish payload for run 2."""
import base64, io, json, os, time, sys
import requests
from PIL import Image
from run2_articles import ARTICLES, RUN_ID, GENERATED_AT

import unicodedata

def _norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()

# Per-slug image search: list of (query, required_title_token). Title must contain the token.
COVER_SEARCH = {
    "spain-argentina-world-cup-2026-final-report": [
        ("Ferran Torres footballer", "ferran torres"),
        ("Nico Williams footballer", "nico williams"),
        ("Unai Simon footballer", "unai sim"),
    ],
    "world-cup-2026-individual-awards": [
        ("Rodri footballer Spain", "rodri"),
        ("Kylian Mbappe", "mbappe"),
    ],
    "messi-argentina-future-after-world-cup-2026": [
        ("Lionel Messi Argentina 2024", "messi"),
    ],
    "joao-gomes-aston-villa-transfer-july-2026": [
        ("Joao Gomes Wolverhampton footballer", "joao gomes"),
        ("Villa Park Aston Villa stadium", "villa park"),
        ("Villa Park", "villa park"),
    ],
    "emiliano-martinez-world-cup-2026-final-saves-record": [
        ("Emiliano Martinez goalkeeper Argentina", "martinez"),
    ],
    "top-7-summer-2026-transfers": [
        ("Anthony Gordon footballer", "gordon"),
        ("Sandro Tonali footballer", "tonali"),
    ],
    "community-shield-2026-arsenal-manchester-city-preview": [
        ("Principality Stadium Cardiff", "stadium"),
        ("Millennium Stadium Cardiff", "stadium"),
    ],
    "world-cup-2026-in-numbers-records": [
        ("MetLife Stadium", "metlife"),
        ("MetLife Stadium aerial", "stadium"),
    ],
}
EXCLUDE = ["ponte", "bridge", "puente", "cartel", "cevicher", "street", " road",
           "funchal", " map", "logo", "emblem", "coat of arms", "stamp", "diagram",
           "gemeinde", "iglesia", "church", "cemetery", "grave", "plaque"]

CA = "/root/.ccr/ca-bundle.crt"
VERIFY = CA if os.path.exists(CA) else True
UA = "WorldCupNewsAgent/1.0 (Sport Arena Hub editorial bot; contact almaznis1@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"
HDRS = {"User-Agent": UA}

def commons_candidates(term):
    """Return list of imageinfo dicts (thumburl, width, height, mime) for a search term."""
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": term, "gsrnamespace": "6", "gsrlimit": "20",
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1600",
    }
    r = requests.get(API, params=params, headers=HDRS, verify=VERIFY, timeout=45)
    r.raise_for_status()
    pages = (r.json().get("query", {}) or {}).get("pages", {})
    out = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii:
            continue
        mime = ii.get("mime", "")
        w, h = ii.get("width", 0), ii.get("height", 0)
        if mime not in ("image/jpeg", "image/png"):
            continue
        if not w or not h:
            continue
        out.append({
            "title": p.get("title", ""),
            "thumburl": ii.get("thumburl") or ii.get("url"),
            "url": ii.get("url"),
            "width": w, "height": h, "mime": mime,
            "aspect": w / h,
        })
    # Prefer landscape, wide, decent res
    out = [c for c in out if c["aspect"] >= 1.25 and c["width"] >= 1000]
    out.sort(key=lambda c: (abs(c["aspect"] - 1.9), -c["width"]))
    return out

def filtered_candidates(query, token):
    cands = commons_candidates(query)
    tok = _norm(token)
    res = []
    for c in cands:
        t = _norm(c["title"])
        if tok not in t:
            continue
        if any(x in t for x in EXCLUDE):
            continue
        res.append(c)
    return res

def to_16x9_b64(img_bytes):
    im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    w, h = im.size
    target = 16 / 9
    ar = w / h
    if ar > target:  # too wide -> crop width
        nw = int(h * target); x = (w - nw) // 2
        im = im.crop((x, 0, x + nw, h))
    elif ar < target:  # too tall -> crop height (mild, sources are landscape)
        nh = int(w / target); y = int((h - nh) * 0.35)  # bias toward upper area (faces)
        im = im.crop((0, y, w, y + nh))
    im = im.resize((1600, 900), Image.LANCZOS)
    for q in (80, 72, 65, 58, 50):
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True)
        data = buf.getvalue()
        if len(data) <= 300 * 1024:
            return base64.b64encode(data).decode(), len(data), q
    return base64.b64encode(data).decode(), len(data), q

def fetch_cover(slug):
    for query, token in COVER_SEARCH[slug]:
        try:
            cands = filtered_candidates(query, token)
        except Exception as e:
            print(f"    search error '{query}': {e}")
            continue
        for c in cands[:6]:
            try:
                dl = requests.get(c["thumburl"], headers=HDRS, verify=VERIFY, timeout=60)
                dl.raise_for_status()
                b64, size, q = to_16x9_b64(dl.content)
                print(f"    OK '{query}' <- {c['title']} ({c['width']}x{c['height']}) -> {size//1024}KB q{q}")
                return b64, c["url"], c["title"]
            except Exception as e:
                print(f"    proc error {c.get('title')}: {e}")
                continue
        time.sleep(1.0)
    return None, None, None

def main():
    payload_articles = []
    manifest_articles = []
    for i, a in enumerate(ARTICLES, 1):
        print(f"[{i}/8] {a['slug']}")
        b64, src_url, title = fetch_cover(a["slug"])
        base = {
            "title": a["title"], "slug": a["slug"], "body": a["body"],
            "excerpt": a["excerpt"], "category": a["category"], "type": a["type"],
            "sources": a["sources"], "source_type": a["source_type"],
        }
        pay = dict(base)
        man = dict(base)
        if b64:
            pay["image_base64"] = b64
            pay["image_url"] = None
            man["image_url"] = None
            man["image_base64"] = None
            man["_img_source"] = src_url
        else:
            # fallback: use original Commons URL directly as image_url
            print(f"    !! no base64, fallback image_url search")
            fb = None
            for query, token in COVER_SEARCH[a["slug"]]:
                try:
                    cands = filtered_candidates(query, token)
                    if cands:
                        fb = cands[0]["url"]; break
                except Exception:
                    pass
            pay["image_base64"] = None
            pay["image_url"] = fb
            man["image_url"] = fb
            man["image_base64"] = None
            man["_img_source"] = fb
        payload_articles.append(pay)
        manifest_articles.append(man)
        time.sleep(3.5)  # Wikimedia rate-limit courtesy

    with open("run2_payload.json", "w", encoding="utf-8") as f:
        json.dump({"articles": payload_articles}, f, ensure_ascii=False)
    manifest = {"generated_at": GENERATED_AT, "run_id": RUN_ID, "articles": manifest_articles}
    with open("run2_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    n_b64 = sum(1 for p in payload_articles if p.get("image_base64"))
    n_url = sum(1 for p in payload_articles if p.get("image_url"))
    n_none = sum(1 for p in payload_articles if not p.get("image_base64") and not p.get("image_url"))
    print(f"\nDONE. base64={n_b64} image_url={n_url} no_image={n_none}")
    if n_none:
        print("WARNING: some articles have no cover image!")

if __name__ == "__main__":
    main()
