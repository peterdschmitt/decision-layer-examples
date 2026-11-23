"""Set a decision model's bar on your own past cases.

A decision model returns a percentage for each allowed answer. Its own numbers
imply an error rate, but on hard cases the real rate can be several times higher
(David J Knudson's independent test, Nov. 21, 2026). So measure, for each bar:
the share of cases the decision model would take, the error its numbers imply and
the error you actually see. Cases below the bar go to the LLM, as today.

Expected, not measured: checked offline with made-up numbers only.
"""
from collections import Counter

DEFAULT_BARS = (0.5, 0.7, 0.8, 0.9, 0.95, 0.99)


def top(probs):
    """The decision model's pick and its percentage (as 0-1)."""
    label = max(probs, key=probs.get)
    return label, probs[label]


def bar_report(cases, bars=DEFAULT_BARS):
    """cases: list of dicts with 'probs' (answer -> 0-1) and 'truth' (the right answer).

    Returns one row per bar: share taken, implied error, seen error (None when nothing clears).
    """
    if not cases:
        raise ValueError("need at least one case")
    rows = []
    for bar in bars:
        kept = [c for c in cases if top(c["probs"])[1] >= bar]
        if not kept:
            rows.append({"bar": bar, "share": 0.0, "implied": None, "seen": None, "kept": 0})
            continue
        implied = sum(1 - top(c["probs"])[1] for c in kept) / len(kept)
        seen = sum(top(c["probs"])[0] != c["truth"] for c in kept) / len(kept)
        rows.append({"bar": bar, "share": len(kept) / len(cases), "implied": implied,
                     "seen": seen, "kept": len(kept)})
    return rows


def pick_bar(rows, max_wrong=0.05, min_kept=30):
    """Lowest bar whose seen error is within your limit, on enough cases to mean something.

    Returns None when no bar qualifies: keep the LLM on this choice.
    """
    ok = [r for r in rows if r["seen"] is not None and r["kept"] >= min_kept and r["seen"] <= max_wrong]
    return min(ok, key=lambda r: r["bar"]) if ok else None


def misses_by_answer(cases, bar):
    """For cases that clear the bar: how often each right answer was missed.

    One overall score can hide a pattern, such as one answer almost always called
    something else (Knudson found one model calling most clear contradictions 'neutral').
    """
    total, missed, called = Counter(), Counter(), {}
    for c in cases:
        label, p = top(c["probs"])
        if p < bar:
            continue
        total[c["truth"]] += 1
        if label != c["truth"]:
            missed[c["truth"]] += 1
            called.setdefault(c["truth"], Counter())[label] += 1
    return {t: {"cases": n, "missed": missed[t], "miss_rate": missed[t] / n,
                "called_instead": dict(called.get(t, {}))} for t, n in total.items()}


def flip_rate(repeats):
    """repeats: list of lists, the same case asked several times (each item a probs dict).

    Returns the share of cases whose top answer changed between runs.
    """
    if not repeats:
        return 0.0
    flips = sum(len({top(p)[0] for p in runs}) > 1 for runs in repeats)
    return flips / len(repeats)


def cost_saved(share, dm_price, llm_price):
    """Share of today's LLM cost saved when the decision model answers every case
    and the LLM takes only the cases below the bar.

    Prices are per answer, in any one currency.
    """
    if llm_price <= 0:
        raise ValueError("llm_price must be positive")
    new = dm_price + (1 - share) * llm_price
    return 1 - new / llm_price
