"""Qualify four made-up LLM steps, then run a cascade over one of them offline.

    python3 run.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from cascade import cascade, qualify, share_by_source  # noqa: E402

if __name__ == "__main__":
    data = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))
    answers = data["model_answers"]
    decide = lambda key: answers[key]  # stand-in for the decision model
    moves, stays = qualify(data["steps"], decide)
    print("move to the decision model:", moves)
    print("stay on the LLM:", stays)
    items = ["r1", "r2", "r3", "r4", "d1", "d2", "d3", "d4"]
    results = [cascade(i, decide, llm=lambda i: "llm_label", rule=lambda i: "rule_label") for i in items]
    for i, r in zip(items, results):
        print(f"  {i}: {r[0]:<10} from {r[1]}")
    print("share by source:", share_by_source(results))
