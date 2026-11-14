"""Score the sample set offline, or print the request for one summary.

    python3 run.py             # offline: made-up probabilities in sample_input.json
    python3 run.py --dry-run   # print a request for one summary, send nothing
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gate import evaluate, pick_bar  # noqa: E402
from request import build_body  # noqa: E402

if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        print(json.dumps(build_body("User opened billing, typed a card number, then left."), indent=2))
        sys.exit(0)
    cases = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))["cases"]
    print("at bar 0.40:", evaluate(cases, 0.40))
    print("cheapest bar when a miss costs 100 LLM calls:", pick_bar(cases, cost_false_alarm=1, cost_miss=100))
    print("cheapest bar when a miss costs 1 LLM call:", pick_bar(cases, cost_false_alarm=1, cost_miss=1))
