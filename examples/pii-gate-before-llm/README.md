# Screen for personal details first, and send only the flagged ones to the LLM

**Area:** any product that stores AI-written text that could carry personal details: session summaries, call notes, support transcripts, case notes. **Model:** jev-1.14 in the request (PostHog does not say which decision model runs its gate; any decision model that takes yes/no questions about a text works). **Status:** gate and scoring rules checked offline with made-up probabilities; model call not yet run by us (expected, not measured).

Full write-up: How PostHog’s decision model lets 98.7% of session summaries skip the LLM (draft, Decision Layer, Nov. 14, 2026).

## The process

Every summary gets two narrow yes/no questions from the decision model: does it name a real person, and does it show contact details or an ID? If either scores at or above the bar, the LLM rewrites the summary without the details and the decision model checks it again. Otherwise the summary is stored as is and the LLM is never called. If the decision model is down, the summary counts as flagged, so nothing is stored unchecked. A summary still flagged after two rewrites is held for a person.

PostHog runs this shape in production for Replay Vision. It set the bar low, at 0.4, because a false alarm costs one extra LLM call while a miss stores personal data as clean. It says 98.7% of summaries skip the LLM. It gives no volumes, costs or miss rate.

## The rules

[`gate.py`](gate.py):

- **`scrub`**: both questions, the bar, the rewrite and the re-check, with a cap on rewrites.
- **`evaluate`**: on a labelled set, how many summaries skip the LLM, how many clean ones are sent anyway (false alarms), and how many with personal details slip through (misses).
- **`pick_bar`**: the bar with the lowest total cost of mistakes, given what a false alarm and a miss each cost you. Pick it on one batch and check it on another.

## Try it

    python3 -m unittest -q test_gate   # offline, made-up numbers
    python3 run.py                     # score the sample set at 0.40, then pick a bar by cost
    python3 run.py --dry-run           # print the request for one summary

## Where it breaks

- A bar set on one model version may not hold on the next. PostHog found its bars moved between versions of the same model, and ran the new one in shadow while it re-set them on hand-checked data.
- Narrow questions beat one broad one. PostHog says two narrow questions cut false flags to about a tenth of what a single question produced.
- Text that needs several steps of reasoning, or a long context, belongs with the LLM.
