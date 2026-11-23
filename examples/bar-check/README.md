# Bar check: set a decision model's bar on your own past cases

**Area:** any small, repeated choice an LLM makes today: sorting messages, spotting refund requests, flagging alerts, picking a code. **Model:** any decision model that returns a percentage per allowed answer (Jev, Gemini Decisions, OpenAI Decisions, Microsoft-Decision-1 and others). **Status:** checked offline with made-up numbers; model calls not yet run by us (expected, not measured).

Full write-up: the Decision Layer post on what "90% sure" means (draft, Nov. 23, 2026).

## The process

1. **Pull a few hundred past cases** for one choice, with the right answers. Include the hard ones, where your own people disagree.
2. **Run the decision model on all of them** and keep its percentages.
3. **For each possible bar, compare three numbers:** the share of cases the decision model would take, the error its own percentages imply, and the error you actually see. In David J Knudson's independent test (Nov. 21, 2026), the seen error above 0.9 was about five times the implied error for Jev, against the majority of five people, but a higher bar always meant fewer mistakes.
4. **Pick the lowest bar with an error you accept,** on enough cases to mean something. Below the bar, the LLM takes the case, as today. If no bar qualifies, keep the LLM on that choice.
5. **Count misses for each answer,** not just overall. One model in Knudson's test called most clear contradictions "neutral".
6. **Ask each case more than once** and measure how often the top answer changes.
7. **Count the saving:** the share above the bar, less the decision model's own price.

## The rules

[`bar_check.py`](bar_check.py):

- **`bar_report`**: per bar, share taken, implied error, seen error.
- **`pick_bar`**: lowest bar within your error limit, with a minimum number of cases; `None` means keep the LLM.
- **`misses_by_answer`**: misses for each right answer, and what was called instead.
- **`flip_rate`**: share of cases whose top answer changed across repeat runs.
- **`cost_saved`**: share of today's LLM cost saved, given the share above the bar and the two prices.

## Try it

    python3 -m unittest -q test_bar_check   # offline, made-up numbers
    python3 run.py                          # 400 made-up cases

## Where it breaks

- The right answers have to be right. If your people disagree on a case, record that rather than forcing one answer.
- Don't tune the bar on the cases you then report. Hold some back and check the bar on those.
- A bar set on one kind of case may not hold when the cases change. Re-run the check when the inputs shift or the model version changes.
