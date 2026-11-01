# Customer-chat routing with a confidence gate

**Area:** customer service and sales messaging (WhatsApp, web chat, social DMs). **Model:** jev-1.13.0, the version Entagl tested. **Status:** routing rules checked offline; model call not yet run by us (expected, not measured).

Full write-up: [How a customer-messaging company handed 88% of its AI's decisions to a decision model](https://decision-layer-indol.vercel.app/blog/entagl-customer-chat-routing-decision-model/).

## The process, fully automated

Behind every AI reply sit small decisions: answer, hand over, send a standard reply, or ignore; and did the customer ask us to stop. A frontier LLM can make them, but it pays to write and gives no measure of doubt. Here the decision model makes each call with a probability. Confident answers are acted on straight away; the rest go to the LLM, which also writes every reply.

## The questions

| Question | Type | Why |
|---|---|---|
| `action` | Choice | What to do with the latest message. The confidence is what the gate reads. |
| `stop_contact` | Noul (yes/no) | Checked first, with a low bar: missing a stop request is the expensive mistake. |

## What the code adds that the model can't see

- **Facts computed in code:** who owns the chat, whether contact details were already collected. Entagl's replay lost points when the model had to guess these.
- **Template lines stripped:** click-to-chat ads open with a stock line that made the model wave job-seekers through as leads.
- **Rules kept in code:** no second handover after the customer already gave their details.

## The rules

[`route.py`](route.py): stop request at 0.5 or more wins; action confidence at 0.85 or more acts; anything less, or a null confidence, goes to the LLM. `accuracy_by_language` scores a shadow run per language, because an average can hide the weak one.

## Try it

    python3 -m unittest -q test_route   # offline, made-up answers
    python3 run.py --dry-run            # print the request for the sample chat

## Where it breaks

- Set the bar per task from your own labelled cases; Entagl used 85% in its test and 90% in its replay.
- A confident answer can still be wrong (Entagl saw one at 0.95). Track outcomes after you switch.
- Test every language your customers write in, dialects included.
- Pin the version you tested and re-test before moving.
