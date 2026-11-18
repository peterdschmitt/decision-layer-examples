"""Route six made-up requests offline and set the effort for each.

    python3 run.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from route import agreement_with_llm, handle, share_by_source  # noqa: E402

if __name__ == "__main__":
    data = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))
    reqs = data["requests"]

    def decide(key, options):  # stand-in for the decision model
        return reqs[key]["route"] if "chat" in options else reqs[key]["effort"]

    print("before switching:", agreement_with_llm(decide, data["past_llm_routes"]))
    workers = {"chat": lambda r, e: f"chat answer ({e})", "agent": lambda r, e: f"agent task ({e})"}
    records = [handle(k, decide, llm_route=lambda r: "agent", workers=workers) for k in reqs]
    for k, r in zip(reqs, records):
        print(f"  {k}: {r['route']:<5} by {r['route_by']:<14} effort {r['effort']:<6} by {r['effort_by']}")
    print("route made by:", share_by_source(records))
    print("effort made by:", share_by_source(records, "effort_by"))
