# Agent turn: a decision model beside a chat agent's LLM

**Area:** any customer-service chat agent that looks things up and changes records: airline and travel bookings, orders and returns, subscriptions, insurance policies. **Model:** any decision model that answers yes/no and multiple-choice questions with a percentage per answer (Jev, OpenAI Decisions, Microsoft-Decision-1.1 and others). **Status:** checked offline with made-up data; model calls not yet run by us (expected, not measured).

Full write-up: the Decision Layer post on the airline chat test (draft, Nov. 24, 2026).

## The process

1. **List the small, fixed questions of each turn:** is a lookup needed, which of the customer's records, did the customer say yes, why are they cancelling.
2. **Ask them in one request to the decision model,** at the same moment the LLM starts. If no lookup is needed, the LLM's reply goes out and nobody waits for the decision model.
3. **Act only above each question's bar.** Below it, the LLM handles that step as before. Every choice has a "none" option.
4. **Let code do the lookups** the decision model points to.
5. **Write the policy as rules in code.** A change runs only if it passes the rules and the customer clearly said yes. The LLM writes the reply and fills in every change.
6. **Score before and after:** rule-breaking chats, LLM calls per customer message, cost per chat. In Sai Vamshi Atukuri's independent preprint (Nov. 22, 2026), on a public airline customer-service test with an AI customer, chats with a forbidden change fell from 43 to 10 of 600 and LLM calls per message fell 24–37%. He did not test the parts separately.

## The rules

[`harness.py`](harness.py):

- **`turn`**: one customer turn; returns the reply and whether it took the fast path.
- **`allowed`**: example airline rules (flown flights, basic economy, 24-hour window, insurance covers health or weather only).
- **`sure`**: an answer only when it clears its bar.
- **`scorecard`**: before-and-after shares for rule-breaking chats, LLM calls per message and cost per chat.

## Try it

    python3 -m unittest -q test_harness   # offline, made-up data
    python3 run.py                        # one made-up cancellation that the rules hold

## Where it breaks

- The rules in code are only as good as the policy you write down. Replay past correct changes through them and make sure none are blocked.
- Asking the LLM to get a clear yes can make some customers say yes and leave in the same message. Count those chats.
- On a fast, cheap LLM, the decision model's half second can delay a turn. Start both at once.
- Pin the decision model's version, or re-run the scorecard when it changes.
