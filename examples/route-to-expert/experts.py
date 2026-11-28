"""Route to the right expert: a decision model picks which specialist handles a
request, or "none" to keep it with the general assistant. The LLM still writes
every answer, and makes the routing call itself whenever the decision model is
below the bar. Every failure keeps the request with the general assistant.

Before switching, replay past requests where you know the right route and
compare the old router (the LLM alone) with the new one, route by route.

Expected, not measured: the model calls here are stand-ins.
"""
import math
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple

MODEL = "jev-1.14.0"  # pin the version you tested
QUESTION = "Which expert should handle this request?"
NONE = "none"
EXPERTS = {
    "benefits": "Health, dental and retirement plans, leave and vacation balances",
    "it_access": "Logins, passwords, accounts, devices and access to systems or drives",
    "expenses": "Expense reports, receipts, reimbursements and corporate cards",
}
OPTIONS = list(EXPERTS) + [NONE]
BAR = 0.6  # placeholder: set it from a replay of your own past requests


def build_body(request: str) -> dict:
    """One choice question. "none" means the general assistant answers."""
    criteria = dict(EXPERTS)
    criteria[NONE] = "None of these: a general question the assistant can answer itself"
    return {
        "state": request,
        "model": MODEL,
        "questions": {"expert": {"type": "choice", "instructions": QUESTION, "criteria": criteria}},
    }


def read_answer(answer: dict) -> dict:
    """The API's choice answer carries a probability for every option."""
    return answer["probabilities"]


def check(probs, options=OPTIONS) -> Dict[str, float]:
    """Refuse an answer we cannot trust: empty, an unknown option, or a
    probability outside 0 to 1. Refused answers count as failures."""
    if not isinstance(probs, dict) or not probs:
        raise ValueError("no probabilities")
    out = {}
    for option, p in probs.items():
        if option not in options:
            raise ValueError(f"unknown option {option!r}")
        p = float(p)
        if math.isnan(p) or not 0.0 <= p <= 1.0:
            raise ValueError("probability out of range")
        out[option] = p
    return out


def route_request(request: str, decide: Callable, llm_route: Callable,
                  bar: float = BAR, options=OPTIONS) -> dict:
    """Pick who handles the request. Nothing here writes text.

    Top option at or above `bar`: the decision model routes.
    Below the bar, or the decision model fails: the LLM routes, as before.
    The LLM also fails, or names an unknown expert: "none" (fail-safe)."""
    p_top = None
    try:
        probs = check(decide(request), options)
        best = max(probs, key=probs.get)
        p_top = probs[best]
        if p_top >= bar:
            return {"expert": best, "by": "decision model", "p": p_top}
    except Exception:
        pass
    try:
        choice = llm_route(request)
        if choice in options:
            return {"expert": choice, "by": "LLM", "p": p_top}
    except Exception:
        pass
    return {"expert": NONE, "by": "fail-safe", "p": p_top}


def handle(request: str, decide: Callable, llm_route: Callable, answer: Callable,
           bar: float = BAR) -> dict:
    """Route, then let the LLM (as the chosen expert, or the general assistant)
    do the actual work of answering."""
    routed = route_request(request, decide, llm_route, bar)
    return {**routed, "reply": answer(routed["expert"], request)}


@dataclass
class RouterScore:
    per_route: Dict[str, Tuple[Optional[float], Optional[float]]]  # route -> (precision, recall)
    accuracy: float
    wrong: int
    total: int


def score_routes(gold: List[str], chosen: List[str], options=OPTIONS) -> RouterScore:
    """Precision: of the requests sent to a route, the share that belonged there.
    Recall: of the requests that belonged there, the share sent there.
    None means nothing was sent there (precision) or nothing belonged (recall)."""
    per_route = {}
    for r in options:
        hits = sum(1 for g, c in zip(gold, chosen) if g == r and c == r)
        sent = chosen.count(r)
        belong = gold.count(r)
        per_route[r] = (hits / sent if sent else None, hits / belong if belong else None)
    total = len(gold)
    right = sum(1 for g, c in zip(gold, chosen) if g == c)
    return RouterScore(per_route, right / total if total else 0.0, total - right, total)


def _replayed(case: dict, bar: float, options) -> dict:
    """The new router on one past request: the decision model's recorded
    probabilities, and the LLM's recorded old route as its backup."""
    return route_request(case["request"], lambda r: case["probs"],
                         lambda r: case["old_route"], bar, options)


def replay(cases: Iterable[dict], bar: float = BAR, options=OPTIONS) -> Dict[str, RouterScore]:
    """cases: {'request', 'gold', 'old_route', 'probs'}. 'gold' is the route a
    person agrees was right. Returns {'old': RouterScore, 'new': RouterScore}."""
    cases = list(cases)
    gold = [c["gold"] for c in cases]
    new = [_replayed(c, bar, options)["expert"] for c in cases]
    return {"old": score_routes(gold, [c["old_route"] for c in cases], options),
            "new": score_routes(gold, new, options)}


def sweep_bar(cases: List[dict], bars=(0.5, 0.6, 0.7, 0.8, 0.9), options=OPTIONS) -> List[tuple]:
    """For each bar: (bar, settled by the decision model alone, sent to the LLM,
    settled ones that were wrong). Choose a bar on your own data."""
    out = []
    for b in bars:
        settled = to_llm = settled_wrong = 0
        for c in cases:
            r = _replayed(c, b, options)
            if r["by"] == "decision model":
                settled += 1
                settled_wrong += r["expert"] != c["gold"]
            else:
                to_llm += 1
        out.append((b, settled, to_llm, settled_wrong))
    return out
