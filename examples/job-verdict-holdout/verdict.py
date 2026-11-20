"""Decide, job by job, whether a decision model can take over from an LLM.

Pattern from Hostinger's test (company report, Oct. 7, 2026): pick the bar on one
set of past examples, lock it, then test on a second set the model has never seen.
Compare against the LLM you run today, and couple the two where the decision model
falls short. Offline and made-up numbers only: expected, not measured.
"""

BARS = [b / 100 for b in range(50, 100)]


def top(probs):
    """The decision model's pick and how sure it was."""
    best = max(probs, key=probs.get)
    return best, probs[best]


def choose_bar(calibration, target=0.95):
    """Lowest bar at which the sure answers on the calibration set are right often enough.

    calibration: list of (probs, right_answer). Returns None if no bar reaches the target.
    """
    picks = [(top(p)[1], top(p)[0] == right) for p, right in calibration]
    for bar in BARS:
        sure = [ok for conf, ok in picks if conf >= bar]
        if sure and sum(sure) / len(sure) >= target:
            return bar
    return None


def answer(probs, llm_answer, bar):
    """Coupled setup: a sure pick stands; an unsure one goes to the LLM."""
    best, conf = top(probs)
    if bar is not None and conf >= bar:
        return best, "decision_model", conf
    return llm_answer, "llm", None


def holdout_report(holdout, bar):
    """Score three setups on the held-out set.

    holdout: list of dicts with keys probs, llm (the current LLM's answer) and right.
    """
    n = len(holdout)
    alone = sum(top(h["probs"])[0] == h["right"] for h in holdout) / n
    llm = sum(h["llm"] == h["right"] for h in holdout) / n
    coupled_answers = [answer(h["probs"], h["llm"], bar) for h in holdout]
    coupled = sum(a[0] == h["right"] for a, h in zip(coupled_answers, holdout)) / n
    share = sum(a[1] == "decision_model" for a in coupled_answers) / n
    return {"decision_model_alone": alone, "llm_alone": llm,
            "coupled": coupled, "decision_model_share": share}


def verdict(report, tolerance=0.02, min_share=0.3):
    """switch, couple or keep_llm, by how far each setup sits from the LLM today.

    tolerance: the accuracy drop you accept (Hostinger took 1.5 points on phishing
    and refused 7.6 on support chats). min_share: below this, coupling saves too little.
    """
    if report["decision_model_alone"] >= report["llm_alone"] - tolerance:
        return "switch"
    if (report["coupled"] >= report["llm_alone"] - tolerance
            and report["decision_model_share"] >= min_share):
        return "couple"
    return "keep_llm"


def cost_cut(decision_cost, llm_cost):
    """Share of cost saved, e.g. 0.021 against 0.09 is about 0.77."""
    return 1 - decision_cost / llm_cost
