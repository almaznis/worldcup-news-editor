import sys, os, json, datetime, shutil, glob
sys.path.insert(0,".")
import articles_data_20260609 as A
import articles_data_repl_20260609 as R

RUN_ID="run-20260609-032e77be"
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
kept=[a for a in A.ARTICLES if a["slug"] in
      ("somali-referee-artan-denied-us-entry-world-cup-2026","iran-fans-tickets-revoked-world-cup-2026")]
final=kept+R.ARTICLES   # 8 articles
assert len(final)==8, len(final)

# 1) append accurate history lines for the 6 replacements + a correction note
removed=["netherlands-timber-out-world-cup-2026-geertruida-4/-5/-6",
         "uzbekistan-historic-world-cup-2026-debut-cannavaro-2/-3/-4",
         "brazil-2-1-egypt-friendly-cleveland-june-2026","spain-3-1-peru-friendly-june-2026",
         "ronaldo-portugal-world-cup-2026-last-dance","top-7-stars-to-watch-world-cup-2026-cis"]
with open("logs/articles-history.jsonl","a",encoding="utf-8") as f:
    for a in R.ARTICLES:
        f.write(json.dumps({"timestamp":NOW,"run_id":RUN_ID,"publish_status":"inserted",
            "source_type":a["source_type"],"type":a["type"],"title":a["title"],"slug":a["slug"],
            "image_via":"base64","category":a["category"],"topic":a["excerpt"],
            "teams":[],"players":[],"sources":a["sources"]},ensure_ascii=False)+"\n")
    f.write(json.dumps({"timestamp":NOW,"run_id":RUN_ID,"note":"run_correction",
        "detail":"Dedup performed against live DB (per-branch log was stale). Removed self-duplicate and topic-duplicate rows created by this run; replaced 6 already-covered topics with 6 DB-verified unique topics. Final unique set = 8.",
        "removed_slugs":removed,
        "final_slugs":[a["slug"] for a in final]},ensure_ascii=False)+"\n")

# 2) last-run.json
json.dump({"run_id":RUN_ID,"generated_at":NOW,"phase":"news+trend_v2_dedup_vs_db",
    "count":8,"inserted":8,"db_slugs":[a["slug"] for a in final],
    "note":"Deduplicated against live Supabase DB after discovering parallel runs had flooded the portal; see articles-history.jsonl run_correction line."},
    open("logs/last-run.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)

# 3) manifest (no base64/secret)
json.dump({"generated_at":NOW,"run_id":RUN_ID,
    "articles":[{"title":a["title"],"slug":a["slug"],"excerpt":a["excerpt"],"category":a["category"],
        "type":a["type"],"source_type":a["source_type"],"sources":a["sources"]} for a in final]},
    open("logs/manifest-20260609.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)

# 4) local archive: clean stale folders, write final 8
final_slugs={a["slug"] for a in final}
for d in glob.glob("articles/news-*")+glob.glob("articles/trend-*"):
    slug=os.path.basename(d).split("-",1)[1]
    if slug not in final_slugs:
        shutil.rmtree(d,ignore_errors=True)
for a in final:
    src="news" if a["source_type"]=="news" else "trend"
    d=f"articles/{src}-{a['slug']}"; os.makedirs(d,exist_ok=True)
    with open(f"{d}/{src}-{a['slug']}.md","w",encoding="utf-8") as f:
        f.write(f"# {a['title']}\n\n*{a['excerpt']}*\n\n- type: {a['type']}\n- category: {a['category']}\n"
                f"- source_type: {a['source_type']}\n- cover: {a['cover']}\n\n---\n\n"+a["body"]+"\n")

print("news:",sum(x['source_type']=='news' for x in final),"trend:",sum(x['source_type']=='trend' for x in final))
print("final slugs:"); [print("  -",a["slug"]) for a in final]
