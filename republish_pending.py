#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Republish the pending WC2026 Round-of-32 run once the Sport Arena Hub
publish-articles Edge Function is healthy again.

Background: on 2026-07-01 the 8 articles for this run were fully written and their
16:9 cover images optimized, but every POST to
https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles returned
HTTP 500 {"code":"WORKER_ERROR"} - the function crashed at startup on every call
(reproduced even with a wrong secret and a minimal payload), so nothing was
published and articles-history.jsonl was intentionally NOT updated.

Usage (after the backend is fixed):
    AGENT_PUBLISH_SECRET=... python3 republish_pending.py

It reads articles/_pending-run-20260701-wc2026-r32/manifest.json, re-encodes each
cover.jpg to base64, POSTs all 8 in one batch, prints results, and (on success)
appends one line per inserted article to logs/articles-history.jsonl.
"""
import os, sys, json, base64, time, datetime
import urllib.request

REPO = os.path.dirname(os.path.abspath(__file__))
PENDING = os.path.join(REPO, "articles", "_pending-run-20260701-wc2026-r32", "manifest.json")
ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
SECRET = os.environ.get("AGENT_PUBLISH_SECRET")
if not SECRET:
    sys.exit("AGENT_PUBLISH_SECRET not set")

m = json.load(open(PENDING))
articles = []
for e in m["articles"]:
    a = {k: e[k] for k in ["title","slug","body","excerpt","category","type","sources"]}
    a["image_url"] = None
    cover = os.path.join(REPO, e["cover_file"])
    a["image_base64"] = base64.b64encode(open(cover, "rb").read()).decode() if os.path.exists(cover) else None
    a["source_type"] = e["source_type"]
    articles.append(a)

data = json.dumps({"articles": articles}).encode()
req = urllib.request.Request(ENDPOINT, data=data,
        headers={"Content-Type": "application/json", "x-agent-secret": SECRET}, method="POST")
with urllib.request.urlopen(req, timeout=300) as r:
    resp = json.load(r)

results = resp.get("results", [])
inserted = [x for x in results if x.get("status") == "inserted"]
for x in results:
    print(x.get("status"), x.get("slug"), x.get("error"))
print("inserted:", len(inserted), "of", len(articles))

# append history only for clean (non-suffixed) inserts
hist = os.path.join(REPO, "logs", "articles-history.jsonl")
by_slug = {a["slug"]: a for a in articles}
now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
with open(hist, "a") as f:
    for x in inserted:
        ret = x.get("slug", "")
        base = ret
        intended = next((s for s in by_slug if ret.startswith(s)), ret)
        a = by_slug.get(intended, {})
        f.write(json.dumps({
            "timestamp": now, "run_id": m["run_id"], "source_type": a.get("source_type"),
            "type": a.get("type"), "title": a.get("title"), "slug": ret,
            "topic": (a.get("excerpt") or "")[:160], "teams": [], "players": [],
            "sources": a.get("sources", [])}, ensure_ascii=False) + "\n")
print("history updated")
