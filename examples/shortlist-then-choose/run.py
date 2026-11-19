"""Shortlist and choose five made-up products offline.

    python3 run.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from choose import accuracy, choose, error_cut, recall_at_k, share_by_source, shortlist  # noqa: E402

if __name__ == "__main__":
    data = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))
    cats, prods = data["categories"], data["products"]
    truth = {k: v["truth"] for k, v in prods.items()}
    lists = {k: shortlist(v["vec"], cats, k=3) for k, v in prods.items()}
    print("right category on the short list:", recall_at_k(prods, truth, lists))
    decide = lambda item, options: prods[item]["answers"]  # stand-in for the decision model
    llm_pick = lambda item, options: truth[item]  # stand-in for the LLM you already use
    results = {k: choose(k, lists[k], decide, llm_pick) for k in prods}
    for k, (cat, src, p) in results.items():
        print(f"  {k}: {cat:<16} by {src}")
    print("accuracy:", accuracy(results, truth), "| made by:", share_by_source(results))
    print("Channel3's numbers, 81.9% -> 97.2%: errors cut by", error_cut(0.819, 0.972))
