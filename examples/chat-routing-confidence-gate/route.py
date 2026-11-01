"""Act on confident answers; send the rest to the LLM. Bars are placeholders: set them per task
from your own labelled cases (Entagl used 85% in its test and 90% in its replay)."""

ACTION_BAR = 0.85
STOP_BAR = 0.5  # low on purpose: a missed stop request is the expensive mistake


def route(answers: dict, chat: dict) -> dict:
    stop = answers["stop_contact"].get("noul")
    if stop is not None and stop >= STOP_BAR:
        return {"action": "stop_contact", "by": "decision_model"}
    act = answers["action"]
    confidence = act.get("confidence") or 0.0  # a null confidence counts as unsure
    if confidence < ACTION_BAR:
        return {"action": "llm_review", "by": "llm", "confidence": confidence}
    action = act["choice"]
    # Rules stay in code: a follow-up in an owned chat stays with that specialist,
    # and a customer who already gave contact details is not handed over again.
    if action == "hand_over" and chat.get("contact_already_collected") and chat.get("handed_over"):
        action = "answer"
    return {"action": action, "by": "decision_model", "owner": chat.get("chat_owner"), "confidence": confidence}


def accuracy_by_language(results):
    """results: (language, correct: bool) pairs from your shadow run. An average hides the weak language."""
    totals = {}
    for lang, ok in results:
        n, k = totals.get(lang, (0, 0))
        totals[lang] = (n + 1, k + int(ok))
    return {lang: k / n for lang, (n, k) in totals.items()}
