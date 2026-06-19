#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, ssl, time, urllib.request, urllib.error, datetime, pathlib

RUN_ID = "run-20260619-wc2026-md8"
ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
SECRET = os.environ["AGENT_PUBLISH_SECRET"]
CTX = ssl.create_default_context()

with open("/tmp/run_payload.json", encoding="utf-8") as f:
    articles = json.load(f)

def post(batch):
    data = json.dumps({"articles": batch}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("x-agent-secret", SECRET)
    last = None
    for attempt in range(4):
        try:
            r = urllib.request.urlopen(req, timeout=120, context=CTX)
            return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:500]
            if e.code in (401, 405):
                return e.code, {"fatal": body}
            last = (e.code, body)
        except Exception as e:
            last = ("EXC", str(e)[:200])
        time.sleep(2 * (2 ** attempt))
    return "FAIL", {"error": last}

print(f"Publishing {len(articles)} articles...")
status, resp = post(articles)
print("HTTP", status)
results = resp.get("results", []) if isinstance(resp, dict) else []
by_slug = {r.get("slug", "").rstrip("-0123456789") or r.get("slug"): r for r in results}
for r in results:
    print(f"  {r.get('status'):9} {r.get('slug')}  id={r.get('id')}  {r.get('error') or ''}")
if status in (401, 405) or "fatal" in (resp or {}):
    print("FATAL endpoint response:", resp)
    raise SystemExit(1)

# retry errored items once
errored = [r for r in results if r.get("status") == "error"]
retry_results = []
if errored:
    err_slugs = {r["slug"] for r in errored}
    retry_batch = [a for a in articles if a["slug"] in err_slugs]
    print(f"Retrying {len(retry_batch)} errored items...")
    time.sleep(3)
    st2, resp2 = post(retry_batch)
    retry_results = resp2.get("results", []) if isinstance(resp2, dict) else []
    for r in retry_results:
        print(f"  RETRY {r.get('status'):9} {r.get('slug')}  {r.get('error') or ''}")

# Merge final results keyed by original slug order
final = {}
for r in results + retry_results:
    final[r.get("slug")] = r  # later (retry) overrides

# ───────── logging ─────────
ROOT = pathlib.Path("/home/user/worldcup-news-editor")
logs = ROOT / "logs"; logs.mkdir(exist_ok=True)
hist = logs / "articles-history.jsonl"
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

# map returned slugs back to articles in order (results preserve input order on first pass)
inserted_slugs = []
result_list_in_order = []
# first-pass results are in submit order; build per-article result
for a in articles:
    # find a matching result: exact slug or slug+suffix
    match = None
    for r in results:
        rs = r.get("slug", "")
        if rs == a["slug"] or rs.startswith(a["slug"] + "-"):
            match = r; break
    # apply retry override if present
    for r in retry_results:
        rs = r.get("slug", "")
        if rs == a["slug"] or rs.startswith(a["slug"] + "-"):
            match = r
    result_list_in_order.append((a, match or {}))

with hist.open("a", encoding="utf-8") as fh:
    for a, r in result_list_in_order:
        st = r.get("status", "unknown")
        if st == "inserted":
            inserted_slugs.append(r.get("slug"))
        entry = {
            "timestamp": now, "run_id": RUN_ID, "publish_status": st,
            "db_id": r.get("id"), "db_slug": r.get("slug"),
            "source_type": a["source_type"], "type": a["type"],
            "title": a["title"], "slug": a["slug"],
            "topic": a["excerpt"], "category": a["category"],
            "has_base64_img": a.get("image_base64") is not None,
            "sources": a["sources"],
        }
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

# last-run.json
(logs / "last-run.json").write_text(json.dumps({
    "run_id": RUN_ID,
    "generated_at": now,
    "count": len(articles),
    "inserted": len(inserted_slugs),
    "news": sum(a["source_type"] == "news" for a in articles),
    "trend": sum(a["source_type"] == "trend" for a in articles),
    "db_slugs": [r.get("slug") for a, r in result_list_in_order],
    "slugs": [a["slug"] for a in articles],
}, ensure_ascii=False, indent=2), encoding="utf-8")

# local markdown archive
for a, r in result_list_in_order:
    src = "news" if a["source_type"] == "news" else "trend"
    folder = ROOT / "articles" / f"{src}-{a['slug']}"
    folder.mkdir(parents=True, exist_ok=True)
    fm = (f"# {a['title']}\n\n_slug:_ `{a['slug']}` | _type:_ {a['type']} | "
          f"_category:_ {a['category']} | _status:_ {r.get('status','?')} | "
          f"_db_slug:_ {r.get('slug','-')}\n\n_Источники:_ " +
          ", ".join(a["sources"]) + "\n\n---\n\n")
    (folder / f"{src}-{a['slug']}.md").write_text(fm + a["body"] + "\n", encoding="utf-8")

print("\nInserted:", len(inserted_slugs), "/", len(articles))
print("DB slugs:", [r.get("slug") for a, r in result_list_in_order])
print("DONE")
