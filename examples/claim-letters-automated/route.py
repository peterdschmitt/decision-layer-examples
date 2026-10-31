"""Decide whether the LLM's letter is sent automatically.

The decision model's answers turn the LLM's draft into something the process
can act on: send it now, or hand it to an adjuster with the reasons attached.
Thresholds are placeholders; they are the dials that set your automation rate.
"""

PROMISE_BAR = 0.2      # low: a wrong promise is the costliest mistake
CONTRADICTION_BAR = 0.3
DOCS_FLOOR = 0.7
TONE_FLOOR = 1.4       # 0 to 2

REASONS = {
    "promises_outcome": "Promises payment, coverage or an outcome the file doesn't confirm",
    "contradicts_file": "Says something that doesn't match the claim file",
    "asks_for_all_documents": "Doesn't ask for every document the file needs",
    "tone": "Tone isn't right for this customer",
}


def route(answers: dict) -> tuple[str, list[str]]:
    """Returns (action, reasons an adjuster should see)."""
    found = []
    if answers["promises_outcome"]["noul"] > PROMISE_BAR:
        found.append("promises_outcome")
    if answers["contradicts_file"]["noul"] > CONTRADICTION_BAR:
        found.append("contradicts_file")
    if answers["asks_for_all_documents"]["noul"] < DOCS_FLOOR:
        found.append("asks_for_all_documents")
    if answers["tone"]["score"] < TONE_FLOOR:
        found.append("tone")
    if not found:
        return "send_automatically", []
    return "adjuster_sends", [REASONS[f] for f in found]
