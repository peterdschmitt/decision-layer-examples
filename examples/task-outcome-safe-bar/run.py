"""Send the sample task message to the API and print the answer.

    python3 run.py --dry-run   # print the request, send nothing
    python3 run.py             # needs TYPESAFE_API_KEY in your environment
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from request import build_body  # noqa: E402

if __name__ == "__main__":
    sample = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))
    body = build_body(sample["last_message"])
    if "--dry-run" in sys.argv:
        print(json.dumps(body, indent=2))
    else:
        from common.jev_client import ask  # noqa: E402

        print(json.dumps(ask(body), indent=2))
