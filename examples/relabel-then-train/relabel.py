"""Relabel, then train: clean the examples a decision model learns from.

A trained decision model relabels every example. An LLM labels the same
examples on its own. Where both agree, the example passes with their
answer (corrected when both say the old answer was wrong). Disagreements and
unsure cases go to people, whose rulings are logged with the rule they
used. Then two checks every deployment needs: the both-calls-right score
and the shuffle test.

Expected, not measured: the model calls are stand-ins here.
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple
import random


def top(probs: Dict[str, float]) -> Tuple[str, float]:
    best = max(probs, key=probs.get)
    return best, probs[best]


def triage(examples, decide: Callable, llm_label: Callable, unsure=0.4):
    """Returns (keep, to_people). Each example: {'id','state','question','label'}."""
    keep, to_people = [], []
    for ex in examples:
        answer, p = top(decide(ex["state"], ex["question"]))
        second = llm_label(ex["state"], ex["question"])
        if p < unsure:
            to_people.append((ex, "decision model unsure", answer, second))
        elif answer != second:
            to_people.append((ex, "the two models disagree", answer, second))
        elif answer != ex["label"]:
            keep.append({**ex, "label": answer, "relabelled": True})  # both say the old answer was wrong
        else:
            keep.append(ex)
    return keep, to_people


@dataclass
class Ruling:
    example_id: str
    label: str
    rule: str          # which written rule decided it
    note: str = ""


@dataclass
class RulingLog:
    rulings: List[Ruling] = field(default_factory=list)

    def settle(self, ex, label, rule, note=""):
        self.rulings.append(Ruling(ex["id"], label, rule, note))
        return {**ex, "label": label, "settled_by_person": True}

    def rules_needing_wording(self, min_count=2) -> List[str]:
        """Rules cited again and again in disputes are the ones to rewrite."""
        counts: Dict[str, int] = {}
        for r in self.rulings:
            counts[r.rule] = counts.get(r.rule, 0) + 1
        return sorted(k for k, v in counts.items() if v >= min_count)


def both_right(records, predict: Callable) -> float:
    """Share of requests where every question was answered right (joint accuracy)."""
    if not records:
        return 0.0
    ok = 0
    for r in records:
        answers = predict(r["state"])
        ok += all(answers[q] == r["labels"][q] for q in r["labels"])
    return ok / len(records)


def shuffle_flip_rate(records, decide_with_options: Callable, seed=0) -> float:
    """Share of answers that change when the options are presented in another order."""
    rng = random.Random(seed)
    flips = total = 0
    for r in records:
        for q, options in r["options"].items():
            a, _ = top(decide_with_options(r["state"], q, list(options)))
            shuffled = list(options)
            rng.shuffle(shuffled)
            b, _ = top(decide_with_options(r["state"], q, shuffled))
            flips += a != b
            total += 1
    return flips / total if total else 0.0
