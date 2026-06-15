#!/usr/bin/env python3
import json, sys, time, io, urllib.parse, urllib.request, os

UA = "WorldCupNewsAgent/1.0 (https://football.kz news bot; contact almaznis1@gmail.com)"
OUT = "/home/user/worldcup-news-editor/build_images"
os.makedirs(OUT, exist_ok=True)

from PIL import Image

# key -> list of candidate Commons search queries (tried in order)
SUBJECTS = {
    "germany_curacao":  ["Kai Havertz 2024", "Jamal Musiala 2023", "Florian Wirtz 2024", "Germany national football team 2024"],
    "netherlands_japan":["Virgil van Dijk 2023", "Virgil van Dijk Netherlands", "Netherlands national football team 2024"],
    "australia_turkiye":["Arda Güler 2024", "Arda Guler Real Madrid", "Hakan Çalhanoğlu 2023", "Turkey national football team 2024"],
    "spain_capeverde":  ["Pedri 2024", "Pedri Spain", "Rodri footballer 2024", "Spain national football team 2024"],
    "belgium_egypt":    ["Mohamed Salah 2024", "Mohamed Salah Liverpool", "Mohamed Salah Egypt"],
    "uzbekistan_colombia":["Eldor Shomurodov 2024", "Eldor Shomurodov Roma", "Eldor Shomurodov", "Uzbekistan national football team"],
    "ranking_top7":     ["SoFi Stadium football", "MetLife Stadium 2023", "AT&T Stadium football", "Mercedes-Benz Stadium Atlanta interior"],
    "portugal_drcongo": ["Cristiano Ronaldo 2024", "Cristiano Ronaldo Portugal 2023", "Cristiano Ronaldo Al Nassr"],
}

def api_search(query):
    params = {
        "action":"query","format":"json","generator":"search",
        "gsrsearch": f'filetype:bitmap {query}',
        "gsrnamespace":"6","gsrlimit":"15",
        "prop":"imageinfo","iiprop":"url|size|mime|extmetadata","iiurlwidth":"1600",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent":UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)

def is_free(ext):
    lic = (ext.get("LicenseShortName",{}) or {}).get("value","")
    licu = lic.lower()
    if any(k in licu for k in ["cc0","public domain","cc by","cc-by","pdm"]):
        return True, lic
    # also accept generic "Creative Commons"
    if "creative commons" in licu:
        return True, lic
    return False, lic

def pick(query):
    data = api_search(query)
    pages = (data.get("query",{}) or {}).get("pages",{})
    cands = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii: continue
        mime = ii.get("mime","")
        if mime not in ("image/jpeg","image/png"): continue
        w,h = ii.get("width",0), ii.get("height",0)
        if w < 900 or h < 500: continue
        if w <= h:  # require landscape
            continue
        free, lic = is_free(ii.get("extmetadata",{}) or {})
        if not free: continue
        thumb = ii.get("thumburl") or ii.get("url")
        cands.append({"title":p.get("title"),"w":w,"h":h,"thumb":thumb,
                      "desc":ii.get("descriptionurl"),"lic":lic})
    # prefer aspect ratio closest to 16:9 and decent width
    def score(c):
        ar = c["w"]/c["h"]
        return abs(ar-1.777)
    cands.sort(key=score)
    return cands

def process(thumb_url, out_path):
    req = urllib.request.Request(thumb_url, headers={"User-Agent":UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    TW, TH = 1600, 900
    # cover-crop to 16:9, centered
    src_ar = im.width/im.height
    tgt_ar = TW/TH
    if src_ar > tgt_ar:
        # too wide -> scale by height, crop width
        nh = TH; nw = round(im.width * TH/im.height)
        im2 = im.resize((nw,nh), Image.LANCZOS)
        left = (nw-TW)//2
        im2 = im2.crop((left,0,left+TW,TH))
    else:
        # taller/narrower -> scale by width, crop height (center)
        nw = TW; nh = round(im.height * TW/im.width)
        im2 = im.resize((nw,nh), Image.LANCZOS)
        top = (nh-TH)//2
        im2 = im2.crop((0,top,TW,top+TH))
    # compress under 300KB
    q = 85
    while q >= 55:
        buf = io.BytesIO()
        im2.save(buf, "JPEG", quality=q, optimize=True)
        if buf.tell() <= 300*1024:
            break
        q -= 5
    with open(out_path,"wb") as f:
        f.write(buf.getvalue())
    return len(buf.getvalue()), q, im2.size

results = {}
for key, queries in SUBJECTS.items():
    chosen = None
    for q in queries:
        try:
            cands = pick(q)
        except Exception as e:
            print(f"[{key}] query '{q}' API error: {e}", flush=True)
            time.sleep(3); continue
        if cands:
            for c in cands[:4]:
                try:
                    out = os.path.join(OUT, key+".jpg")
                    size, qual, dim = process(c["thumb"], out)
                    chosen = {"key":key,"query":q,"file":c["title"],"page":c["desc"],
                              "lic":c["lic"],"bytes":size,"quality":qual,"dim":dim,"out":out}
                    print(f"[{key}] OK <- '{q}' :: {c['title']} | {c['lic']} | {size//1024}KB q{qual} {dim}", flush=True)
                    break
                except Exception as e:
                    print(f"[{key}] process fail {c['title']}: {e}", flush=True)
                    time.sleep(3)
            if chosen: break
        time.sleep(3)
    if not chosen:
        print(f"[{key}] !!! NO IMAGE FOUND", flush=True)
    else:
        results[key]=chosen
    time.sleep(3)

with open(os.path.join(OUT,"_manifest.json"),"w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\n=== DONE ===", len(results), "images")
