"""Route and set effort. Before an LLM does any work, a decision model answers two small questions:
where should this request go, and how hard should the LLM work on it? The LLMs still do the work.

Shape from Microsoft's description of Microsoft-Decision-1.1 in Copilot (Nov. 17, 2026): the
decision model chooses between Copilot's chat and the Cowork agent, and in Cowork it sets how much
reasoning effort to spend. Microsoft has not published its code; this code is ours.
"""

ROUTES = ("chat", "agent")  # answer in chat, or hand to the agent that takes actions
EFFORTS = ("low", "medium", "high")
ROUTE_BAR = 0.8  # below this, the request goes to the LLM router you already have
EFFORT_BAR = 0.7  # below this, step up one level: more effort costs more, a weak answer costs more


def top(probs):
    label = max(probs, key=probs.get)
    return label, probs[label]


def choose_route(request, decide, llm_route, default="chat", bar=ROUTE_BAR):
    """Decision model first. Sure: take its route. Unsure: ask the LLM router.
    Both down: the default. Returns (route, source, confidence)."""
    try:
        route, p = top(decide(request, ROUTES))
        if p >= bar:
            return route, "decision_model", p
    except Exception:
        pass
    try:
        return llm_route(request), "llm", None
    except Exception:
        return default, "rule", None


def choose_effort(request, decide, bar=EFFORT_BAR):
    """How hard should the LLM work? When the decision model is unsure, go one level up."""
    try:
        level, p = top(decide(request, EFFORTS))
    except Exception:
        return "medium", "rule", None
    if p >= bar:
        return level, "decision_model", p
    i = EFFORTS.index(level)
    return EFFORTS[min(i + 1, len(EFFORTS) - 1)], "stepped_up", p


def handle(request, decide, llm_route, workers):
    """Route, set effort, then hand the request to the LLM that does the work.
    workers = {"chat": fn(request, effort), "agent": fn(request, effort)}."""
    route, r_src, r_p = choose_route(request, decide, llm_route)
    effort, e_src, e_p = choose_effort(request, decide)
    answer = workers[route](request, effort)
    return {"route": route, "route_by": r_src, "route_p": r_p,
            "effort": effort, "effort_by": e_src, "effort_p": e_p, "answer": answer}


def agreement_with_llm(decide, past):
    """Before switching: on past requests the LLM router already handled, how often does the
    decision model pick the same route, and how many would it have taken on its own?"""
    same = sure = 0
    for item in past:
        route, p = top(decide(item["request"], ROUTES))
        same += route == item["llm_route"]
        sure += p >= ROUTE_BAR
    n = len(past) or 1
    return {"same_route": round(same / n, 3), "decided_alone": round(sure / n, 3)}


def share_by_source(records, key="route_by"):
    counts = {}
    for r in records:
        counts[r[key]] = counts.get(r[key], 0) + 1
    n = len(records) or 1
    return {k: round(v / n, 3) for k, v in sorted(counts.items())}
