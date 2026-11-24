"""One customer turn in a chat agent: a decision model beside the LLM.

The decision model answers the small, fixed questions of the turn (is a lookup
needed? which booking? did the customer say yes? why are they cancelling?) in one
request, at the same moment the LLM starts. Code acts on answers above each
question's bar, does the lookups, and runs a change only if it passes the written
rules and the customer clearly said yes. The LLM writes every reply and fills in
every change. Below a bar, the LLM handles that step as before.

Pattern from Sai Vamshi Atukuri's independent preprint (Nov. 22, 2026) on an airline
customer-service test. This is our own sketch, offline, with made-up data:
expected, not measured.
"""
import asyncio
from dataclasses import dataclass, field

BARS = {"lookup_needed": 0.5, "booking": 0.5, "customer_said_yes": 0.5, "reason": 0.5}
COVERED_REASONS = {"health", "weather"}  # travel insurance pays only for these


@dataclass
class Change:
    kind: str          # "cancel", "change_flight", ...
    booking_id: str


@dataclass
class Reply:
    text: str
    changes: list = field(default_factory=list)
    held: list = field(default_factory=list)   # changes that did not run, with why


def allowed(change, booking, reason=None):
    """The airline's written rules, as code. Returns (ok, why)."""
    if booking.get("flown"):
        return False, "a flight has already flown"
    if change.kind == "change_flight" and booking.get("cabin") == "basic_economy":
        return False, "basic economy can't be changed"
    if change.kind == "cancel":
        if booking.get("hours_since_booking", 999) < 24 or booking.get("cabin") == "business" \
                or booking.get("airline_cancelled"):
            return True, "allowed"
        if booking.get("insured") and reason in COVERED_REASONS:
            return True, "allowed: insured, covered reason"
        return False, "not covered"
    return True, "allowed"


def sure(answer, name):
    """(value, probability) -> value when it clears the bar, else None."""
    value, p = answer
    return value if p >= BARS[name] and value != "none" else None


async def turn(state, decide, llm, fetch):
    """decide(state) -> {question: (answer, probability)}; llm(state) -> Reply; fetch(id) -> booking."""
    draft = asyncio.create_task(llm(state))           # the LLM starts at once, as before
    d = await decide(state)
    if d["lookup_needed"][1] < BARS["lookup_needed"]:
        return await draft, "fast"                     # nothing to look up: the LLM's reply goes out
    draft.cancel()
    pick = sure(d["booking"], "booking")
    if pick:
        state["bookings"] = {pick: await fetch(pick)}  # code does the lookup the decision model picked
    reply = await llm(state)                           # the LLM writes and fills in any change
    said_yes = sure(d["customer_said_yes"], "customer_said_yes") == "yes"
    reason = sure(d.get("reason", ("none", 0.0)), "reason")
    kept = []
    for c in reply.changes:
        ok, why = allowed(c, state.get("bookings", {}).get(c.booking_id, {}), reason)
        if not said_yes:
            ok, why = False, "no clear yes from the customer"
        (kept if ok else reply.held).append(c if ok else (c, why))
    reply.changes = kept
    return reply, "full"


def scorecard(before, after):
    """Each arg: list of chat results dicts with 'forbidden_change' (bool), 'llm_calls', 'messages', 'cost'.

    Returns the share change in rule-breaking chats, LLM calls per message and cost per chat.
    """
    def summary(chats):
        n = len(chats)
        return {
            "rule_breaking_share": sum(c["forbidden_change"] for c in chats) / n,
            "llm_calls_per_message": sum(c["llm_calls"] for c in chats) / sum(c["messages"] for c in chats),
            "cost_per_chat": sum(c["cost"] for c in chats) / n,
        }
    b, a = summary(before), summary(after)
    return {k: {"before": b[k], "after": a[k],
                "change": (a[k] - b[k]) / b[k] if b[k] else None} for k in b}
