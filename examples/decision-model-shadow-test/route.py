"""Act on confident answers, send the rest to the LLM, and score candidates in shadow.

The bars here are placeholders. The point of a shadow test is to set them from your own
labelled cases, separately for each decision model: a cut-off does not carry across models.
"""

BAR = 0.9  # placeholder: set per model from your own data


def route(answers: dict, bar: float = BAR) -> dict:
    p = answers["urgent"].get("noul")
    if p is None or 1 - bar < p < bar:
        return {"action": "llm_review", "probability": p}  # unsure: the LLM decides, as today
    return {"action": "page_on_call" if p >= bar else "normal_queue", "probability": p}


def shadow_test(probabilities, labels, bar):
    """probabilities: one candidate's answers on your past cases; labels: the right answers."""
    acted = wrong = missed_urgent = 0
    for p, right in zip(probabilities, labels):
        if 1 - bar < p < bar:
            continue  # would have gone to the LLM
        acted += 1
        said = p >= bar
        wrong += said != right
        missed_urgent += right and not said  # the expensive mistake: urgent sent to the normal queue
    n = len(labels)
    return {
        "runs_without_llm": acted / n if n else 0.0,
        "wrong_when_acting": wrong / acted if acted else 0.0,
        "missed_urgent": missed_urgent,
    }


def pick_bar(probabilities, labels, max_wrong=0.01, bars=(0.7, 0.8, 0.9, 0.95, 0.99)):
    """Lowest bar (most work without the LLM) whose error rate when acting stays under max_wrong
    and which never sends an urgent ticket to the normal queue. None if no bar qualifies."""
    for bar in sorted(bars):
        r = shadow_test(probabilities, labels, bar)
        if r["wrong_when_acting"] <= max_wrong and r["missed_urgent"] == 0 and r["runs_without_llm"] > 0:
            return bar, r
    return None, None
