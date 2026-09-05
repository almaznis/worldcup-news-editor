# -*- coding: utf-8 -*-
import requests, json, time
API="https://commons.wikimedia.org/w/api.php"
HEAD={"User-Agent":"WorldCupNewsAgent/1.0 (editorial; contact almaznis1@gmail.com)"}
covers={
 "enzo":"Enzo_Fernandez_Julian_Alvarez_Argentina_v_Egypt_7_July_2026-116.jpg",
 "ucl":"Santiago_Bernabéu_Stadium,_2007.jpg",
 "baleba":"Carlos_Baleba_24012026_(3).jpg",
 "ranking":"Morgan_Rogers_England_v_Panama_27_June_26-106.jpg",
 "diomande":"Yan_Diomande_Piero_Hincapie_Cote_D'Ivoire_v_Ecuador_14_June_2026-126.jpg",
 "kairat":"FC_Red_Bull_Salzburg_(U19)_gegen_FC_Kairat_Almaty_(U46).jpg",
 "ballon":"Ferran_Torres_Argentina_v_Spain_19_July_2026-233.jpg",
 "kaznt":"Astana_Arena_2013-10-24_21.46.10.JPG",
}
inline={
 "enzo":"Argentina_vs_mexico_enzofernandez_vs_hectormoreno.jpg",
 "anderson":"Elliot_Anderson_England_v_Ghana_23_June_2026-059.jpg",
 "barcola":"Bradley_Barcola_France_v_Spain_7.24.26-079.jpg",
 "diomande":"Yan_Diomande_Cote_D'Ivoire_v_Ecuador_14_June_2026-17_(cropped).jpg",
 "tonali":"Tonali_Milan_Newcastle.jpg",
}
def get(files, width):
    titles="|".join("File:"+f for f in files)
    for att in range(5):
        r=requests.get(API,params={"action":"query","format":"json","titles":titles,
            "prop":"imageinfo","iiprop":"url|size","iiurlwidth":str(width)},headers=HEAD,timeout=40)
        if r.status_code==429: time.sleep(6*(att+1)); continue
        d=r.json(); pages=d.get("query",{}).get("pages",{})
        out={}
        for p in pages.values():
            t=p.get("title","").replace("File:","").replace(" ","_")
            ii=(p.get("imageinfo") or [{}])[0]
            out[t]=ii.get("thumburl")
        return out
    return {}
cov=get(list(covers.values()),1280)
time.sleep(4)
inl=get(list(inline.values()),1000)
res={"covers":{},"inline":{}}
for k,f in covers.items():
    res["covers"][k]=cov.get(f)
    print("COVER",k,"->",cov.get(f))
for k,f in inline.items():
    res["inline"][k]=inl.get(f)
    print("INLINE",k,"->",inl.get(f))
json.dump(res,open("thumb_urls.json","w"))
missing=[k for k,v in res["covers"].items() if not v]
print("MISSING COVERS:",missing)
