"""Race a decision model against the LLM; use the fast answer only when it is sure.

Pattern from Alvar Laigna's write-up of a proof of concept at RTK, Estonia (company
report, Sept. 29, 2026): both models start on each message at the same moment. If the
decision model clears the bar, its answer is used and the LLM call is cancelled. If it
is unsure, slow or down, the LLM's answer arrives when it always did. Each choice can
run live, in shadow (background only) or off. Offline and made-up numbers only:
expected, not measured.
"""
import asyncio

MODES = ("live", "shadow", "off")


async def route(message, decide, llm_plan, bar=0.9, mode="live", timeout=2.0, log=None):
    """Return (answer, who). who is 'decision model' or 'llm'."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    plan = asyncio.create_task(llm_plan(message))  # the LLM starts at once, as before
    if mode == "off":
        return await plan, "llm"
    try:
        label, prob = await asyncio.wait_for(decide(message), timeout=timeout)
    except Exception:
        return await plan, "llm"  # decision model slow or down: the usual path
    if mode == "live" and prob >= bar:
        plan.cancel()  # sure enough: use the fast answer and stop the LLM
        if log is not None:
            log.append({"message": message, "label": label, "prob": prob, "llm": None})
        return label, "decision model"
    answer = await plan  # unsure, or shadow: the LLM's answer, on its usual time
    if log is not None:
        log.append({"message": message, "label": label, "prob": prob, "llm": answer})
    return answer, "llm"


def scorecard(log, bar):
    """The two numbers that matter, from shadow runs where both answers are known.

    answer_rate: share of messages where the decision model clears the bar.
    agreement: of those, share where it matches the LLM (agreement, not correctness).
    llm_calls_saved: share of LLM calls a live run at this bar would cancel.
    """
    both = [r for r in log if r["llm"] is not None]
    if not both:
        return {"answer_rate": 0.0, "agreement": None, "llm_calls_saved": 0.0}
    sure = [r for r in both if r["prob"] >= bar]
    agree = sum(r["label"] == r["llm"] for r in sure)
    return {
        "answer_rate": len(sure) / len(both),
        "agreement": agree / len(sure) if sure else None,
        "llm_calls_saved": len(sure) / len(both),
    }


def agreement_floor(agree, n):
    """Lower end of an exact 95% interval when every one of n sure answers agreed.

    Laigna's 11 of 11 gives about 0.715: the true rate could be as low as ~72%.
    Only valid for agree == n.
    """
    if agree != n or n == 0:
        raise ValueError("only for all-agree samples")
    return 0.025 ** (1 / n)


def pick_bar(log, min_agreement=0.95, bars=None):
    """Lowest bar whose sure answers agree with the LLM often enough (most calls saved)."""
    bars = bars or [b / 100 for b in range(50, 100)]
    for bar in bars:
        s = scorecard(log, bar)
        if s["agreement"] is not None and s["agreement"] >= min_agreement:
            return bar, s
    return None
