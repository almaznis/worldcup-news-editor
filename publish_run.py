#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publish a run of articles to the Sport Arena Hub endpoint, then append to the
history log and update last-run.json.

Usage: python3 publish_run.py <payload.json>
  where payload.json = { "run_id": "...", "generated_at": "...",
                         "articles": [ {...}, ... ] }
Each article object may carry "image_base64" and "log_meta" (topic/teams/players);
both are stripped from what we send/store appropriately.
"""
import base64, io, json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
from PIL import Image

ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
SECRET   = os.environ["AGENT_PUBLISH_SECRET"]
LOG_PATH = "/home/user/worldcup-news-editor/logs/articles-history.jsonl"
LAST_RUN = "/home/user/worldcup-news-editor/logs/last-run.json"


def download_base64(url: str) -> str | None:
    """Download, optimize (resize longest side to 1600px, JPEG q82, strip EXIF),
    and return base64. Returns None on failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (WorldCupNewsAgent)"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
        im = Image.open(io.BytesIO(raw)); im.load()
        w, h = im.size
        if h >= w:
            print(f"  img WARN not landscape ({w}x{h}) {url.split('/')[-1][:40]}")
        im = im.convert("RGB")
        longest = max(w, h)
        if longest > 1600:
            s = 1600 / longest
            im = im.resize((int(w * s), int(h * s)))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=82, optimize=True)  # no exif → metadata stripped
        out = buf.getvalue()
        enc = base64.b64encode(out).decode("ascii")
        print(f"  img ok {url.split('/')[-1][:44]} ({len(raw)//1024}->{len(out)//1024} KB)")
        return enc
    except Exception as exc:
        print(f"  img FAIL {url}: {exc}")
        return None


def post(articles: list) -> list:
    payload = json.dumps({"articles": articles}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("x-agent-secret", SECRET)
    last_err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode()).get("results", [])
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:400]
            print(f"HTTP {e.code}: {body}")
            if e.code in (401, 405):
                raise SystemExit(f"Fatal auth/method error {e.code} — stopping.")
            last_err = e
        except Exception as e:
            print(f"network error: {e}")
            last_err = e
        time.sleep(2 ** (attempt + 1))
    raise SystemExit(f"Publish failed after retries: {last_err}")


def main():
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        run = json.load(f)
    run_id = run["run_id"]
    arts = run["articles"]

    # Encode any cover images that are given as a download URL in _image_src.
    send = []
    meta_by_slug = {}
    for a in arts:
        obj = {k: a[k] for k in ("title", "slug", "body", "excerpt", "category",
                                 "type", "image_url", "sources", "source_type")}
        if a.get("image_base64"):
            obj["image_base64"] = a["image_base64"]
        elif a.get("_image_src"):
            b64 = download_base64(a["_image_src"])
            if b64:
                obj["image_base64"] = b64
            else:
                obj["image_url"] = a.get("image_url")
        send.append(obj)
        meta_by_slug[a["slug"]] = a.get("log_meta", {})

    print(f"Publishing {len(send)} articles…")
    results = post(send)

    # Retry failures once more individually
    failed = [r for r in results if r.get("status") != "inserted"]
    if failed:
        print(f"Retrying {len(failed)} failed items…")
        fset = {r["slug"] for r in failed}
        retry_objs = [o for o in send if o["slug"] in fset]
        retry_results = post(retry_objs)
        by = {r.get("slug"): r for r in results}
        for r in retry_results:
            by[r.get("slug")] = r
        results = list(by.values())

    for r in results:
        mark = "OK " if r.get("status") == "inserted" else "ERR"
        print(f"  {mark} {r.get('slug')} [{r.get('status')}] {r.get('error') or ''}")

    # Append log lines for inserted articles
    ts = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    inserted = [r for r in results if r.get("status") == "inserted"]
    # map returned slug back to source article by stripping -N suffix match
    src_by_slug = {a["slug"]: a for a in arts}
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        for r in inserted:
            ret_slug = r.get("slug")
            base = ret_slug
            src = src_by_slug.get(base)
            if not src:
                # try stripping trailing -N
                import re
                m = re.match(r"^(.*)-\d+$", ret_slug)
                if m:
                    src = src_by_slug.get(m.group(1))
            src = src or {}
            meta = meta_by_slug.get(src.get("slug"), {})
            entry = {
                "timestamp":   ts,
                "run_id":      run_id,
                "source_type": src.get("source_type"),
                "type":        src.get("type"),
                "title":       src.get("title"),
                "slug":        ret_slug,
                "topic":       meta.get("topic", ""),
                "teams":       meta.get("teams", []),
                "players":     meta.get("players", []),
                "sources":     src.get("sources", []),
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    with open(LAST_RUN, "w", encoding="utf-8") as f:
        json.dump({
            "run_id": run_id,
            "generated_at": run.get("generated_at", ts),
            "count": len(inserted),
            "slugs": [r.get("slug") for r in inserted],
        }, f, ensure_ascii=False, indent=2)
    print(f"\nInserted {len(inserted)}/{len(send)}. Logs updated.")
    if len(inserted) != len(send):
        print("WARNING: not all articles inserted.")


if __name__ == "__main__":
    main()
