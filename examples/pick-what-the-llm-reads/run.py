import json
from pick import pick_notes, score_picker, sweep_bar

data = json.load(open("sample_input.json"))
cases = [{"question": c["question"], "notes": list(c["notes"]), "relevant": set(c["relevant"]),
          "probs": c["notes"]} for c in data["cases"]]
by_q = {c["question"]: c["probs"] for c in cases}


def decide(question, chunk):  # stand-in for a decision model call
    return [by_q[question][n] for n in chunk]


bar, s = sweep_bar(cases, decide, min_precision=0.8)
print(f"chosen bar={bar:.2f} precision={s['precision']:.0%} recall={s['recall']:.0%} "
      f"silent_when_nothing_fits={s['silent_when_nothing_fits']:.0%}")
for c in cases:
    print(f"- {c['question']} -> {pick_notes(c['question'], c['notes'], decide, bar) or 'nothing added'}")
