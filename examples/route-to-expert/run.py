"""Route one helpdesk request, then replay a made-up history of past requests.

    python3 run.py --dry-run   # print the request, send nothing, replay offline
    python3 run.py             # needs TYPESAFE_API_KEY in your environment

The two LLM functions below are stand-ins. Swap them for your assistant's own calls.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from common.jev_client import ask  # noqa: E402
from experts import OPTIONS, build_body, handle, read_answer, replay, sweep_bar  # noqa: E402

SAMPLE = "My dental claim was denied last week. Who can help me appeal it?"

# MADE UP for this example: not real requests, routes or model output.
# gold = the route a person agrees was right, old_route = what the LLM chose on its own,
# probs = what the decision model said (None = it timed out).
PAST = [
    {"request": "How do I add my newborn to my health plan?",
     "gold": "benefits", "old_route": "benefits", "probs": {"benefits": 0.93, "none": 0.05, "expenses": 0.02}},
    {"request": "I'm locked out of my laptop after the password change",
     "gold": "it_access", "old_route": "it_access", "probs": {"it_access": 0.95, "none": 0.05}},
    {"request": "Where do I submit the receipt for last week's client dinner?",
     "gold": "expenses", "old_route": "none", "probs": {"expenses": 0.88, "none": 0.12}},
    {"request": "I need the guest wifi password for a visitor",
     "gold": "it_access", "old_route": "none", "probs": {"it_access": 0.71, "none": 0.29}},
    {"request": "When is the company holiday party?",
     "gold": "none", "old_route": "none", "probs": {"none": 0.82, "benefits": 0.18}},
    {"request": "Can I put a client's train ticket on my corporate card?",
     "gold": "expenses", "old_route": "benefits", "probs": {"expenses": 0.64, "benefits": 0.30, "none": 0.06}},
    {"request": "How many vacation days do I have left?",
     "gold": "benefits", "old_route": "benefits", "probs": {"benefits": 0.58, "none": 0.32, "expenses": 0.10}},
    {"request": "Summarize the new travel policy for me",
     "gold": "none", "old_route": "expenses", "probs": {"none": 0.52, "expenses": 0.40, "benefits": 0.08}},
    {"request": "I need access to the finance shared drive",
     "gold": "it_access", "old_route": "expenses", "probs": {"it_access": 0.77, "expenses": 0.20, "none": 0.03}},
    {"request": "Does our retirement match vest right away?",
     "gold": "benefits", "old_route": "none", "probs": {"benefits": 0.90, "none": 0.10}},
    {"request": "My conference reimbursement still hasn't arrived",
     "gold": "expenses", "old_route": "expenses", "probs": {"expenses": 0.91, "benefits": 0.09}},
    {"request": "My dental claim was denied, who do I talk to?",
     "gold": "benefits", "old_route": "benefits", "probs": {"expenses": 0.61, "benefits": 0.35, "none": 0.04}},
    {"request": "Can you reword this email to my team?",
     "gold": "none", "old_route": "none", "probs": None},
]


def llm_route(request: str) -> str:
    """Stand-in for the assistant's own routing call, used only below the bar."""
    return "benefits" if "dental" in request.lower() else "none"


def answer(expert: str, request: str) -> str:
    """Stand-in for the LLM doing the work, as the chosen expert or the general assistant."""
    who = "the general assistant" if expert == "none" else f"the {expert} expert"
    return f"(stand-in) {who} would answer: {request}"


def fmt(x):
    return "n/a" if x is None else f"{x:.2f}"


def show_replay() -> None:
    print("\nReplay of 13 made-up past requests (bar 0.6):")
    r = replay(PAST)
    print(f"  {'route':<10} {'old precision':>14} {'old recall':>11} {'new precision':>14} {'new recall':>11}")
    for route in OPTIONS:
        (op, orc), (np_, nr) = r["old"].per_route[route], r["new"].per_route[route]
        print(f"  {route:<10} {fmt(op):>14} {fmt(orc):>11} {fmt(np_):>14} {fmt(nr):>11}")
    for name in ("old", "new"):
        s = r[name]
        print(f"  {name} router: accuracy {s.accuracy:.0%}, wrong routes {s.wrong} of {s.total}")
    print("\nBar sweep (bar, settled by the decision model, sent to the LLM, settled but wrong):")
    for row in sweep_bar(PAST):
        print("  ", row)


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        print(json.dumps(build_body(SAMPLE), indent=2))
    else:
        decide = lambda req: read_answer(ask(build_body(req))["expert"])  # noqa: E731
        print(json.dumps(handle(SAMPLE, decide, llm_route, answer), indent=2))
    show_replay()
