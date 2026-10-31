"""Check the sample LLM draft against the claim file and print the action.

    python3 run.py --dry-run   # print the request, send nothing
    python3 run.py             # needs TYPESAFE_API_KEY in your environment

Plug in your own LLM where the draft comes from; the check is model-agnostic.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from common.jev_client import ask  # noqa: E402
from request import build_body  # noqa: E402
from route import route  # noqa: E402

if __name__ == "__main__":
    with open(os.path.join(HERE, "claim_file.json"), encoding="utf-8") as f:
        claim_file = json.load(f)
    with open(os.path.join(HERE, "llm_draft.txt"), encoding="utf-8") as f:
        draft = f.read().strip()
    body = build_body(claim_file, draft)
    if "--dry-run" in sys.argv:
        print(json.dumps(body, indent=2))
        sys.exit(0)
    answers = ask(body)
    action, fixes = route(answers)
    print(json.dumps(answers, indent=2))
    print("action:", action)
    for fix in fixes:
        print(" - tell the LLM:", fix)
