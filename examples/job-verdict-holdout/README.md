# Job verdict on a held-out set: switch, couple, or keep the LLM

**Area:** any small, repeated choice an LLM makes today: phishing checks, ticket or chat sorting, spam, routing, safety checks. **Model:** any decision model that returns a probability per allowed answer (Jev, OpenAI Decisions, Gemini Decision 1, Microsoft-Decision-1.1 and others). **Status:** checked offline with made-up numbers; model calls not yet run by us (expected, not measured).

Full write-up: the Hostinger verdict essay on Decision Layer (draft, Nov. 20, 2026).

## The process

1. **Pick the bar on one set.** On past items with known answers, find the lowest bar at which the decision model's sure answers are right often enough. Lock it in. Hostinger used this method on its phishing test (company report, Oct. 7, 2026).
2. **Test on a second set.** Score three setups on items the bar was not tuned on: the decision model alone, the LLM you run today, and the two coupled (sure answers stand, unsure ones go to the LLM).
3. **Give each job a verdict.** `switch` if the decision model alone is within your accepted gap of the LLM. `couple` if the coupled setup is, and the decision model handles enough of the work to matter. Otherwise `keep_llm`.
4. **Count the saving.** `cost_cut` turns two prices into a share saved. Hostinger's figures give about 77% on phishing (against an estimated price) and about 82% on support chats.

## The rules

[`verdict.py`](verdict.py):

- **`choose_bar`**: lowest bar where sure answers on the calibration set hit the target.
- **`answer`**: the coupled setup; a sure pick stands, an unsure one goes to the LLM.
- **`holdout_report`**: accuracy of each setup on the held-out set, and the decision model's share of the work.
- **`verdict`**: switch, couple or keep_llm, with an accepted gap (Hostinger took 1.5 points on phishing and refused 7.6 on support chats).
- **`cost_cut`**: share of cost saved.

## Try it

    python3 -m unittest -q test_verdict   # offline, made-up numbers
    python3 run.py                        # two made-up jobs

## Where it breaks

- Don't nudge the bar on test results. If too many wrong answers get through, rebuild the calibration set, as Hostinger advises.
- Each unsure answer sent to the LLM costs what it costs today, so the saving shrinks as the LLM's share grows.
- A decision model works on small, clear questions. Break a big job into narrow ones before you test it.
