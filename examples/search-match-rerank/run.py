"""Re-rank a sample search offline, then read a made-up three-arm test.

    python3 run.py             # offline: made-up scores and visit counts in sample_input.json
    python3 run.py --dry-run   # print the request for one product, send nothing
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from request import build_body  # noqa: E402
from rerank import rerank, split_credit  # noqa: E402

if __name__ == "__main__":
    data = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))
    if "--dry-run" in sys.argv:
        print(json.dumps(build_body(data["search"], data["candidates"][0]), indent=2, ensure_ascii=False))
        sys.exit(0)
    scores = {c["title"]: c["score"] for c in data["candidates"]}
    ranked, who = rerank(data["search"], data["candidates"], lambda s, p: scores[p["title"]])
    print(f"ranked by {who}:")
    for p in ranked:
        print(f"  {scores[p['title']]:.2f}  {p['title']}")
    arms = {k: tuple(v) for k, v in data["test_arms"].items()}
    for name, r in split_credit(arms["old_search"], arms["new_search"], arms["new_search_plus_model"]).items():
        print(f"{name}: lift {r['lift']:+.1%}, p-value {r['p_value']:.4f}")
