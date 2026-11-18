# Route and set effort: a decision model decides where each request goes and how hard the LLM works

**Area:** any assistant or agent product with more than one way to handle a request: answer in chat or hand to an agent that acts, a small model or a big one, a quick pass or a deep one. **Model:** any decision model that returns a probability per answer (Microsoft-Decision-1.1, Jev, OpenAI Decisions, Gemini Decision 1, Clef and others). **Status:** checked offline with made-up numbers; model calls not yet run by us (expected, not measured).

Full write-up: the Microsoft Copilot takeaways post on Decision Layer (draft, Nov. 18, 2026).

## The process

1. **Before switching, compare.** Run the decision model on past requests your current LLM router already handled. Measure how often it picks the same route, and how many it would decide on its own at your bar. Microsoft says its decision model makes the Copilot-or-Cowork call "as accurately as a large language model, 2.2x faster and at 4.4x lower cost" (company report, Nov. 17, 2026).
2. **Route.** For each new request, the decision model answers "chat or agent?". Sure: take its route. Unsure: ask the LLM router you already have. Both down: a default.
3. **Set effort.** The decision model answers "low, medium or high effort?". Unsure: go one level up.
4. **Hand off.** The chosen LLM does the work at the chosen effort. Every record keeps who made each call and how sure it was.

## The rules

[`route.py`](route.py):

- **`choose_route`**: decision model, then the LLM router, then a default; returns the route, its source and the confidence.
- **`choose_effort`**: decision model; steps up one level when unsure.
- **`handle`**: both calls, then the hand-off to the LLM that does the work.
- **`agreement_with_llm`**: same-route rate and share decided alone, on past requests.
- **`share_by_source`**: how much of the routing the decision model did.

## Try it

    python3 -m unittest -q test_route   # offline, made-up numbers
    python3 run.py                      # route six made-up requests

## Where it breaks

- The options must be fixed and few. If a request fits none of them, add "none of these" and send it to the LLM router.
- Agreement with an LLM router is not the same as being right. Check a sample of disagreements by hand before you switch.
- Microsoft has not published its routing code, its volumes or the LLM it compared against. This is our version of the shape it describes.
