# Pick what the LLM reads: a decision model chooses the notes

**Area:** any step where an LLM answers from material chosen for it: search results, help-center articles, past tickets, policy pages, code notes. **Model:** any decision model that returns a probability per item (Jev, OpenAI Decisions, Microsoft-Decision-1 and others). **Status:** checked offline with made-up numbers; model calls not yet run by us (expected, not measured).

Full write-up: the Unblocked post on Decision Layer (draft, Nov. 21, 2026).

## The process

1. **Ask about a batch.** Send the question and about 20 notes at once. The decision model returns one percentage per note: the chance it helps answer the question.
2. **Keep only what clears the bar.** Notes above the bar go to the LLM, best first, up to five. If none clears it, add nothing. Unblocked built for that case first (company report, Sept. 22, 2026).
3. **The LLM writes the answer** from the chosen notes, and you record what it read.
4. **Test on a fresh, blind-graded set.** Old logs only show notes the old picker already chose, so they favour it. `log_bias` measures this (Unblocked found 72%).
5. **Tune the bar, not the prompt.** `sweep_bar` finds the bar with the most useful notes found while keeping the share of good picks above your floor.

## The rules

[`pick.py`](pick.py):

- **`pick_notes`**: batch the notes, keep those above the bar, best first, at most five; may be empty.
- **`answer`**: the LLM answers from the chosen notes and returns what it read.
- **`score_picker`**: share of chosen notes that were useful, share of useful notes found, and how often nothing was added when nothing fit.
- **`sweep_bar`**: the bar to lock in.
- **`relative_change`** and **`log_bias`**: the two numbers behind the post's claims.

## Try it

    python3 -m unittest -q test_pick   # offline, made-up numbers
    python3 run.py                     # five made-up questions

## Where it breaks

- The grading set needs people or a separate grader who never saw the picker's choices.
- A low bar lets more wrong notes in; a high one starves the LLM. Re-run `sweep_bar` when your notes change.
- The decision model answers one narrow question about each note. It does not write or summarise anything.
