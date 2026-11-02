"""Put the bar on the safe answer, give every decider its own bar, and compare on the same cases.
Bars are placeholders: set each from your own test cases, then re-check on real ones."""

from dataclasses import dataclass
from typing import Callable

SAFE = "succeeded"


@dataclass
class Decider:
    name: str
    decide: Callable[[str], dict]  # returns {"succeeded": p, "failed": p, "needs_human": p}
    min_safe: float  # its own bar: an LLM's self-reported scores run high, so don't reuse Jev's


def notice(last_message: str, main: Decider, backup: Decider) -> dict:
    """What to tell the user. The bar reads P(succeeded), not the top answer's confidence,
    which drops when the other answers split the rest."""
    for d in (main, backup):
        try:
            probs = d.decide(last_message)
        except Exception:
            continue  # decision model down or erroring: use the backup
        if not probs:  # e.g. a general LLM with no probabilities at all
            continue
        if probs.get(SAFE, 0.0) >= d.min_safe:
            return {"notice": "done", "by": d.name, "p_safe": probs[SAFE]}
        top = max(probs, key=probs.get)
        return {"notice": "failed" if top == "failed" else "needs_you", "by": d.name, "p_safe": probs.get(SAFE, 0.0)}
    return {"notice": "hold", "by": None}  # no decider answered: send nothing rather than a guess


def compare(cases, deciders):
    """cases: (last_message, true_outcome) pairs you wrote, including past mistakes.
    Switch the default only if the new decider is as good on every case type."""
    report = {}
    for d in deciders:
        right, wrong = 0, []
        for text, truth in cases:
            probs = d.decide(text)
            said = SAFE if probs.get(SAFE, 0.0) >= d.min_safe else max(probs, key=probs.get)
            if said == truth:
                right += 1
            else:
                wrong.append(text)
        report[d.name] = {"right": right, "of": len(cases), "wrong": wrong}
    return report
