#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch landscape 16:9 cover images from Wikimedia Commons, optimize, base64."""
import base64, io, json, time, urllib.parse, urllib.request
from PIL import Image, ImageOps

UA = "WorldCupNewsAgent/1.0 (https://futbol.kz; almaznis1@gmail.com) Python-urllib"
API = "https://commons.wikimedia.org/w/api.php"

# slug -> list of search queries (tried in order)
SUBJECTS = {
    "usa-paraguay-world-cup-2026-opener-preview":     ["Christian Pulisic 2024", "Christian Pulisic"],
    "iran-world-cup-2026-tickets-revoked-supporters": ["Mehdi Taremi 2023", "Mehdi Taremi", "Iran national football team 2026"],
    "spain-3-1-peru-world-cup-2026-warmup":           ["Pedri 2024", "Pedri Gonzalez footballer", "Mikel Oyarzabal"],
    "netherlands-timber-out-world-cup-2026":          ["Jurrien Timber 2024", "Jurrien Timber", "Ronald Koeman 2024"],
    "world-cup-2026-golden-boot-favourites-ranking":  ["Kylian Mbappe 2024", "Kylian Mbappe Real Madrid"],
    "england-saka-fitness-world-cup-2026":            ["Bukayo Saka 2024", "Bukayo Saka", "Bukayo Saka England"],
    "uzbekistan-debut-vs-colombia-world-cup-2026":    ["Abdukodir Khusanov", "Eldor Shomurodov 2023", "Eldor Shomurodov"],
    "world-cup-2026-last-dance-legends-ranking":      ["Cristiano Ronaldo 2024", "Cristiano Ronaldo Al Nassr 2023"],
}

BAD = ("logo", "icon", "signature", "map", "coat of arms", "emblem", "badge",
       "diagram", "kit", "stadium", "crowd", "trophy", "flag")

def api_search(query, limit=15):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f'filetype:bitmap {query}', "gsrnamespace": "6",
        "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1600",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def pick(query):
    data = api_search(query)
    pages = (data.get("query") or {}).get("pages") or {}
    cands = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [None])[0]
        if not ii:
            continue
        title = p.get("title", "").lower()
        if any(b in title for b in BAD):
            continue
        w, h = ii.get("width", 0), ii.get("height", 0)
        mime = ii.get("mime", "")
        if w < 1000 or h == 0:
            continue
        if w <= h:           # require landscape
            continue
        if mime not in ("image/jpeg", "image/png"):
            continue
        # license check (must be CC/PD)
        meta = ii.get("extmetadata", {})
        lic = (meta.get("LicenseShortName", {}) or {}).get("value", "").lower()
        if lic and not any(k in lic for k in ("cc", "public domain", "pd")):
            continue
        cands.append((w / h, ii["thumburl"], p["title"], lic, w, h))
    # prefer aspect ratio closest to 16:9 (1.78), but >= 1.3
    cands = [c for c in cands if c[0] >= 1.3]
    cands.sort(key=lambda c: abs(c[0] - 1.78))
    return cands[0] if cands else None

def optimize(thumburl):
    req = urllib.request.Request(thumburl, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img).convert("RGB")
    # resize longest side to 1600
    if img.width > 1600:
        img = img.resize((1600, round(img.height * 1600 / img.width)), Image.LANCZOS)
    # center-crop / pad toward 16:9 so the on-site center crop keeps the face
    target = 16 / 9
    ar = img.width / img.height
    if ar < target:  # too tall -> letterbox top/bottom (keep face, no crop)
        new_h = round(img.width / target)
        canvas = Image.new("RGB", (img.width, new_h), (15, 17, 22))
        canvas.paste(img, (0, (new_h - img.height) // 2))
        img = canvas
    q = 82
    while True:
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=q, optimize=True)
        if buf.tell() <= 300_000 or q <= 50:
            break
        q -= 8
    return buf.getvalue()

out = {}
for slug, queries in SUBJECTS.items():
    chosen = None
    for q in queries:
        try:
            chosen = pick(q)
        except Exception as e:
            print(f"  search error {q}: {e}")
            chosen = None
        if chosen:
            print(f"[{slug}] q='{q}' -> {chosen[2]} ar={chosen[0]:.2f} {chosen[4]}x{chosen[5]} lic={chosen[3]}")
            break
        time.sleep(1)
    if not chosen:
        print(f"[{slug}] NO IMAGE FOUND")
        out[slug] = None
        continue
    try:
        data = optimize(chosen[1])
        b64 = base64.b64encode(data).decode()
        out[slug] = {"b64_len": len(b64), "kb": round(len(data)/1024, 1),
                     "title": chosen[2], "thumburl": chosen[1], "b64": b64}
        print(f"    optimized -> {out[slug]['kb']} KB")
    except Exception as e:
        print(f"    optimize error: {e}")
        out[slug] = None
    time.sleep(3.5)  # Wikimedia rate-limit courtesy

with open("/tmp/images.json", "w") as f:
    json.dump(out, f)
print("\nSUMMARY:")
for s, v in out.items():
    print(f"  {s}: {'OK '+str(v['kb'])+'KB '+v['title'] if v else 'MISSING'}")
