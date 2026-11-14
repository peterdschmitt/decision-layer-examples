"""A decision model screens every summary for personal details. Only flagged summaries go to the
LLM to be rewritten, and each rewrite is checked again. Clean summaries never reach the LLM."""

QUESTIONS = ["Does this name a real person?", "Does this show contact details or an ID?"]


def scrub(summary, decide, rewrite, bar=0.40, max_rewrites=2):
    """decide(text, question) -> chance the answer is yes. rewrite(text) -> text without the details.
    Returns (text or None, LLM calls). None means still flagged after the rewrites: hold it for a person.
    If the decision model is down, the summary counts as flagged: nothing is stored unchecked."""
    calls = 0
    while True:
        try:
            flagged = any(decide(summary, q) >= bar for q in QUESTIONS)
        except Exception:
            flagged = True
        if not flagged:
            return summary, calls
        if calls == max_rewrites:
            return None, calls
        summary = rewrite(summary)
        calls += 1


def evaluate(cases, bar=0.40):
    """cases: [{"has_personal": bool, "scores": [p_question_1, p_question_2]}]
    Returns how many skip the LLM, how many false alarms go to it, and how many misses get stored."""
    skipped = false_alarms = misses = 0
    for c in cases:
        flagged = max(c["scores"]) >= bar
        if not flagged:
            skipped += 1
            if c["has_personal"]:
                misses += 1
        elif not c["has_personal"]:
            false_alarms += 1
    return {"total": len(cases), "skip_llm": skipped, "false_alarms": false_alarms, "misses": misses}


def pick_bar(cases, cost_false_alarm, cost_miss, bars=(0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)):
    """The bar with the lowest total cost of mistakes. A false alarm costs one LLM call; a miss stores
    personal data as clean. When a miss costs far more, the cheapest bar is a low one. Ties go to the
    lower bar. Pick it on one batch and check it on another."""
    def cost(b):
        r = evaluate(cases, b)
        return r["false_alarms"] * cost_false_alarm + r["misses"] * cost_miss
    return min(bars, key=lambda b: (cost(b), b))
