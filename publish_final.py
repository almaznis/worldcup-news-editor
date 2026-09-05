# -*- coding: utf-8 -*-
"""Final publish: expanded Russian bodies + public landscape image_url covers
(fallback, since the Wikimedia image CDN blocks this IP). Logs + archives."""
import json, os, re, time, datetime, urllib.parse
import requests
import articles_content as AC

REPO = "/home/user/worldcup-news-editor"
RUN_ID = "run-20260905-kz-sept-window-v2"
GENERATED_AT = "2026-09-05T09:30:00Z"
ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
SECRET = os.environ["AGENT_PUBLISH_SECRET"]

def clean(u):
    if not u:
        return u
    u = u.split("?")[0]  # drop tracking query params
    return u.replace("https://thumb.wikimedia.org/", "https://upload.wikimedia.org/")

_TU = json.load(open("thumb_urls.json"))
COVER_URL = {k: clean(v) for k, v in _TU["covers"].items()}
INLINE = {k: clean(v) for k, v in _TU["inline"].items()}

def main():
    os.makedirs(f"{REPO}/logs", exist_ok=True)
    AC.INLINE = INLINE
    a4 = AC.build_a4()

    arts = AC.get_articles()
    for a in arts:
        if a["key"] == "ranking":
            a["body"] = a4
        a["image_url"] = COVER_URL[a["key"]]
        a["image_base64"] = None

    def pub_obj(a):
        return {"title": a["title"], "slug": a["slug"], "body": a["body"],
                "excerpt": a["excerpt"], "category": a["category"], "type": a["type"],
                "image_url": a["image_url"], "image_base64": None,
                "sources": a["sources"], "source_type": a["source_type"]}

    payload = [pub_obj(a) for a in arts]
    # audit manifest
    json.dump({"generated_at": GENERATED_AT, "run_id": RUN_ID, "articles": payload},
              open(f"{REPO}/logs/manifest-{RUN_ID}.json", "w"), ensure_ascii=False, indent=2)

    def post(objs):
        r = requests.post(ENDPOINT, headers={"Content-Type": "application/json",
                          "x-agent-secret": SECRET}, data=json.dumps({"articles": objs}), timeout=200)
        print("HTTP", r.status_code)
        try:
            return r.status_code, r.json()
        except Exception:
            print(r.text[:600]); return r.status_code, None

    print("Publishing 8 (with covers + expanded bodies)…")
    st, resp = post(payload)
    if st == 401:
        print("401 – secret problem. STOP."); return
    results = (resp or {}).get("results", [])
    by = {r.get("slug"): r for r in results}

    # retry any error / missing
    errs = [a for a in arts if by.get(a["slug"], {}).get("status") == "error" or a["slug"] not in by]
    # note: successful inserts return an appended slug (-2), so match by order for missing base slugs
    if errs:
        print("Retrying", len(errs)); time.sleep(3)
        _, r2 = post([pub_obj(a) for a in errs])
        for i, r in enumerate((r2 or {}).get("results", [])):
            errs_slug = errs[i]["slug"]
            by[errs_slug] = r

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    inserted = 0
    with open(f"{REPO}/logs/articles-history.jsonl", "a", encoding="utf-8") as log:
        for i, a in enumerate(arts):
            # results come back in submission order; map by index for reliability
            res = results[i] if i < len(results) else by.get(a["slug"], {})
            st_ = res.get("status", "unknown")
            if st_ == "inserted":
                inserted += 1
            log.write(json.dumps({"timestamp": now, "run_id": RUN_ID, "phase": "v2_covers_expanded",
                "publish_status": st_, "db_id": res.get("id"), "db_slug": res.get("slug"),
                "source_type": a["source_type"], "type": a["type"], "title": a["title"],
                "slug": a["slug"], "image_url": res.get("image_url") or a["image_url"],
                "topic": a["excerpt"][:140], "teams": [], "players": [],
                "sources": a["sources"]}, ensure_ascii=False) + "\n")
            # archive
            src = "news" if a["source_type"] == "news" else "trend"
            d = f"{REPO}/articles/{src}-{a['slug']}"
            os.makedirs(d, exist_ok=True)
            with open(f"{d}/{src}-{a['slug']}.md", "w", encoding="utf-8") as md:
                md.write(f"# {a['title']}\n\n> {a['excerpt']}\n\n"
                         f"*Категория: {a['category']} · Тип: {a['type']} · "
                         f"Подборка: {a['source_type']} · Обложка: {a['image_url']}*\n\n{a['body']}\n")

    json.dump({"run_id": RUN_ID, "generated_at": GENERATED_AT,
               "counts": {"total": len(arts), "inserted": inserted,
                          "news": sum(1 for a in arts if a["source_type"] == "news"),
                          "trend": sum(1 for a in arts if a["source_type"] == "trend")},
               "db_slugs": [results[i].get("slug") if i < len(results) else None for i in range(len(arts))]},
              open(f"{REPO}/logs/last-run.json", "w"), ensure_ascii=False, indent=2)

    print("\n=== RESULTS ===")
    for i, a in enumerate(arts):
        res = results[i] if i < len(results) else {}
        print(f"  {res.get('status','?'):10} {res.get('slug', a['slug'])}  img={bool(res.get('image_url'))}")
    print(f"Inserted {inserted}/{len(arts)}")

    # final output manifest
    json.dump({"generated_at": GENERATED_AT, "run_id": RUN_ID,
               "articles": [{"title": a["title"],
                             "slug": (results[i].get("slug") if i < len(results) else a["slug"]),
                             "body": a["body"], "excerpt": a["excerpt"], "category": a["category"],
                             "type": a["type"], "image_url": (results[i].get("image_url") if i < len(results) else a["image_url"]),
                             "image_base64": None, "sources": a["sources"], "source_type": a["source_type"],
                             "publish_status": (results[i].get("status") if i < len(results) else None)}
                            for i, a in enumerate(arts)]},
              open(f"{REPO}/logs/output-manifest-{RUN_ID}.json", "w"), ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
