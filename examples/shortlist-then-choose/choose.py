"""Shortlist, then choose. A cheap search narrows thousands of categories to a short list.
A decision model picks one from that list and says how sure it is. Unsure items go to the LLM
you already use, so you always know which answers were sure.

Shape from Channel3's write-up (Evan Fenster, Oct. 5, 2026): embedding search returned the top 30
categories, and Jev picked from them, at 97.2% accuracy against 81.9% for the LLM that did that step
before. Channel3 did not describe an LLM step for unsure items; that part is ours. The code is ours.
"""

import math

NONE = "none of these"
BAR = 0.8  # how sure the decision model must be to decide on its own


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def shortlist(item_vec, category_vecs, k=30):
    """Cheap step: the k categories closest to the item. Aim for the right one to be in here."""
    ranked = sorted(category_vecs, key=lambda c: cosine(item_vec, category_vecs[c]), reverse=True)
    return ranked[:k]


def choose(item, options, decide, llm_pick, bar=BAR):
    """Decision model picks from the short list, with "none of these" allowed.
    Sure: take it. Unsure, "none", or down: the LLM picks. Returns (category, source, confidence)."""
    try:
        probs = decide(item, list(options) + [NONE])
        best = max(probs, key=probs.get)
        if best != NONE and probs[best] >= bar:
            return best, "decision_model", probs[best]
    except Exception:
        pass
    return llm_pick(item, options), "llm", None


def recall_at_k(items, truth, shortlists):
    """How often the right category made the short list. If this is low, no picker can fix it."""
    hits = sum(truth[i] in shortlists[i] for i in items)
    return round(hits / (len(items) or 1), 3)


def accuracy(results, truth):
    right = sum(results[i][0] == truth[i] for i in results)
    return round(right / (len(results) or 1), 3)


def error_cut(before_acc, after_acc):
    """Share of errors removed: 81.9% -> 97.2% accuracy removes about 85% of errors."""
    before_err, after_err = 1 - before_acc, 1 - after_acc
    return round(1 - after_err / before_err, 3) if before_err else 0.0


def share_by_source(results):
    counts = {}
    for _, src, _ in results.values():
        counts[src] = counts.get(src, 0) + 1
    n = len(results) or 1
    return {k: round(v / n, 3) for k, v in sorted(counts.items())}
