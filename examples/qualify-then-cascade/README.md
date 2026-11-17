# Qualify, then cascade: find which LLM decisions a decision model can take, and keep the LLM for the rest

**Area:** any team with LLM calls that return one choice from a fixed list: data labelling, duplicate checks, eval judging, routing requests to agents or models, and when an assistant should speak up in a group chat. **Model:** any decision model that returns a probability per answer (Jev, OpenAI Decisions, Gemini Decision 1, Clef and others). **Status:** checked offline with made-up numbers; model calls not yet run by us (expected, not measured).

Full write-up: the SellScale verdict essay on Decision Layer (draft, Nov. 17, 2026).

## The process

1. **Qualify.** For each LLM step that picks one answer from a list, run the decision model on your own labelled examples. Move the step only if it matches the labels often enough. SellScale's bar was 99% for a step already working on an LLM, and 96% for a new feature an LLM was too slow to run at all. About half the workflows it tested cleared the bar, mostly simple yes/no questions. Complex rubric questions scored 60 to 70%.
2. **Cascade.** For each item in a step that moved, accept the decision model's answer when it is confident. Send the rest to the LLM you already have. If both fail, use a rule. Record which layer made every label.
3. **Watch the share.** The share of labels made by the decision model is the number to tune the threshold against.

An independent preprint tested the same accept-or-escalate shape for judging answers (Li, Miao, Krishnan and Padman, arXiv 2609.26550). With a threshold fixed in advance, the cascade was 0.9 points more accurate than GPT-6 alone on 1,610 held-out pairs, at 41% of its fee.

## The rules

[`cascade.py`](cascade.py):

- **`agreement`** and **`qualify`**: score each step on its own labelled data; a step can carry its own bar.
- **`cascade`**: decision model, then the LLM, then a rule; returns the label, its source and the confidence.
- **`share_by_source`**: how much work each layer did.
- **`speak_or_stay_quiet`**: the group-chat shape. The decision model makes one call per message; when it isn't sure, the agent stays quiet; the LLM writes only when the call is "reply".

## Try it

    python3 -m unittest -q test_cascade   # offline, made-up numbers
    python3 run.py                        # qualify four steps, then run a cascade

## Where it breaks

- A decision model reads; it doesn't work things out. Steps that need math, code or a chain of logic stay on the LLM. The preprint found the decision model fell behind exactly there.
- Agreement with your labels is only as good as the labels. Use examples a person has checked.
- Re-qualify when the decision model's version changes. Pin the version in production.
