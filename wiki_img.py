#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find candidate Wikimedia Commons images for a subject, preferring landscape.

Usage: python3 wiki_img.py "Lamine Yamal"
Prints candidate image URLs with dimensions so we can pick a wide (landscape)
CC-licensed photo for a 16:9 cover.
"""
import json, sys, urllib.parse, urllib.request

UA = {"User-Agent": "WorldCupNewsAgent/1.0 (editorial; almaznis1@gmail.com)"}
API = "https://commons.wikimedia.org/w/api.php"


def _get(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())


def search(query: str, limit: int = 25):
    # search in the File namespace (6)
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{query}", "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1600",
    }
    data = _get(params)
    pages = data.get("query", {}).get("pages", {})
    rows = []
    for p in pages.values():
        ii = p.get("imageinfo", [{}])[0]
        mime = ii.get("mime", "")
        if mime not in ("image/jpeg", "image/png"):
            continue
        w, h = ii.get("width", 0), ii.get("height", 0)
        if not w or not h:
            continue
        meta = ii.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "?")
        rows.append({
            "title": p.get("title"),
            "w": w, "h": h, "ratio": round(w / h, 2),
            "url": ii.get("url"),
            "thumb": ii.get("thumburl"),
            "license": lic,
        })
    # prefer landscape (ratio >= 1.2), then larger
    rows.sort(key=lambda r: (r["ratio"] < 1.2, -(r["w"] * r["h"])))
    return rows


if __name__ == "__main__":
    q = " ".join(sys.argv[1:])
    for r in search(q):
        tag = "LANDSCAPE" if r["ratio"] >= 1.2 else "portrait "
        print(f"{tag} {r['w']}x{r['h']} r={r['ratio']} [{r['license']}] {r['url']}")
