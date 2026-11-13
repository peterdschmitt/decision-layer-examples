"""Score the sample test set offline, or print the request for one page.

    python3 run.py             # offline: made-up probabilities in sample_input.json
    python3 run.py --dry-run   # print a request for one page, send nothing
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from judge import evaluate, pick_bar  # noqa: E402
from request import QUESTIONS, build_body  # noqa: E402

if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        qs = dict(QUESTIONS, invoice_total=QUESTIONS["invoice_total"].format(invoice="AEC-2025-104276"))
        print(json.dumps(build_body("<base64 page image>", qs), indent=2))
        sys.exit(0)
    cases = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))["cases"]
    print("at bar 0.30:", evaluate(cases, 0.30))
    print("highest bar that blanks no real answer:", pick_bar(cases))
