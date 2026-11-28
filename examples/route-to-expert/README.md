# Route to the right expert

**Area:** any AI assistant that hands some requests to specialists: an HR, IT and finance helpdesk, customer service, internal search. **Model:** a decision model for the routing call, plus an LLM that does all the answering. **Status:** checked offline with made-up requests. Model calls not yet run by us (expected, not measured).

The pattern is based on Glean's published test, [Jev and the return of the zero-shot classifier](https://www.glean.com/blog/jev-zero-shot-classifier). This is our own code, not Glean's. Decision Layer is independent and is not affiliated with Glean or TypeSafe.

## In plain words

**The setup.** An AI assistant answers questions from staff. A few kinds of question go better with a specialist: an "expert" that is its own LLM agent with its own tools. Here there are three, for benefits, IT access and expenses. Everything else stays with the general assistant.

**What the LLM does.** It does all the real work. Whoever handles the request, an expert or the general assistant, the LLM reads it and writes the answer. It also stays on as the backup for the routing call.

**What the decision model does.** It answers one narrow question for every request: "Which expert should handle this request?" The options are the three experts and "none". It gives a percentage for each option in milliseconds. It never writes a word to the person asking.

**The bar.** When the top option is at or above the bar (60% to start with), the request goes straight to that expert. The bar is a dial. Raise it and more requests go to the LLM for the call. Lower it and the decision model settles more on its own.

**When it's unsure.** Below the bar, the LLM makes the routing call the way it did before. The decision model's answer is not a review of the LLM, and the LLM is not checking the decision model. Each one makes the call it is better placed to make.

**When something fails.** If the decision model is down or gives an answer that makes no sense, the LLM routes. If the LLM fails too, the request stays with the general assistant, which still answers. No request is dropped.

**How to decide whether to switch.** Take past requests where someone has marked the right route. Replay them through the old way (the LLM alone) and the new way, and compare route by route: how often each expert got requests that belonged to it, and how often it missed ones that did. Then try several bars and count the mistakes in what the decision model settled alone.

## What to expect

Expected, not measured. In the made-up history that ships with `run.py`, the new router makes fewer wrong routes than the old one, and raising the bar from 0.6 to 0.7 removes the one confident mistake at the cost of more LLM calls. Those numbers come from data we wrote ourselves to show the arithmetic. They say nothing about how any model performs. Run the replay on your own past requests before you rely on a bar.

## For builders

Python 3.10 or newer, standard library only.

```bash
python3 -m unittest test_route   # 16 offline tests, from this folder
python3 run.py --dry-run         # print the request, send nothing, replay the made-up history
TYPESAFE_API_KEY=... python3 run.py
```

The key is read from the environment when the request is sent and is never printed or logged.

### Files

- **`experts.py`**: `build_body` (one choice question), `read_answer`, `route_request` (the routing rules), `handle` (route, then the LLM answers), `replay` and `score_routes` (per-route precision and recall, accuracy and wrong routes for the old and new router), and `sweep_bar`.
- **`test_route.py`**: offline tests of the rules, the fallbacks and the scorer arithmetic on a small hand-checked set.
- **`run.py`**: routes one sample request and replays 13 made-up past requests. Its two LLM functions are stand-ins for your assistant's own calls.

### The rules

`route_request(request, decide, llm_route, bar=0.6)` returns `{"expert", "by", "p"}`, in this order:

1. The decision model's probabilities are checked. An empty answer, an option that isn't on the list, or a probability outside 0 to 1 counts as a failure.
2. Top option at or above the bar: that expert, `"by": "decision model"`.
3. Below the bar, or the decision model failed: the LLM's own routing call, `"by": "LLM"`.
4. The LLM failed or named an expert that doesn't exist: `"none"`, `"by": "fail-safe"`.

Then `handle(...)` calls `answer(expert, request)`, which is where the LLM writes the reply.

### The replay

Each past request needs four things: the request, the right route (`gold`), the route the LLM chose on its own (`old_route`), and the decision model's probabilities (`probs`, or `None` if it failed). `replay(cases, bar)` runs the new rules with the recorded probabilities and uses the recorded old route as the LLM's backup call. That is exactly what the LLM would have said, since it already said it.

Precision for a route is the share of requests sent there that belonged there. Recall is the share of requests that belonged there that were sent there. A route nothing was sent to has no precision (`None`), which is different from a precision of zero.

`sweep_bar(cases, bars)` returns `(bar, settled by the decision model, sent to the LLM, settled but wrong)` for each bar. Put the bar where the settled-but-wrong count is one you can live with, and re-check it on fresh requests.

### Where it breaks

- The `gold` labels are only as good as the person who wrote them. Have two people label a sample and see how often they agree.
- Watch precision on each expert most closely. A request sent to the wrong expert gets a confident answer from the wrong tools.
- Adding an expert changes the question. Re-run the replay and the sweep before you rely on the old bar.
- Pin the model version and re-test before moving to a new one.
