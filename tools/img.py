#!/usr/bin/env python3
"""Search Wikimedia Commons for a CC image, download, optimize to a 16:9
landscape JPEG (subject centered, padded if needed) under ~300 KB, and emit base64.

Usage:
  python3 tools/img.py "search terms" OUTPUT_BASENAME [--exclude svg logo]
Writes:
  /tmp/<basename>.jpg          optimized image
  /tmp/<basename>.b64          base64 of the jpg
Prints a JSON line with chosen file title, source page, license, dimensions, kb.
"""
import sys, json, base64, io, time, re
import requests
from PIL import Image, ImageOps

H = {"User-Agent": "WorldCupNewsAgent/1.0 (almaznis1@gmail.com) educational-football-news"}
API = "https://commons.wikimedia.org/w/api.php"


def search_files(query, limit=25):
    r = requests.get(API, params={
        "action": "query", "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}", "gsrnamespace": "6",
        "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1600",
        "format": "json",
    }, headers=H, timeout=40)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    out = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii:
            continue
        meta = ii.get("extmetadata", {})
        lic = (meta.get("LicenseShortName", {}) or {}).get("value", "")
        out.append({
            "title": p.get("title", ""),
            "descurl": ii.get("descriptionurl", ""),
            "thumburl": ii.get("thumburl", ""),
            "url": ii.get("url", ""),
            "w": ii.get("width", 0), "h": ii.get("height", 0),
            "mime": ii.get("mime", ""),
            "license": lic,
        })
    return out


def license_ok(lic):
    l = lic.lower()
    return any(k in l for k in ["cc", "public domain", "pd", "cc0"]) and "non-free" not in l


def fetch(url):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=H, timeout=60)
            if r.status_code == 200 and r.content[:2] == b"\xff\xd8" or (r.status_code == 200 and len(r.content) > 1000):
                return r.content
        except Exception as e:
            sys.stderr.write(f"fetch err {e}\n")
        time.sleep(3)
    return None


def to_169(img):
    img = ImageOps.exif_transpose(img).convert("RGB")
    W, H_ = img.size
    target = 16 / 9
    cur = W / H_
    # We pad (letterbox) to 16:9 so faces are never cropped, subject centered.
    if cur < target:
        new_w = int(round(H_ * target)); new_h = H_
    else:
        new_w = W; new_h = int(round(W / target))
    canvas = Image.new("RGB", (new_w, new_h), (15, 17, 22))
    canvas.paste(img, ((new_w - W) // 2, (new_h - H_) // 2))
    # resize longest side to ~1600
    if canvas.size[0] > 1600:
        ratio = 1600 / canvas.size[0]
        canvas = canvas.resize((1600, int(round(canvas.size[1] * ratio))), Image.LANCZOS)
    return canvas


def encode_under(img, max_kb=300):
    for q in [85, 80, 75, 70, 65, 60, 55, 50]:
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=q, optimize=True)
        kb = len(buf.getvalue()) / 1024
        if kb <= max_kb:
            return buf.getvalue(), q, kb
    return buf.getvalue(), q, kb


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    query, base = args[0], args[1]
    excludes = []
    if "--exclude" in sys.argv:
        i = sys.argv.index("--exclude")
        excludes = [e.lower() for e in sys.argv[i + 1:]]
    cands = search_files(query)
    chosen = None
    for c in cands:
        if c["mime"] == "image/svg+xml":
            continue
        if not license_ok(c["license"]):
            continue
        t = c["title"].lower()
        if any(x in t for x in excludes + ["logo", "icon", "flag", "emblem", "coat of arms", ".svg"]):
            continue
        if c["w"] < 700:
            continue
        chosen = c
        break
    if not chosen:
        print(json.dumps({"ok": False, "reason": "no candidate", "n": len(cands)}))
        return
    data = fetch(chosen["thumburl"] or chosen["url"])
    if not data:
        print(json.dumps({"ok": False, "reason": "download failed", "title": chosen["title"]}))
        return
    img = to_169(Image.open(io.BytesIO(data)))
    jpg, q, kb = encode_under(img)
    with open(f"/tmp/{base}.jpg", "wb") as f:
        f.write(jpg)
    with open(f"/tmp/{base}.b64", "w") as f:
        f.write(base64.b64encode(jpg).decode())
    print(json.dumps({
        "ok": True, "title": chosen["title"], "source": chosen["descurl"],
        "license": chosen["license"], "size": img.size, "kb": round(kb, 1),
        "quality": q, "b64file": f"/tmp/{base}.b64",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
