#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch a real lead photo for a subject via the Wikipedia/Wikimedia API,
letterbox/pad it onto a 16:9 canvas (subject centered, blurred fill) so a
center-crop never chops the face, optimize to JPEG < ~300 KB, return base64.
"""
import base64, io, json, time, urllib.parse, urllib.request
from PIL import Image, ImageFilter

UA = {"User-Agent": "WorldCupNewsAgent/1.0 (editorial; contact almaznis1@gmail.com)"}


def _get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def wiki_image_url(title, lang="en"):
    """Return the original lead-image URL for a Wikipedia page title, or None."""
    api = (f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json"
           f"&prop=pageimages&piprop=original&redirects=1&titles="
           + urllib.parse.quote(title))
    try:
        data = json.loads(_get(api).decode())
        pages = data.get("query", {}).get("pages", {})
        for _, p in pages.items():
            orig = p.get("original", {}).get("source")
            if orig:
                return orig
    except Exception as e:
        print(f"    api error {title}: {e}")
    return None


def to_169_b64(img_bytes, target_w=1600, target_h=900, quality=82):
    src = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    # blurred cover background filling the whole 16:9 canvas
    bg = src.copy()
    scale = max(target_w / bg.width, target_h / bg.height)
    bg = bg.resize((int(bg.width * scale) + 1, int(bg.height * scale) + 1), Image.LANCZOS)
    left = (bg.width - target_w) // 2
    top = (bg.height - target_h) // 2
    bg = bg.crop((left, top, left + target_w, top + target_h)).filter(ImageFilter.GaussianBlur(28))
    # foreground: contain the full image, centered, with headroom margin
    fg = src.copy()
    margin = 0.90  # leave a margin so face is well inside frame
    fscale = min(target_w * margin / fg.width, target_h * margin / fg.height)
    fw, fh = max(1, int(fg.width * fscale)), max(1, int(fg.height * fscale))
    fg = fg.resize((fw, fh), Image.LANCZOS)
    canvas = bg.copy()
    canvas.paste(fg, ((target_w - fw) // 2, (target_h - fh) // 2))
    # encode under size budget
    for q in (quality, 74, 66, 58):
        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=q, optimize=True)
        b = buf.getvalue()
        if len(b) <= 300 * 1024:
            return base64.b64encode(b).decode("ascii"), len(b)
    return base64.b64encode(b).decode("ascii"), len(b)


def fetch(title, lang="en"):
    url = wiki_image_url(title, lang)
    if not url:
        return None, None, None
    try:
        raw = _get(url)
        b64, size = to_169_b64(raw)
        return b64, size, url
    except Exception as e:
        print(f"    download/process error {title}: {e}")
        return None, None, url


if __name__ == "__main__":
    # subject -> list of candidate Wikipedia titles (first that resolves wins)
    SUBJECTS = {
        "cunha":     ["Matheus Cunha"],
        "saibari":   ["Ismael Saibari", "Brahim Díaz"],
        "almiron":   ["Miguel Almirón"],
        "pulisic":   ["Christian Pulisic", "Folarin Balogun"],
        "havertz":   ["Kai Havertz", "Jamal Musiala"],
        "khusanov":  ["Abdukodir Khusanov", "Eldor Shomurodov"],
        "messi":     ["Lionel Messi"],
        "yamal":     ["Lamine Yamal"],
    }
    for key, titles in SUBJECTS.items():
        got = False
        for t in titles:
            url = wiki_image_url(t)
            print(f"{key:10s} <- {t:25s} : {url}")
            if url:
                got = True
                break
            time.sleep(0.5)
        if not got:
            print(f"  !! no image for {key}")
        time.sleep(0.4)
