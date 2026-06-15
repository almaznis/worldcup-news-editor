#!/usr/bin/env python3
"""Fetch a Wikimedia Commons photo and turn it into a clean 16:9 hero cover.

Usage: coverimg.py OUTBASE "File:Title one.jpg" ["File:Alt two.jpg" ...]
- Queries Commons API for each candidate, picks the first raster image whose
  ORIGINAL width is large enough for a sharp hero.
- Builds a 1600x900 canvas: blurred/darkened cover background + the full photo
  contained & centered (so faces are never cropped), JPEG q82, EXIF stripped.
- Writes <OUTBASE>.b64 (base64 of the jpeg) and prints license + size info.
"""
import sys, io, json, base64, urllib.parse, urllib.request

from PIL import Image, ImageFilter, ImageEnhance, ImageOps

UA = "WorldCupNewsAgent/1.0 (almaznis1@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read()

def imageinfo(title):
    q = {
        "action": "query", "format": "json", "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1600",
        "titles": title,
    }
    data = json.loads(get(API + "?" + urllib.parse.urlencode(q)))
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "imageinfo" not in page:
        return None
    return page["imageinfo"][0]

def build(outbase, candidates):
    chosen = None
    for title in candidates:
        try:
            ii = imageinfo(title)
        except Exception as e:
            print("  ! error %s: %s" % (title, e)); continue
        if not ii:
            print("  - missing: %s" % title); continue
        if not ii.get("mime", "").startswith("image/") or "svg" in ii.get("mime", ""):
            print("  - not raster: %s (%s)" % (title, ii.get("mime"))); continue
        w, h = ii.get("width", 0), ii.get("height", 0)
        if w < 600:
            print("  - too small (%sx%s): %s" % (w, h, title)); continue
        chosen = (title, ii); break
    if not chosen:
        print("FAILED: no usable candidate"); sys.exit(2)
    title, ii = chosen
    lic = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "?")
    artist = ii.get("extmetadata", {}).get("Artist", {}).get("value", "?")
    src_url = ii.get("thumburl") or ii.get("url")
    raw = get(src_url)
    im = Image.open(io.BytesIO(raw))
    im = ImageOps.exif_transpose(im).convert("RGB")

    CW, CH = 1600, 900
    # blurred cover background
    bg = ImageOps.fit(im, (CW, CH), method=Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(28))
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    # foreground contained, centered, with margin so face has headroom
    fg = im.copy()
    fg.thumbnail((int(CW * 0.62), int(CH * 0.92)), Image.LANCZOS)
    canvas = bg.copy()
    x = (CW - fg.width) // 2
    y = (CH - fg.height) // 2
    canvas.paste(fg, (x, y))

    out = io.BytesIO()
    canvas.save(out, format="JPEG", quality=82, optimize=True)
    data = out.getvalue()
    b64 = base64.b64encode(data).decode()
    with open(outbase + ".b64", "w") as f:
        f.write(b64)
    # strip html tags from artist for readability
    import re
    artist_txt = re.sub("<[^>]+>", "", artist)[:120]
    print("OK  %s" % title)
    print("    license: %s | artist: %s" % (lic, artist_txt))
    print("    src %sx%s -> hero 1600x900 | jpeg %d KB | b64 -> %s.b64" % (
        ii.get("width"), ii.get("height"), len(data)//1024, outbase))

if __name__ == "__main__":
    outbase = sys.argv[1]
    cands = sys.argv[2:]
    build(outbase, cands)
