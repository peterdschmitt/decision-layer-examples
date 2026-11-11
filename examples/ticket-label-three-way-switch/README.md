# Moving a labelling job from an LLM to a decision model: the three-way switch

**Area:** IT, operations and support teams that sort tickets, requests or alerts into a fixed list. **Model:** jev-1.13.0 in the request (Amazon used AWS's Strands Decider; any decision model that takes a choice question works). **Status:** switch and report rules checked offline with made-up probabilities; model call not yet run by us (expected, not measured). The labels and the sample ticket are made up.

Full write-up: How Amazon cut the cost of sorting internal tickets 98% with a decision model (draft, Decision Layer, Nov. 11, 2026).

## The process, fully automated

A setting has three positions. **llm**: the old way. **both**: both models label every live ticket; the LLM's label is used and the decision model's is logged next to it. **decision_model**: the decision model labels every ticket it is sure of; everything below the bar, and every "none", goes to the LLM.

Amazon's engineers ran this switch on one of the world's largest internal ticketing systems and report 98% lower cost per ticket and 78% less time per call. They did not publish an accuracy figure or say what happens below their bar. Sending those tickets to the LLM is our choice.

## The question

| Question | Type | Why |
|---|---|---|
| `label` | Choice: your labels plus "none" | Each label is one or two plain sentences, as Amazon did when its LLM descriptions were too long. Keys are sorted, because field order alone moved Amazon's probabilities by up to 0.19. |

## The rules

[`switch.py`](switch.py):

- **`label_ticket`**: the three-way switch. Decision model down: the LLM labels it, as before.
- **`side_by_side_report`**: from the "both" log, the share of tickets above the bar, how often the decision model agrees with the LLM there, and the list of disagreements.
- **`ready_to_switch`**: switch only when agreement above the bar is high enough and every disagreement has been read by a person.

## Try it

    python3 -m unittest -q test_switch   # offline, made-up probabilities
    python3 run.py --dry-run             # print the request for the sample ticket

## Where it breaks

- If a label needs a written explanation, if the label list changes every week, or if the useful part of a ticket doesn't fit in a few thousand tokens, keep the LLM. These are the Amazon engineers' own limits.
- Agreement with the LLM is not accuracy. Read the disagreements and decide who was right.
- Pin the version you tested and re-test before moving.
