# Shortlist, then choose: a cheap search narrows the list, a decision model picks, the LLM takes the unsure ones

**Area:** any job that files items into a large list of categories: product catalogs, expense and ledger codes, support topics, medical or legal codes, document types. **Model:** any decision model that picks from a supplied list and returns a probability per option (Jev, OpenAI Decisions, Gemini Decision 1, Microsoft-Decision-1.1 and others). **Status:** checked offline with made-up numbers; model calls not yet run by us (expected, not measured).

Full write-up: the Channel3 story on Decision Layer (draft, Nov. 19, 2026).

## The process

1. **Shortlist.** A cheap search (an embedding index of your categories) returns the closest 30. Measure how often the right category makes the list. Channel3 found the top match alone was right under 40% of the time, but the top 30 held it over 99% of the time.
2. **Choose.** The decision model picks one category from the short list, with "none of these" allowed, and says how sure it is. Channel3 reported 97.2% accuracy at this step, against 81.9% for the LLM it used before, at about the same cost (company report, Oct. 5, 2026).
3. **Hand off the unsure ones.** Below your bar, or on "none of these", the LLM you already use picks. This step is ours; Channel3 did not describe it.
4. **Record who chose.** Every result keeps its source and confidence.

## The rules

[`choose.py`](choose.py):

- **`shortlist`**: the k closest categories by cosine similarity.
- **`choose`**: decision model first; unsure, "none" or down goes to the LLM.
- **`recall_at_k`**: how often the right category made the short list.
- **`accuracy`**, **`error_cut`**: compare before and after (81.9% to 97.2% removes about 85% of errors).
- **`share_by_source`**: how much of the work the decision model did.

## Try it

    python3 -m unittest -q test_choose   # offline, made-up numbers
    python3 run.py                       # five made-up products

## Where it breaks

- Don't ask the decision model to walk the category tree level by level. Channel3 tried it, and a youth bicycle ended up under motor vehicles because the right path scored low near the top.
- Don't score every category one by one. Channel3 found that reached 98.0% but would have cost about 2,000 times its current setup.
- Against a cheap open model run in batches, the saving is small. Channel3 says its costs were nearly identical; the gain was accuracy.
