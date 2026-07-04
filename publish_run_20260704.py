#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publish run for 2026-07-04 (World Cup 2026 Round of 16 opening day).
Downloads Wikimedia portrait/landscape photos, letterboxes them onto a 16:9
canvas (subject centered, no face crop), compresses to JPEG, base64-encodes,
and POSTs all 8 articles to the Sport Arena Hub publish endpoint.
"""
import base64
import io
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests
from PIL import Image, ImageOps

ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
SECRET = os.environ.get("AGENT_PUBLISH_SECRET")
RUN_ID = "run-20260704-r16opening"
GENERATED_AT = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

UA = {"User-Agent": "SportArenaHubBot/1.0 (editorial; contact almaznis1@gmail.com)"}


def make_cover_b64(url, target=(1600, 900)):
    """Download an image and letterbox it onto a 16:9 canvas, subject centered.
    Returns base64 JPEG string (< ~300KB) or None on failure."""
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=30)
            if r.status_code == 429:
                time.sleep(4 * (attempt + 1))
                continue
            r.raise_for_status()
            src = Image.open(io.BytesIO(r.content))
            src = ImageOps.exif_transpose(src).convert("RGB")
            tw, th = target
            # Scale to fit fully inside the canvas (no cropping of the subject).
            scale = min(tw / src.width, th / src.height)
            nw, nh = max(1, int(src.width * scale)), max(1, int(src.height * scale))
            resized = src.resize((nw, nh), Image.LANCZOS)
            # Sample a background colour from the image edges for the letterbox.
            bg = resized.resize((1, 1)).getpixel((0, 0))
            canvas = Image.new("RGB", target, bg)
            canvas.paste(resized, ((tw - nw) // 2, (th - nh) // 2))
            for q in (82, 75, 68, 60):
                buf = io.BytesIO()
                canvas.save(buf, "JPEG", quality=q, optimize=True)
                data = buf.getvalue()
                if len(data) <= 300_000:
                    print(f"  cover {url.split('/')[-1]} -> {len(data)//1024}KB q{q}")
                    return base64.b64encode(data).decode()
            print(f"  cover {url.split('/')[-1]} -> {len(data)//1024}KB (q60, over target but ok)")
            return base64.b64encode(data).decode()
        except Exception as e:
            print(f"  [warn] image attempt {attempt+1} failed for {url}: {e}")
            time.sleep(2 * (attempt + 1))
    return None


from articles_data import ARTICLES

CATS = {"ЧМ-2026", "Сборные", "Отчёты о матчах", "Новости игроков", "Тренды"}
TYPES = {"transfer", "preview", "match_report", "ranking"}


def validate():
    assert len(ARTICLES) == 8, f"expected 8 articles, got {len(ARTICLES)}"
    news = [a for a in ARTICLES if a["source_type"] == "news"]
    trend = [a for a in ARTICLES if a["source_type"] == "trend"]
    assert len(news) == 5, f"expected 5 news, got {len(news)}"
    assert len(trend) == 3, f"expected 3 trend, got {len(trend)}"
    slugs = [a["slug"] for a in ARTICLES]
    assert len(set(slugs)) == 8, "duplicate slugs"
    problems = []
    for a in ARTICLES:
        for f in ("title", "slug", "body", "excerpt", "category", "type"):
            if not a.get(f):
                problems.append(f"{a['slug']}: empty {f}")
        if a["category"] not in CATS:
            problems.append(f"{a['slug']}: bad category {a['category']}")
        if a["type"] not in TYPES:
            problems.append(f"{a['slug']}: bad type {a['type']}")
        if not a.get("sources"):
            problems.append(f"{a['slug']}: empty sources")
        for field in ("title", "excerpt", "body"):
            if "—" in a[field]:
                problems.append(f"{a['slug']}: em dash in {field}")
    types_used = [a["type"] for a in ARTICLES]
    print("types:", {t: types_used.count(t) for t in TYPES})
    if problems:
        print("VALIDATION PROBLEMS:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print(f"validation OK: 8 articles ({len(news)} news / {len(trend)} trend), slugs unique")


def main():
    dry = "--dry-run" in sys.argv
    validate()
    if not SECRET and not dry:
        print("FATAL: AGENT_PUBLISH_SECRET missing")
        sys.exit(1)
    # Attach covers (use disk cache from a prior run if present).
    import pathlib
    cached = {}
    cf = pathlib.Path("scratch_covers.json")
    if cf.exists():
        cached = json.loads(cf.read_text())
    for a in ARTICLES:
        cov = a.pop("_cover_url", None)
        if cached.get(a["slug"]):
            a["image_base64"] = cached[a["slug"]]
        elif cov and not a.get("image_base64"):
            a["image_base64"] = make_cover_b64(cov)
            time.sleep(3.5)  # Wikimedia rate-limit courtesy
        if not a.get("image_base64") and not a.get("image_url"):
            print(f"  [ERROR] no cover for {a['slug']}")

    covered = sum(1 for a in ARTICLES if a.get("image_base64") or a.get("image_url"))
    print(f"covers ready: {covered}/8")
    if dry:
        print("DRY RUN — not posting. Payload sizes:")
        for a in ARTICLES:
            b = a.get("image_base64")
            print(f"  {a['slug']}: img_b64={'yes '+str(len(b)//1024)+'KB' if b else 'NO'}, body={len(a['body'])} chars")
        return None

    # Cache covers to disk so retries don't re-download.
    import pathlib
    cache = pathlib.Path("scratch_covers.json")
    cache.write_text(json.dumps({a["slug"]: a.get("image_base64") for a in ARTICLES}))

    headers = {"Content-Type": "application/json", "x-agent-secret": SECRET}
    batch_size = int(os.environ.get("BATCH_SIZE", "1"))
    all_results = {}
    for i in range(0, len(ARTICLES), batch_size):
        chunk = ARTICLES[i:i + batch_size]
        slugs = [a["slug"] for a in chunk]
        for attempt in range(4):
            try:
                resp = requests.post(ENDPOINT, headers=headers,
                                     json={"articles": chunk}, timeout=120)
                print(f"batch {slugs} -> HTTP {resp.status_code}")
                if resp.status_code == 200:
                    for r in resp.json().get("results", []):
                        all_results[r.get("slug")] = r
                        print("   ", r.get("slug"), r.get("status"), r.get("error") or "")
                    break
                else:
                    print("   ", resp.text[:500])
                    time.sleep(2 * (attempt + 1))
            except Exception as e:
                print(f"   [warn] attempt {attempt+1}: {e}")
                time.sleep(2 * (attempt + 1))
        time.sleep(1)

    # Persist results for logging step.
    pathlib.Path("scratch_results.json").write_text(json.dumps(all_results, ensure_ascii=False, indent=2))
    inserted = [s for s, r in all_results.items() if r.get("status") == "inserted"]
    print(f"\nINSERTED {len(inserted)}/{len(ARTICLES)}")
    return all_results


if __name__ == "__main__":
    main()
