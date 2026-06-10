#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64, io, json, time, urllib.parse, urllib.request
from PIL import Image, ImageOps
from fetch_images import api_search, optimize, BAD

RETRY = {
    "world-cup-2026-golden-boot-favourites-ranking": [
        "Kylian Mbappe 2022 FIFA World Cup", "Kylian Mbappe France 2021",
        "Kylian Mbappe 2025", "Harry Kane 2024 Bayern", "Harry Kane England 2022"],
    "england-saka-fitness-world-cup-2026": [
        "Bukayo Saka Arsenal 2023", "Bukayo Saka 2023", "Bukayo Saka Arsenal"],
    "iran-world-cup-2026-tickets-revoked-supporters": [
        "Mehdi Taremi Porto", "Mehdi Taremi 2024", "Sardar Azmoun 2023"],
}

def pick_relaxed(query, min_ar=1.3):
    data = api_search(query)
    pages = (data.get("query") or {}).get("pages") or {}
    cands = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [None])[0]
        if not ii: continue
        title = p.get("title", "").lower()
        if any(b in title for b in BAD): continue
        w, h = ii.get("width", 0), ii.get("height", 0)
        if w < 900 or h == 0 or w <= h: continue
        if ii.get("mime") not in ("image/jpeg", "image/png"): continue
        ar = w / h
        if ar < min_ar: continue
        cands.append((ar, ii["thumburl"], p["title"], w, h))
    cands.sort(key=lambda c: abs(c[0] - 1.78))
    return cands[0] if cands else None

out = json.load(open("/tmp/images.json"))
for slug, queries in RETRY.items():
    for q in queries:
        try:
            c = pick_relaxed(q)
        except Exception as e:
            print(f"  err {q}: {e}"); c = None
        if c:
            try:
                data = optimize(c[1]); b64 = base64.b64encode(data).decode()
                out[slug] = {"b64_len": len(b64), "kb": round(len(data)/1024,1),
                             "title": c[2], "thumburl": c[1], "b64": b64}
                print(f"[{slug}] q='{q}' -> {c[2]} ar={c[0]:.2f} {c[3]}x{c[4]} -> {out[slug]['kb']}KB")
            except Exception as e:
                print(f"  optimize err: {e}"); c = None
        if c: break
        time.sleep(2)
    time.sleep(3.5)

json.dump(out, open("/tmp/images.json", "w"))
print("\nFINAL:")
for s, v in out.items():
    print(f"  {s}: {'OK '+str(v['kb'])+'KB '+v['title'] if v else 'MISSING'}")
