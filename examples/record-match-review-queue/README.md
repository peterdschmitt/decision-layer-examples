# Same donor or not? A decision model decides, an LLM reviews only the least sure

**Area:** any business with duplicate records (customers, suppliers, donors, patients). **Model:** jev-1.13.0, the version Southbridge AI tested. **Status:** decision rules checked offline with made-up probabilities; model call not yet run by us (expected, not measured). The sample pair uses Southbridge's example names with a made-up address.

Full write-up: [How a data company cut the cost of matching records 86% with a decision model](https://decision-layer-indol.vercel.app/blog/southbridge-record-matching-decision-model/).

## The process, fully automated

Code groups records that look alike. A decision model answers one question per pair: same donor, different donor, or unsure, with a probability for each. The pairs it is least sure of go to an LLM for review. Every answer that changes a record must clear a bar; anything below it is held.

In Southbridge's test on 200 hard groups of Ohio campaign-finance records, this shape matched the LLMs-alone score (199 of 200) at 86% lower cost. Its one remaining mistake was a 53% guess with no bar. This example adds the bar.

## The question

| Question | Type | Why |
|---|---|---|
| `identity` | Choice: same, different, unsure | The criteria say what *counts* as enough evidence. Southbridge's first wording listed what didn't count, and the model said no to every household question on its practice set. |

## The rules

[`decide.py`](decide.py):

- **Review only the least sure.** Rank by "unsure" first, then the lowest top probability. Southbridge found five reviews worked; ten fixed one more group and broke another.
- **The LLM sees the records, not the decision model's answer.** So it reviews independently.
- **A bar on every answer that changes a record.** Below it, or an "unsure" top answer: hold.
- **Decision model down:** the pair goes to the front of the review queue.
- **Score holds apart from wrong answers.** A hold costs a review; a wrong merge puts one person's history on another's record.

## Try it

    python3 -m unittest -q test_decide   # offline, made-up probabilities
    python3 run.py --dry-run             # print the request for the sample pair

## Where it breaks

- Southbridge's answer key was built with AI models and checked by hand where setups disagreed. Build your own key from your records.
- If many pairs come back unsure, savings shrink. YTAL sent whole batches back to its old LLM process and its total cost rose about 4%. Send single pairs, not batches.
- Pin the version you tested and re-test before moving.
