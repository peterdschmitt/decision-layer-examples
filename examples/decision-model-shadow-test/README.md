# Choosing a decision model: the shadow test

**Area:** any repeated decision an LLM makes today (here: is this support ticket urgent?). **Model:** jev-1.14.0 plus any candidate that accepts the same request format. **Status:** routing and scoring rules checked offline on made-up numbers; model calls not yet run by us (expected, not measured).

Full write-up: [How to pick a decision model: the price barely matters, the mistakes do](https://decision-layer-indol.vercel.app/blog/choosing-a-decision-model/).

## The process, fully automated

The decision model answers one yes-or-no question with a probability. Above your bar, the process acts on its own (page the on-call team, or send the ticket to the normal queue). Inside the unsure band, the ticket goes to the LLM, as today.

Before you switch, run two or three candidate decision models in shadow next to your current LLM, log every probability, and score each one on your own labelled cases. This folder does the scoring.

## The question

| Question | Type | Why |
|---|---|---|
| `urgent` | Noul (yes/no) | The decision itself. The probability is what you set the bar on. |

[`request.py`](request.py) builds the same body for every candidate; only `model` changes. Cloudflare says Clef accepts the Jev request format; check each candidate's docs.

## The rules

[`route.py`](route.py):

- `route`: probability at or above the bar pages on-call; at or below 1 − bar goes to the normal queue; anything in between, or no answer, goes to the LLM
- `shadow_test`: for one candidate's logged probabilities and your labels, the share of cases it would handle without the LLM, how often it is wrong when it acts, and how many urgent tickets it would have sent to the normal queue (the expensive mistake)
- `pick_bar`: the lowest bar whose error rate when acting stays under your limit and that never misses an urgent ticket

## Try it offline

    python3 compare.py                # made-up numbers in sample_cases.json
    python3 compare.py my_cases.json   # your own logged probabilities and labels
    python3 run.py --dry-run           # print the request for the sample ticket

The tests show the lesson from Construct's benchmark: a bar that suits one model can make a second model look useless. Set each model's bar from its own answers.

## Where it breaks

- A few hundred cases is a start, not proof. Include the hard and expensive ones on purpose.
- Bars picked and scored on the same cases flatter every model. Hold some cases back to check.
- Hosted models can change under the same name. Re-run a fixed set of cases on a schedule and alert when probabilities move.
- Keep fixed rules (numeric limits, severity policy) in ordinary code; ask the model only what needs reading.
