"""Rules for checking customer profiles: the decision model checks every profile,
and only its unsure zone goes to an LLM for a second look.

All thresholds here are placeholders. Pick yours on one batch and check them on another.
"""

LOW, HIGH = 0.30, 0.90  # Hightouch's chosen zone, picked on the same data it scored


def check(p, llm_answer, low=LOW, high=HIGH):
    """p: the decision model's chance the profile joins two or more people (None if it was down).
    llm_answer: a function that returns the LLM's verdict, called only when needed.
    Returns (verdict, who decided)."""
    if p is None:
        return llm_answer(), "llm"  # decision model down: the LLM checks, as before
    if p >= high:
        return "wrongly_joined", "decision_model"
    if p < low:
        return "one_person", "decision_model"
    return llm_answer(), "llm"  # unsure zone


def evaluate(cases, low=LOW, high=HIGH, dm_cost=0.0, llm_cost=1.0):
    """cases: dicts with 'p' (decision model), 'llm' (LLM verdict) and 'truth'.
    Every case costs one decision-model call; cases in the zone also cost one LLM call.
    Returns the share sent to the LLM, accuracy, and cost relative to the LLM alone."""
    sent = right = 0
    for c in cases:
        verdict, who = check(c["p"], lambda c=c: c["llm"], low, high)
        sent += who == "llm"
        right += verdict == c["truth"]
    n = len(cases)
    coupled = n * dm_cost + sent * llm_cost
    return {
        "share_sent": sent / n,
        "accuracy": right / n,
        "cost_vs_llm_alone": coupled / (n * llm_cost),
    }


def honest_when_wrong(cases, cutoff=0.5, low=LOW, high=HIGH):
    """Before you couple: what share of the decision model's own mistakes fall inside the zone?
    Hightouch found most of Jev's mistakes did and most of GPT-6 Luna's did not."""
    misses = [c for c in cases if ("wrongly_joined" if c["p"] >= cutoff else "one_person") != c["truth"]]
    if not misses:
        return 1.0
    return sum(low <= c["p"] < high for c in misses) / len(misses)
