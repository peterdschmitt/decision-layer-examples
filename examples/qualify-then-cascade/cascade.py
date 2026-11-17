"""Qualify, then cascade. First measure each LLM decision step against your own labelled data and
move only the ones that clear the bar. Then, for each item, accept the decision model's answer when
it is confident, send the rest to the LLM you already have, and fall back to a rule if both fail.
Every label records which layer made it.

Shape from SellScale's write-up (Sept. 22, 2026) and the "accept when confident, escalate when
unsure" pattern tested by Li, Miao, Krishnan and Padman (arXiv 2609.26550). The code is ours.
"""

REPLACE_BAR = 0.99  # a step already running well on an LLM must match it this often to move
NEW_FEATURE_BAR = 0.96  # a feature that can't ship on an LLM at all may accept a lower bar


def agreement(decide, examples):
    """Share of labelled examples where the decision model's top answer matches the label."""
    hits = 0
    for ex in examples:
        probs = decide(ex["input"])
        hits += max(probs, key=probs.get) == ex["label"]
    return hits / len(examples)


def qualify(steps, decide, bar=REPLACE_BAR):
    """Score every step on its own labelled data. Return (moves, stays) with each step's score."""
    moves, stays = [], []
    for name, step in steps.items():
        score = agreement(decide, step["examples"])
        (moves if score >= step.get("bar", bar) else stays).append((name, round(score, 3)))
    return moves, stays


def cascade(item, decide, llm, rule, threshold=0.9):
    """Decision model first. Confident: accept. Unsure or down: the LLM. LLM fails: the rule.
    Returns (label, source, confidence) so you can see how much work each layer does."""
    try:
        probs = decide(item)
        label = max(probs, key=probs.get)
        if probs[label] >= threshold:
            return label, "decision_model", probs[label]
    except Exception:
        pass
    try:
        return llm(item), "llm", None
    except Exception:
        return rule(item), "rule", None


def share_by_source(results):
    """How much work each layer did: the number to watch when you tune the threshold."""
    counts = {}
    for _, source, _ in results:
        counts[source] = counts.get(source, 0) + 1
    total = len(results) or 1
    return {k: round(v / total, 3) for k, v in sorted(counts.items())}


def speak_or_stay_quiet(messages, decide, write, threshold=0.8):
    """The group-chat shape: the decision model makes one call per new message, and when it
    isn't sure the agent stays quiet. The LLM writes only when the call is "reply"."""
    probs = decide(messages)  # {"stay_quiet": p, "reply": p, "bring_in_teammate": p}
    call = max(probs, key=probs.get)
    if probs[call] < threshold:
        return "stay_quiet", None
    if call == "reply":
        return call, write(messages)
    return call, None
