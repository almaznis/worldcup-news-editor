#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch a Wikimedia Commons image by file title, compose a 16:9 cover
(blurred cover background + contained, face-centered foreground), optimize to
JPEG under ~300KB, return base64. Also exposes a CLI for quick validation."""
import base64, io, json, sys, time, urllib.parse, urllib.request
from PIL import Image, ImageFilter

UA = "WorldCupNewsAgent/1.0 (football news editor; contact almaznis1@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"

def _get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if binary else r.read().decode("utf-8")

def thumb_url(file_title, width=1600):
    """Return (thumburl, descurl, width, height, mime) for a Commons file."""
    params = {
        "action": "query", "format": "json", "prop": "imageinfo",
        "titles": f"File:{file_title}", "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": str(width),
    }
    data = json.loads(_get(API + "?" + urllib.parse.urlencode(params)))
    pages = data["query"]["pages"]
    for _, page in pages.items():
        if "imageinfo" not in page:
            return None
        ii = page["imageinfo"][0]
        meta = ii.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "?")
        return {
            "thumburl": ii.get("thumburl"), "descurl": ii.get("descriptionurl"),
            "width": ii.get("thumbwidth"), "height": ii.get("thumbheight"),
            "mime": ii.get("mime"), "license": lic,
        }
    return None

def compose_cover(img_bytes, out_w=1600, out_h=900, quality=82, max_kb=300):
    src = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    sw, sh = src.size
    target_ar = out_w / out_h
    # Blurred background: cover the whole canvas
    bg_scale = max(out_w / sw, out_h / sh)
    bg = src.resize((max(1, int(sw * bg_scale)), max(1, int(sh * bg_scale))), Image.LANCZOS)
    bx = (bg.width - out_w) // 2
    by = (bg.height - out_h) // 2
    bg = bg.crop((bx, by, bx + out_w, by + out_h)).filter(ImageFilter.GaussianBlur(28))
    # darken background slightly
    bg = Image.blend(bg, Image.new("RGB", bg.size, (20, 22, 28)), 0.28)
    # Foreground: contain within canvas with headroom margin (95%)
    margin = 0.96
    fg_scale = min((out_w * margin) / sw, (out_h * margin) / sh)
    fw, fh = max(1, int(sw * fg_scale)), max(1, int(sh * fg_scale))
    fg = src.resize((fw, fh), Image.LANCZOS)
    ox = (out_w - fw) // 2
    oy = (out_h - fh) // 2
    bg.paste(fg, (ox, oy))
    canvas = bg
    # encode, reduce quality until under max_kb
    q = quality
    while True:
        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=q, optimize=True)
        kb = buf.tell() / 1024
        if kb <= max_kb or q <= 50:
            break
        q -= 6
    return base64.b64encode(buf.getvalue()).decode("ascii"), kb, q, canvas.size

def fetch_b64(file_title, width=1600):
    info = thumb_url(file_title, width)
    if not info or not info["thumburl"]:
        return None
    raw = _get(info["thumburl"], binary=True)
    b64, kb, q, size = compose_cover(raw)
    return {"b64": b64, "kb": round(kb, 1), "q": q, "size": size,
            "license": info["license"], "descurl": info["descurl"],
            "src_size": (info["width"], info["height"])}

if __name__ == "__main__":
    # quick test
    for t in sys.argv[1:]:
        r = fetch_b64(t)
        if r:
            print(f"OK  {t} -> {r['kb']}KB q{r['q']} {r['size']} lic={r['license']} src={r['src_size']}")
            print(f"    desc={r['descurl']}")
        else:
            print(f"FAIL {t}")
        time.sleep(3.5)
