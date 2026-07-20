# -*- coding: utf-8 -*-
"""POST the run-2 payload to the Sport Arena Hub publish endpoint. Retries errored items once."""
import json, os, sys, time
import requests

ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"
CA = "/root/.ccr/ca-bundle.crt"
VERIFY = CA if os.path.exists(CA) else True

secret = os.environ.get("AGENT_PUBLISH_SECRET")
if not secret:
    print("FATAL: AGENT_PUBLISH_SECRET not set"); sys.exit(2)

payload = json.load(open("run2_payload.json"))
by_slug = {a["slug"]: a for a in payload["articles"]}
HDRS = {"Content-Type": "application/json", "x-agent-secret": secret}

def post(articles):
    r = requests.post(ENDPOINT, headers=HDRS, data=json.dumps({"articles": articles}),
                      verify=VERIFY, timeout=180)
    print("HTTP", r.status_code)
    if r.status_code == 401:
        print("401 Unauthorized — secret rejected. STOP."); sys.exit(3)
    try:
        return r.status_code, r.json()
    except Exception:
        print("Non-JSON response:", r.text[:500]); return r.status_code, None

status, resp = post(payload["articles"])
if resp is None:
    sys.exit(4)
results = resp.get("results", [])
for x in results:
    print(f"  {x.get('status'):9} slug={x.get('slug')} id={x.get('id')} err={x.get('error')}")

errored = [x for x in results if x.get("status") == "error"]
if errored:
    print(f"\nRetrying {len(errored)} errored item(s)...")
    time.sleep(3)
    retry_articles = [by_slug[x["slug"]] for x in errored if x.get("slug") in by_slug]
    status2, resp2 = post(retry_articles)
    if resp2:
        r2 = resp2.get("results", [])
        for x in r2:
            print(f"  RETRY {x.get('status'):9} slug={x.get('slug')} id={x.get('id')} err={x.get('error')}")
        # merge retry results back
        rmap = {x.get("slug"): x for x in r2}
        results = [rmap.get(x["slug"], x) if x.get("status") == "error" else x for x in results]

json.dump({"results": results}, open("run2_results.json", "w"), ensure_ascii=False, indent=2)
ins = sum(1 for x in results if x.get("status") == "inserted")
err = sum(1 for x in results if x.get("status") == "error")
print(f"\nFINAL: inserted={ins} error={err}")
# flag suffixed slugs (already-published duplicates)
for x in results:
    rs = x.get("slug", "")
    if rs and rs[-2:] in ("-2","-3","-4","-5","-6","-7","-8","-9"):
        print(f"  NOTE suffixed slug (possible duplicate): {rs}")
