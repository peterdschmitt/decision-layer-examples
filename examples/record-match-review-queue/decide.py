"""Decision model answers every pair; an LLM reviews only the least-sure few; a bar guards every answer that changes a record.
Bars and review counts are placeholders: set them from your own test cases, then re-check on real records."""

from typing import Callable

Probs = dict  # {"same": p, "different": p, "unsure": p}


def sureness(probs: Probs) -> float:
    """Rank for review. An "unsure" top answer, or no answer at all, counts as least sure."""
    if not probs:
        return -1.0
    top = max(probs, key=probs.get)
    return 0.0 if top == "unsure" else probs[top]


def final(probs: Probs, bar: float) -> str:
    """The answer that changes a record, or "hold". Southbridge's one coupled mistake was a 53% guess with no bar."""
    if not probs:
        return "hold"
    top = max(probs, key=probs.get)
    return top if top != "unsure" and probs[top] >= bar else "hold"


def match(cases: list, decide: Callable[[dict], Probs], review: Callable[[dict], Probs], max_reviews: int = 5, bar: float = 0.8) -> dict:
    """cases: [{"id": .., "a": {..}, "b": {..}}]. review() is the LLM; it sees the records, not the decision model's answer."""
    answers = {}
    for c in cases:
        try:
            answers[c["id"]] = decide(c)
        except Exception:
            answers[c["id"]] = {}  # decision model down: send to review first
    queue = sorted(cases, key=lambda c: sureness(answers[c["id"]]))[:max_reviews]
    reviewed = set()
    for c in queue:
        try:
            answers[c["id"]] = review(c)
            reviewed.add(c["id"])
        except Exception:
            pass  # a failed review keeps the decision model's answer; the bar still applies
    return {cid: {"answer": final(p, bar), "reviewed": cid in reviewed} for cid, p in answers.items()}


def score(results: dict, truth: dict) -> dict:
    """Compare against your own answer key. Count holds separately: a hold is not a wrong merge."""
    right = sum(1 for cid, r in results.items() if r["answer"] == truth[cid])
    held = sum(1 for r in results.values() if r["answer"] == "hold")
    return {"right": right, "held": held, "wrong": len(results) - right - held, "of": len(results)}
