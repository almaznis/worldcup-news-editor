#!/usr/bin/env python3
import json, time, io, urllib.parse, urllib.request, os
from PIL import Image, ImageFilter

UA = "WorldCupNewsAgent/1.0 (https://football.kz news bot; contact almaznis1@gmail.com)"
OUT = "/home/user/worldcup-news-editor/build_images"
os.makedirs(OUT, exist_ok=True)

# key -> list of English Wikipedia article titles (lead image = guaranteed subject)
SUBJECTS = {
    "germany_curacao":     ["Kai Havertz", "Jamal Musiala", "Florian Wirtz"],
    "australia_turkiye":   ["Arda Güler", "Kenan Yıldız", "Hakan Çalhanoğlu"],
    "spain_capeverde":     ["Lamine Yamal", "Pedri", "Mikel Oyarzabal"],
    "belgium_egypt":       ["Mohamed Salah"],
    "uzbekistan_colombia": ["Eldor Shomurodov", "Abdukodir Khusanov"],
    "portugal_drcongo":    ["Cristiano Ronaldo"],
    "ranking_top7":        ["MetLife Stadium", "SoFi Stadium", "AT&T Stadium"],
}

def jget(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)

def wiki_pageimage_file(title):
    p = {"action":"query","format":"json","titles":title,"prop":"pageimages","piprop":"name"}
    d = jget("https://en.wikipedia.org/w/api.php?"+urllib.parse.urlencode(p))
    pages = d.get("query",{}).get("pages",{})
    for pg in pages.values():
        name = pg.get("pageimage")
        if name:
            return "File:"+name
    return None

def commons_imageinfo(filetitle):
    p = {"action":"query","format":"json","titles":filetitle,"prop":"imageinfo",
         "iiprop":"url|size|mime|extmetadata","iiurlwidth":"1600"}
    d = jget("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(p))
    pages = d.get("query",{}).get("pages",{})
    for pg in pages.values():
        ii = (pg.get("imageinfo") or [None])[0]
        if ii: return ii
    return None

def is_free(ext):
    lic = (ext.get("LicenseShortName",{}) or {}).get("value","")
    l = lic.lower()
    ok = any(k in l for k in ["cc0","public domain","cc by","cc-by","pdm","creative commons"])
    return ok, lic

def process(raw, out_path):
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    TW, TH = 1600, 900
    ar = im.width/im.height
    if ar >= 1.55:
        # landscape: cover-crop centered to 16:9
        nh = TH; nw = round(im.width*TH/im.height)
        r = im.resize((nw,nh), Image.LANCZOS)
        left = (nw-TW)//2
        canvas = r.crop((left,0,left+TW,TH))
    else:
        # portrait/squarish: blurred cover background + sharp fit-to-height foreground
        # background: cover the canvas, blurred
        if ar > TW/TH:
            bh = TH; bw = round(im.width*TH/im.height)
        else:
            bw = TW; bh = round(im.height*TW/im.width)
        bg = im.resize((bw,bh), Image.LANCZOS)
        bx, by = (bw-TW)//2, (bh-TH)//2
        bg = bg.crop((bx,by,bx+TW,by+TH)).filter(ImageFilter.GaussianBlur(28))
        # darken bg slightly
        from PIL import ImageEnhance
        bg = ImageEnhance.Brightness(bg).enhance(0.78)
        # foreground: fit to height 900 (with small margin)
        fh = 880; fw = round(im.width*fh/im.height)
        if fw > TW:  # too wide even at full height (shouldn't for portrait) -> fit width
            fw = TW-40; fh = round(im.height*fw/im.width)
        fg = im.resize((fw,fh), Image.LANCZOS)
        canvas = bg.copy()
        canvas.paste(fg, ((TW-fw)//2, (TH-fh)//2))
    q = 85
    while q >= 55:
        buf = io.BytesIO()
        canvas.save(buf, "JPEG", quality=q, optimize=True)
        if buf.tell() <= 300*1024: break
        q -= 5
    with open(out_path,"wb") as f:
        f.write(buf.getvalue())
    return len(buf.getvalue()), q, ar

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

results = {}
for key, titles in SUBJECTS.items():
    done = False
    for title in titles:
        try:
            ft = wiki_pageimage_file(title)
            if not ft:
                print(f"[{key}] no pageimage for '{title}'"); time.sleep(2); continue
            ii = commons_imageinfo(ft)
            if not ii:
                print(f"[{key}] no imageinfo for {ft}"); time.sleep(2); continue
            free, lic = is_free(ii.get("extmetadata",{}) or {})
            if not free:
                print(f"[{key}] '{title}' not free ({lic}) -> skip"); time.sleep(2); continue
            if ii.get("mime") not in ("image/jpeg","image/png"):
                print(f"[{key}] '{title}' mime {ii.get('mime')} skip"); time.sleep(2); continue
            src = ii.get("thumburl") or ii.get("url")
            raw = fetch(src)
            out = os.path.join(OUT, key+".jpg")
            size,q,ar = process(raw, out)
            results[key] = {"title":title,"file":ft,"page":ii.get("descriptionurl"),
                            "lic":lic,"bytes":size,"quality":q,"src_ar":round(ar,3)}
            print(f"[{key}] OK <- {title} :: {ft} | {lic} | {size//1024}KB q{q} ar{ar:.2f}")
            done = True
            time.sleep(3)
            break
        except Exception as e:
            print(f"[{key}] '{title}' error: {e}"); time.sleep(3)
    if not done:
        print(f"[{key}] !!! FAILED")
    time.sleep(2)

# merge with existing manifest (keep netherlands_japan from v1)
mpath = os.path.join(OUT,"_manifest_v2.json")
with open(mpath,"w") as f:
    json.dump(results,f,ensure_ascii=False,indent=2)
print("\n=== DONE v2 ===", len(results))
