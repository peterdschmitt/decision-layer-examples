import json
from bar_check import bar_report, pick_bar, misses_by_answer, cost_saved

cases = json.load(open("sample_input.json"))["cases"]
print("bar   share  implied  seen")
for r in bar_report(cases):
    if r["seen"] is None:
        print(f"{r['bar']:.2f}  {r['share']:5.0%}  nothing clears this bar")
    else:
        print(f"{r['bar']:.2f}  {r['share']:5.0%}  {r['implied']:6.1%}  {r['seen']:5.1%}")
best = pick_bar(bar_report(cases), max_wrong=0.07)
if best is None:
    print("no bar meets a 7% limit: keep the LLM on this choice")
else:
    print(f"lowest bar within 7%: {best['bar']:.2f}, decision model takes {best['share']:.0%}")
    print("misses by answer:", misses_by_answer(cases, best["bar"]))
    # made-up prices per answer: decision model 0.4% of the LLM's
    print(f"LLM cost saved: {cost_saved(best['share'], 0.004, 1.0):.0%}")
