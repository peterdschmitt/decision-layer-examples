# Extract, then decide: small questions about every AI conversation

**Area:** any company running AI agents that talk to customers or staff and wants answers about every conversation, not a sample: what the user asked for, whether they were frustrated, whether they set a rule for the work. **Model:** any decision model that answers multiple-choice questions with a percentage per answer (Jev, OpenAI Decisions, Microsoft-Decision-1.1 and others), plus an LLM agent that can read a whole conversation. **Status:** checked offline with made-up data; model calls not yet run by us (expected, not measured).

Full write-up: the Decision Layer post on Judgment Labs (draft, Nov. 25, 2026).

## The process

1. **List the small questions** you ask about your AI conversations.
2. **Find where each answer lives.** Keep a question only if its answer always sits where code can find it, such as the first user message or every user message.
3. **Have an LLM write the extraction code** for that question once, and test it on real conversations.
4. **Ask the decision model** the question with only the extracted lines.
5. **Set a bar.** Below it, or when the code fails, finds nothing or pulls out too much, send the conversation to an LLM agent that reads it all.
6. **Before switching a question over,** compare answers on a sample with answers a person set. If any miss came from lines the code left out, keep that question with the agent.
7. **Recheck on a schedule.** Rerun a recent sample through the agent. If agreement falls, rewrite the extraction code.

In Judgment Labs' own write-up (Nov. 23, 2026, reviewed by TypeSafe), a decision model reading extracted lines agreed with the reference answers as often as an LLM reading every conversation, at about 99.8% lower model cost. Judgment Labs puts the saving on customers' current setups at up to 80%, because some conversations still go to the agent.

## The parts

[`judge.py`](judge.py):

- **`answer`**: one question on one conversation; returns the answer, whether the decision model or the agent gave it, and why.
- **`sureness`**: 0 when the percentages are spread evenly, 1 when all sit on one answer. The bar applies to this.
- **`first_user_message`**, **`all_user_messages`**: example extraction code.
- **`check_sample`** and **`ready_to_switch`**: the test before a question moves to the decision model.
- **`drifted`**: the scheduled recheck.
- **`scorecard`**: share answered by the decision model, and cost against sending everything to the agent.

## Try it

    python3 -m unittest -q test_judge   # offline, made-up data
    python3 run.py                      # four made-up conversations

## Where it breaks

- The decision model sees only what the code pulls out. If the deciding line sits elsewhere, it can be sure and wrong. That is what the sample test is for.
- Questions that need the whole conversation, such as "did the agent follow policy across 200 turns", stay with the agent.
- Conversations change shape when you change your agent. Treat a new question wording or a new agent version as a new question and run the sample test again.
- Conversations that go to the agent cost as much as before. Count them.
