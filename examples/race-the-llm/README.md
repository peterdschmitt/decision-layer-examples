# Race the LLM: a decision model answers first when it is sure

**Area:** any small, repeated choice an LLM makes before the real work: sorting chat messages, picking a form, choosing a code from a short list. **Model:** any decision model that returns a probability per allowed answer (Jev, OpenAI Decisions, Microsoft-Decision-1.1 and others). **Status:** checked offline with made-up numbers; model calls not yet run by us (expected, not measured).

Full write-up: the Decision Layer post on two teams that put a decision model beside their LLM (draft, Nov. 22, 2026).

## The process

1. **Start both at once.** The LLM starts on every message, as before. The decision model answers the same fixed question at the same time.
2. **Use the fast answer only when it clears the bar.** Then cancel the LLM call. Otherwise, the LLM's answer arrives when it always did, so the worst case is today's wait. Alvar Laigna used this design at RTK, Estonia (company report, Sept. 29, 2026).
3. **Keep a switch for each choice:** `live`, `shadow` (background only, nothing acts on it) or `off`.
4. **Score it in shadow first.** Track how often the decision model is sure, how often it agrees with the LLM, and how many LLM calls a live run would save. Tabbit's gate design sent about 98% of steps to the LLM anyway (company test, Nov. 2026), so single-step accuracy alone says little.
5. **Pick the bar by the cost of a wrong answer,** then go live.

## The rules

[`race.py`](race.py):

- **`route`**: the race, with a time limit; the decision model being slow or down means the usual path.
- **`scorecard`**: answer rate, agreement with the LLM, LLM calls saved, from a shadow log.
- **`pick_bar`**: the lowest bar whose sure answers agree often enough.
- **`agreement_floor`**: how low the true agreement rate could be when every sure answer agreed (11 of 11 gives about 72%).

## Try it

    python3 -m unittest -q test_race   # offline, made-up numbers
    python3 run.py                     # a made-up shadow log

## Where it breaks

- Agreement with the LLM is not correctness. Grade a sample by hand before trusting either.
- Short, context-heavy replies ("ok", "sobis") belong with the LLM.
- Ask the decision model about what is visible in the message, not about abstract ideas.
