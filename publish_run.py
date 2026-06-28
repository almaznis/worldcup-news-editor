# -*- coding: utf-8 -*-
"""Robust chunked publisher for the 2026-06-28 run."""
import json, os, sys, time
import requests
from run_20260628 import articles, ENDPOINT

SECRET = os.environ.get("AGENT_PUBLISH_SECRET")
if not SECRET:
    print("ERROR: AGENT_PUBLISH_SECRET missing"); sys.exit(2)
HEADERS = {"Content-Type":"application/json","x-agent-secret":SECRET}

def post_chunk(items, attempts=4):
    last=None
    for i in range(attempts):
        try:
            r = requests.post(ENDPOINT, headers=HEADERS, data=json.dumps({"articles":items}), timeout=120)
            if r.status_code==200:
                return 200, r.json()
            last=(r.status_code, r.text[:200])
            print(f"  attempt {i+1}: HTTP {r.status_code} {r.text[:120]}")
        except Exception as e:
            last=(None,str(e)); print(f"  attempt {i+1}: EXC {e}")
        time.sleep(2*(2**i))
    return last

def main(chunk_size=1):
    results={}  # slug -> result dict
    pending=list(articles)
    # publish one-by-one (most resource-friendly), collect statuses
    for art in pending:
        slug=art["slug"]
        print(f"Publishing: {slug}")
        out=post_chunk([art])
        if isinstance(out,tuple) and out and out[0]==200:
            code,resp=out
            for res in resp.get("results",[]):
                results[res.get("slug",slug)]=res
                print(f"  -> {res.get('status')} slug={res.get('slug')} id={res.get('id')} err={res.get('error')}")
        else:
            results[slug]={"slug":slug,"status":"error","error":str(out)}
            print(f"  -> FAILED {out}")
        time.sleep(1)
    with open("publish_results.json","w",encoding="utf-8") as f:
        json.dump(results,f,ensure_ascii=False,indent=2)
    ins=sum(1 for r in results.values() if r.get("status")=="inserted")
    print(f"\nINSERTED {ins}/{len(articles)}")
    return results

if __name__=="__main__":
    main()
