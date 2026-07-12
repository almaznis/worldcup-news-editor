#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Image helper: download a Wikimedia (or other) photo, fit it onto a 1600x900
16:9 canvas with a blurred cover background so the subject's face is never
cropped by the site's center-crop, re-encode as optimized JPEG (<~300KB),
and return base64. Reusable by the publish script."""
import base64, io, urllib.request
from PIL import Image, ImageFilter

TARGET_W, TARGET_H = 1600, 900  # 16:9


def fetch(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "WorldCupNewsAgent/1.0 (editorial; contact almaznis1@gmail.com)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def make_16x9_b64(url: str, quality: int = 82) -> tuple[str | None, int]:
    """Return (base64_jpeg, final_kb) or (None, 0) on failure."""
    try:
        raw = fetch(url)
        im = Image.open(io.BytesIO(raw))
        im = im.convert("RGB")
        sw, sh = im.size

        # Blurred cover background filling the whole 16:9 canvas
        scale_bg = max(TARGET_W / sw, TARGET_H / sh)
        bg = im.resize((max(1, int(sw * scale_bg)), max(1, int(sh * scale_bg))), Image.LANCZOS)
        bx = (bg.width - TARGET_W) // 2
        by = (bg.height - TARGET_H) // 2
        bg = bg.crop((bx, by, bx + TARGET_W, by + TARGET_H))
        bg = bg.filter(ImageFilter.GaussianBlur(28))
        # darken background slightly for contrast
        bg = Image.eval(bg, lambda p: int(p * 0.82))

        # Foreground: contain the full image (no crop) centered, with margin
        margin = 0.92  # leave a little headroom/margin around subject
        scale_fg = min(TARGET_W / sw, TARGET_H / sh) * margin
        fg = im.resize((max(1, int(sw * scale_fg)), max(1, int(sh * scale_fg))), Image.LANCZOS)
        fx = (TARGET_W - fg.width) // 2
        fy = (TARGET_H - fg.height) // 2
        bg.paste(fg, (fx, fy))

        out = io.BytesIO()
        q = quality
        bg.save(out, format="JPEG", quality=q, optimize=True)
        # dial down quality until under ~300KB
        while out.tell() > 300 * 1024 and q > 55:
            q -= 6
            out = io.BytesIO()
            bg.save(out, format="JPEG", quality=q, optimize=True)
        data = out.getvalue()
        return base64.b64encode(data).decode("ascii"), len(data) // 1024
    except Exception as exc:
        print(f"  imgutil FAIL {url.split('/')[-1]}: {exc}")
        return None, 0


if __name__ == "__main__":
    import sys
    b64, kb = make_16x9_b64(sys.argv[1])
    print("OK" if b64 else "FAIL", kb, "KB")
