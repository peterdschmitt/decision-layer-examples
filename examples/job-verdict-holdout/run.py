import json
from verdict import choose_bar, holdout_report, verdict, cost_cut

data = json.load(open("sample_input.json"))
for name, job in data["jobs"].items():
    bar = choose_bar([(p, r) for p, r in job["calibration"]], target=0.95)
    rep = holdout_report(job["holdout"], bar)
    c = job["cost_per_1000"]
    print(f"{name}: bar={bar} " + " ".join(f"{k}={v:.0%}" for k, v in rep.items())
          + f" cost_cut={cost_cut(c['decision_model'], c['llm']):.0%} verdict={verdict(rep)}")
