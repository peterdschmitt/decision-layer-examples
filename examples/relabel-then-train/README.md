# Relabel, then train: clean the examples before you train a decision model

**Area:** any company training or tuning a decision model on its own past decisions: an assistant's first calls (where a request goes, what the user wants), ticket routing, document sorting, claims intake. **Model:** a decision model that returns a percentage per allowed answer, plus an LLM for a second opinion. **Status:** checked offline with made-up data; model calls not yet run by us (expected, not measured).

Full write-up: the Decision Layer post on QQ Music (draft, Nov. 26, 2026).

## The process

1. **Test ready-made decision models first** on your own real requests, with your rules written into the answers.
2. **Look at the confident misses.** In Tencent's report for QQ Music, staff found that 35–40% of a batch of confident "mistakes" were wrong answers in the data, not in the model.
3. **Relabel every example twice:** once by a trained decision model, once by an LLM on its own.
4. **Keep what both agree on,** with their answer. Where both say the old answer was wrong, it is corrected. The decision model's very sure disagreements are the ones to study first, as Tencent did.
5. **Send disagreements and unsure cases to people,** who rule using the written rules. Log which rule decided each one. Rules that keep coming up need clearer wording.
6. **Train, then score two things:** the share of requests with every call right, and how often an answer changes when the options are shuffled.

## The parts

[`relabel.py`](relabel.py):

- **`triage`**: keep, correct or send each example to people.
- **`RulingLog`**: people's rulings, and the rules that need rewording.
- **`both_right`**: share of requests with every question answered right.
- **`shuffle_flip_rate`**: share of answers that change when the options are reordered.

## Try it

    python3 -m unittest -q test_relabel   # offline, made-up data
    python3 run.py                        # four made-up music requests

## Where it breaks

- If the LLM and the decision model share a blind spot, both can agree on a wrong answer. Sample the agreed set too.
- Cleaning the test set with the same models flatters the score. Keep a set that people labelled from scratch.
- A shuffle test with few options says little. Use your real option lists.
