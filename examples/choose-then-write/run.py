"""Route a made-up batch of school-letter events offline, then diff against today's calendar.

    python3 run.py             # offline: made-up scores in sample_input.json, a stand-in for the LLM
    python3 run.py --dry-run   # print the one request for the whole batch, send nothing
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from request import build_body  # noqa: E402
from route import add_calendar_flags, compare, route, split_cases  # noqa: E402


def stand_in_writer(kept):
    """Stand-in for the cheap LLM: merge items with the same date and owner under the first name."""
    groups = {}
    for k in kept:
        groups.setdefault((k["date"], k["owner"]), []).append(k)
    return [{"ids": [k["id"] for k in g], "owner": g[0]["owner"], "name": g[0]["title"]} for g in groups.values()]


if __name__ == "__main__":
    data = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))
    items = add_calendar_flags(data["items"])
    if "--dry-run" in sys.argv:
        print(json.dumps(build_body(data["rules"], items), indent=2, ensure_ascii=False))
        sys.exit(0)
    print(f"{len(data['items'])} items in, {len(items)} after calendar math in code")
    scores = data["scores"]
    result, who = route(items, lambda _: dict(scores), stand_in_writer, lambda _: data["old_calendar"])
    print(f"routed by {who}:")
    for m in result:
        print(f"  {m['owner']:<16} {m['name']}")
    print("split cases to turn into rules:", split_cases(items, scores))
    print("diff against today's calendar:", compare(result, data["old_calendar"]))
