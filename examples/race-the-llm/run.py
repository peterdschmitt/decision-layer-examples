import json
from race import scorecard, pick_bar, agreement_floor

log = json.load(open("sample_input.json"))["log"]
for bar in (0.8, 0.9, 0.95):
    s = scorecard(log, bar)
    agree = "n/a" if s["agreement"] is None else f"{s['agreement']:.0%}"
    print(f"bar={bar:.2f} answers={s['answer_rate']:.0%} agreement={agree} llm_calls_saved={s['llm_calls_saved']:.0%}")
bar, s = pick_bar(log, min_agreement=1.0)
print(f"lowest bar with full agreement: {bar:.2f} (saves {s['llm_calls_saved']:.0%} of LLM calls)")
print(f"11 of 11 agreeing still means the true rate could be as low as {agreement_floor(11, 11):.0%}")
