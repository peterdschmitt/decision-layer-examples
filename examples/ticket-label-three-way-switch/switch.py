"""A three-way switch for moving a job from an LLM to a decision model:
"llm" (the old way), "both" (side by side: the LLM's label is used, the decision model's is logged),
and "decision_model" (the decision model acts above the bar; everything below goes to the LLM).

Amazon's post does not say what happens below its bar. Sending those tickets to the LLM is our choice.
"""

BAR = 0.80  # placeholder: set it from your own side-by-side log


def label_ticket(ticket, mode, decide, llm_label, log=None, bar=BAR):
    if mode == "llm":
        return llm_label(ticket), "llm"
    try:
        probs = decide(ticket)
    except Exception:
        return llm_label(ticket), "llm"  # decision model down: the LLM labels it, as before
    top = max(probs, key=probs.get)
    if mode == "both":
        label = llm_label(ticket)
        if log is not None:
            log.append({"ticket": ticket.get("id"), "llm": label, "decision_model": top, "sure": probs[top]})
        return label, "llm"
    if mode == "decision_model" and probs[top] >= bar and top != "none":
        return top, "decision_model"
    return llm_label(ticket), "llm"  # below the bar, or "none": the LLM labels it


def side_by_side_report(log, bar=BAR):
    """From the 'both' log: how much the decision model would handle above the bar,
    how often it agrees with the LLM there, and the disagreements to read by hand."""
    above = [r for r in log if r["sure"] >= bar and r["decision_model"] != "none"]
    agree = [r for r in above if r["decision_model"] == r["llm"]]
    return {
        "share_above_bar": len(above) / len(log) if log else 0.0,
        "agreement_above_bar": len(agree) / len(above) if above else 0.0,
        "disagreements": [r for r in above if r["decision_model"] != r["llm"]],
    }


def ready_to_switch(report, min_agreement=0.98, max_unread=0, read=()):
    """Switch only when agreement above the bar is high enough AND every disagreement has been read."""
    unread = [d for d in report["disagreements"] if d["ticket"] not in set(read)]
    return report["agreement_above_bar"] >= min_agreement and len(unread) <= max_unread
