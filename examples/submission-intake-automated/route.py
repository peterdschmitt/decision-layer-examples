"""Decide whether the LLM's fact sheet goes straight to market.

Every fact the decision model judges supported flows through on its own. Only the
specific facts it can't support go to a person, so one doubtful line doesn't hold
up the whole file. Thresholds are placeholders.
"""

SUPPORTED_BAR = 0.85


def route(answers: dict) -> tuple[str, list[str]]:
    """Returns (action, facts a person must confirm)."""
    doubtful = [fact for fact, a in answers.items() if a["noul"] < SUPPORTED_BAR]
    if not doubtful:
        return "send_to_market", []
    return "person_confirms_facts", doubtful
