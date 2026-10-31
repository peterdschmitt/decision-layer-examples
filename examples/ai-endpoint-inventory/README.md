# AI endpoint inventory: decide, then explain only where needed

**Area:** application security, AI governance. **Model:** jev-1.14.0. **Status:** routing rules checked offline; model call not yet run by us (expected, not measured).

Full write-up: [How Harness cut an AI security check's cost 99.9% with a decision model](https://decision-layer-indol.vercel.app/blog/harness-ai-api-inventory-decision-model/).

## The process, fully automated

A security team needs to know which API endpoints send data to an AI model. For every endpoint in a customer's traffic, the system records: is it an AI API, does it return AI-generated content, how confident, and why. An LLM can do the whole job, but it writes thousands of words to reach two yes-or-no answers, and its own "high confidence" says little about which answers are wrong.

Here the decision model answers the two questions with probabilities. Confident answers are recorded straight away. Only the unsure band goes to one LLM call, and the LLM writes reasons only for the endpoints that are AI APIs.

## The questions

| Question | Type | Why |
|---|---|---|
| `is_ai_api` | Noul (yes/no) | The decision itself. The probability is what you set the band on. |
| `returns_ai` | Noul (yes/no) | Only counted when the endpoint is an AI API. |

Send a trimmed sample of the endpoint's traffic as the state: a few requests and responses, long fields cut short. Harness used the top three spans per endpoint.

## The rules

[`route.py`](route.py):

- probability 0.8 or more: record as an AI API; the LLM writes the reason later, in a call that already runs on positives
- 0.2 or less: record as not an AI API, with a standard reason
- in between, or no answer: send to one LLM call

**Expected for the sample endpoint:** chat-style messages forwarded to an AI vendor host should score near 1 and be recorded as an AI API with no LLM call.

## Set the dials from your own data

The 0.2 to 0.8 band is the one Harness says it is deploying, drawn from a 500-endpoint test where every error fell between 0.3 and 0.8. Label a few hundred of your own endpoints by hand, run the model, group the answers by probability and count the errors in each group. Put the band where your errors are, and re-check it on fresh data.

## Where it breaks

- Text in, text out: if the AI call happens somewhere the traffic sample doesn't show, the model can't see it.
- A wider band is safer and costs more LLM calls. Watch both.
- Pin the model version and re-test before moving to a new one.
