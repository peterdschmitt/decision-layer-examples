"""Send the sample chat to the API and print the routing decision.

    python3 run.py --dry-run   # print the request, send nothing
    python3 run.py             # needs TYPESAFE_API_KEY in your environment
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
    chat = json.load(open(os.path.join(HERE, "sample_input.json")))
    body = build_body(chat)
    if "--dry-run" in sys.argv:
        print(json.dumps(body, indent=2))
    else:
        answers = ask(body)
        print(json.dumps(answers, indent=2))
        print("decision:", route(answers, chat))
