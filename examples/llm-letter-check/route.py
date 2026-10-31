"""Turn the decision model's scores into the next step: send, or direct the LLM.

This is the tandem: the scores become precise directions for the LLM,
so the next draft lands right.
Thresholds are placeholders.
"""

PROMISE_BAR = 0.2      # low: a wrong promise is the costliest mistake
CONTRADICTION_BAR = 0.3
DOCS_FLOOR = 0.7
TONE_FLOOR = 1.4       # 0 to 2
MAX_REVISIONS = 2

FIXES = {
    "promises_outcome": "Remove any promise of payment, coverage or outcome. Say the claim is under review.",
    "contradicts_file": "Correct every statement that does not match the claim file.",
    "asks_for_all_documents": "Ask for every document listed under documents_needed.",
    "tone": "Acknowledge the customer's situation, including any injury, in a respectful, plain tone.",
}


def problems(answers: dict) -> list[str]:
    found = []
    if answers["promises_outcome"]["noul"] > PROMISE_BAR:
        found.append("promises_outcome")
    if answers["contradicts_file"]["noul"] > CONTRADICTION_BAR:
        found.append("contradicts_file")
    if answers["asks_for_all_documents"]["noul"] < DOCS_FLOOR:
        found.append("asks_for_all_documents")
    if answers["tone"]["score"] < TONE_FLOOR:
        found.append("tone")
    return found


def route(answers: dict, revision: int = 0) -> tuple[str, list[str]]:
    """Returns (action, revision instructions for the LLM)."""
    found = problems(answers)
    if not found:
        return "send", []
    if revision >= MAX_REVISIONS:
        return "person_reviews", [FIXES[p] for p in found]
    return "revise", [FIXES[p] for p in found]
