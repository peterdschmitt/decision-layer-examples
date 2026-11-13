# Judge the pages, and say "not found" before the LLM guesses

**Area:** any product that answers known questions from documents: extraction tables, review checklists, due-diligence questionnaires, claims and contract review. **Model:** jev-1.14 in the request (Subworkflow tested TypeSafe's jev-1.14; any decision model that takes a yes/no question about a page image works). **Status:** answer and scoring rules checked offline with made-up probabilities; model call not yet run by us (expected, not measured).

Full write-up: How a document startup kept its LLM from guessing at missing answers with a decision model (draft, Decision Layer, Nov. 13, 2026).

## The process

Search shortlists pages for each question. The decision model judges each page: does it answer this question? The LLM reads the best six pages and writes the answer, as before. If no page clears the bar, the answer is "not found" and the LLM is never asked. If the decision model is down, the LLM reads search's pages, as before.

Subworkflow ran this on a made-up 300-page legal file: an answer page came first on 19 of 20 questions (12 for search alone), and 8 of 10 absent questions were marked "not found" with no real answer blanked. Two near-miss traps fooled the judge; the LLM still read those pages. Nothing has shipped.

## The rules

[`judge.py`](judge.py):

- **`answer_question`**: rank the shortlist by the decision model's chance, "not found" below the bar, the LLM reads the top six.
- **`evaluate`**: on a test set with known answers, how often an answer page comes first, how many absent questions are caught, and how many real answers are wrongly blanked.
- **`pick_bar`**: the highest bar that blanks no real answer. Pick it on one batch and check it on another.

## Try it

    python3 -m unittest -q test_judge   # offline, made-up numbers
    python3 run.py                      # score the sample test set
    python3 run.py --dry-run            # print the request for one page

## Where it breaks

- Questions about something very like what is in the file (an agreement with a similar name, a proposal that was never accepted) can score high. Keep the LLM reading the pages so it can decline.
- If questions arrive live, as in a chatbot, you still need search.
- Read the decision model vendor's data terms before any client file goes in. Subworkflow would not send customer documents to Jev under TypeSafe's telemetry clause without clarity in writing.
