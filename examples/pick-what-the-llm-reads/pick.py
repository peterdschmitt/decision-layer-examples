"""Let a decision model pick what the LLM reads, and test it without old-log bias.

Pattern from Unblocked's write-up (company report, Sept. 22, 2026): ask the decision
model about a batch of notes at once, keep those above the bar (up to five), and add
nothing when nothing clears it. Judge the new picker on a fresh, blind-graded set,
not on logs the old picker produced. Offline and made-up numbers only: expected,
not measured.
"""


def pick_notes(question, notes, decide, bar=0.5, batch=20, cap=5):
    """Notes above the bar, best first, at most cap. May be empty."""
    scored = []
    for i in range(0, len(notes), batch):
        chunk = notes[i:i + batch]
        probs = decide(question, chunk)  # one percentage per note
        scored += [(p, n) for p, n in zip(probs, chunk) if p >= bar]
    scored.sort(key=lambda pn: pn[0], reverse=True)
    return [n for _, n in scored[:cap]]


def answer(question, notes, decide, llm, bar=0.5):
    """The LLM writes the answer from the chosen notes; return what it read too."""
    chosen = pick_notes(question, notes, decide, bar)
    return llm(question, chosen), chosen


def score_picker(cases, picker):
    """Precision, recall and 'silent when nothing fits' on blind-graded cases.

    cases: list of dicts with question, notes and relevant (set of useful notes).
    picker: function(question, notes) -> chosen notes.
    """
    chosen_total = chosen_good = relevant_total = relevant_found = 0
    empty_cases = empty_and_silent = 0
    for c in cases:
        chosen = picker(c["question"], c["notes"])
        good = [n for n in chosen if n in c["relevant"]]
        chosen_total += len(chosen)
        chosen_good += len(good)
        relevant_total += len(c["relevant"])
        relevant_found += len(good)
        if not c["relevant"]:
            empty_cases += 1
            empty_and_silent += not chosen
    return {
        "precision": chosen_good / chosen_total if chosen_total else 0.0,
        "recall": relevant_found / relevant_total if relevant_total else 0.0,
        "silent_when_nothing_fits": empty_and_silent / empty_cases if empty_cases else 0.0,
    }


def sweep_bar(cases, decide, bars=None, min_precision=0.45):
    """Highest-recall bar whose precision is at least min_precision. Tune this, not the prompt."""
    bars = bars or [b / 20 for b in range(2, 20)]
    best = None
    for bar in bars:
        s = score_picker(cases, lambda q, n: pick_notes(q, n, decide, bar))
        if s["precision"] >= min_precision and (best is None or s["recall"] > best[1]["recall"]):
            best = (bar, s)
    return best


def relative_change(before, after):
    """e.g. 0.348 -> 0.464 is about +0.333; wrong share 0.652 -> 0.536 is about -0.178."""
    return (after - before) / before


def log_bias(opened, injected_before):
    """Share of notes the agent opened that the old picker had injected (Unblocked: 72%).
    A high share means old logs can't fairly grade a new picker."""
    return sum(n in injected_before for n in opened) / len(opened) if opened else 0.0
