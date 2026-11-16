# Choose, then write: the decision model routes each item, a cheaper LLM writes the result

**Area:** any inbox where the same item arrives from several senders under slightly different names, and each one must go to one owner or be dropped: school and household letters, support and sales inboxes, invoices and statements, regulatory notices. **Model:** gemini-decision-1 in the request (any decision model that takes shared rules plus many choice questions works). **Status:** routing, rules and dry-run diff checked offline with made-up numbers; model calls not yet run by us (expected, not measured).

Full write-up: the household-calendar story on Decision Layer (draft, Nov. 16, 2026).

## The process

An LLM pulls events out of each letter. The decision model then answers one choice question per event: which calendar does it go on, or should it be dropped? All the questions go in one request, and the shared rules go in once. A cheaper LLM merges the repeats and writes the names and notes. Code does the calendar math.

A parent in Hokkaido described this design on Zenn (Nov. 15, 2026). The old setup had one LLM do everything in one call. A straight swap to the decision model alone was cheapest, but the names and notes got worse, because the old LLM had quietly been merging, naming and writing notes too. The parent kept a cheap LLM for that writing. Their reported cost per run fell from about ¥10 to about ¥3.

## The rules

[`route.py`](route.py):

- **`add_calendar_flags`**: weekday and holiday come from code (jpholiday when installed), and holiday names are removed before the model sees them. A model with no reasoning step won't know that a given Monday is a substitute holiday.
- **`route`**: drop an item only when the chance of "drop" is 50% or more, so a missed pool day is rarer than an extra event. Either step failing runs the old LLM-only path. Anything the LLM leaves out of its merge goes back in as is.
- **`newest_document_wins`**: when the newest letter's copy of an event is dropped at 0.8 or more, older copies of the same event are dropped too.
- **`split_cases`**: items whose top answer sits between 0.5 and 0.6. Read these before go-live and turn each pattern into a written rule.
- **`compare`**: the dry-run diff against today's output: added, removed and moved.

[`request.py`](request.py): one request for the whole batch, shared rules once, one choice question per item.

## Try it

    python3 -m unittest -q test_route   # offline, made-up numbers
    python3 run.py                      # route a sample batch, list split cases, diff against today
    python3 run.py --dry-run            # print the one request for the batch

## Where it breaks

- Before you swap out an LLM, list every job it does. Choosing may be only one of them.
- High confidence is not proof. In the parent's first test, the decision model put a substitute holiday on a child's calendar at 0.97. Move every date and number comparison into code.
- The cheaper LLM can drop items while merging. Check its output against what the decision model kept.
