#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image helper: download a photo, normalize it to a sharp landscape 16:9 cover
(so the on-site center crop never cuts off faces), re-encode as optimized JPEG
(<~300 KB), and return a base64 string ready for the publish endpoint's
image_base64 field.
"""
import base64, io, time, urllib.request

from PIL import Image, ImageFilter, ImageOps

UA = {"User-Agent": "WorldCupNewsAgent/1.0 (editorial; contact almaznis1@gmail.com)"}

TARGET_W, TARGET_H = 1600, 900  # 16:9


def _fetch(url: str, retries: int = 3) -> bytes | None:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except Exception as exc:
            print(f"    ! fetch attempt {attempt+1} failed for {url.split('/')[-1]}: {exc}")
            time.sleep(3 + attempt * 2)
    return None


def to_cover_base64(url: str, retries: int = 3) -> tuple[str | None, int]:
    """Return (base64_jpeg, kb_size) for a 16:9 landscape cover, or (None, 0)."""
    raw = _fetch(url, retries)
    if not raw:
        return None, 0
    try:
        im = Image.open(io.BytesIO(raw))
        im = ImageOps.exif_transpose(im)  # honor + strip EXIF orientation
        im = im.convert("RGB")
    except Exception as exc:
        print(f"    ! decode failed: {exc}")
        return None, 0

    w, h = im.size
    src_ratio = w / h
    tgt_ratio = TARGET_W / TARGET_H

    if abs(src_ratio - tgt_ratio) < 0.02:
        canvas = im.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    elif src_ratio > tgt_ratio:
        # wider than 16:9 -> fit width would overflow height; contain by height then
        # letterbox left/right on a blurred fill
        canvas = _contain_on_blur(im)
    else:
        # taller than 16:9 (portrait) -> contain, pillarbox on blurred fill so the
        # whole face stays visible after center crop
        canvas = _contain_on_blur(im)

    buf = io.BytesIO()
    q = 85
    canvas.save(buf, format="JPEG", quality=q, optimize=True, progressive=True)
    while buf.tell() > 300 * 1024 and q > 55:
        q -= 8
        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=q, optimize=True, progressive=True)
    data = buf.getvalue()
    b64 = base64.b64encode(data).decode("ascii")
    print(f"    ✓ cover {w}x{h} -> 1600x900 q{q} {len(data)//1024} KB")
    return b64, len(data) // 1024


def _contain_on_blur(im: Image.Image) -> Image.Image:
    """Place the whole image, centered, on a 1600x900 blurred-cover background."""
    # blurred background that fully covers the 16:9 canvas
    bg = ImageOps.fit(im, (TARGET_W, TARGET_H), Image.LANCZOS, centering=(0.5, 0.4))
    bg = bg.filter(ImageFilter.GaussianBlur(28))
    # darken slightly for contrast
    bg = Image.blend(bg, Image.new("RGB", bg.size, (18, 20, 24)), 0.28)

    # foreground: contain the full image within the canvas
    fg = im.copy()
    fg.thumbnail((TARGET_W, TARGET_H), Image.LANCZOS)
    fw, fh = fg.size
    x = (TARGET_W - fw) // 2
    y = (TARGET_H - fh) // 2
    bg.paste(fg, (x, y))
    return bg


if __name__ == "__main__":
    import sys
    b64, kb = to_cover_base64(sys.argv[1])
    print("OK" if b64 else "FAIL", kb, "KB")
