import asyncio
from harness import turn, Change, Reply

BOOKINGS = {"R1": {"cabin": "economy", "insured": True, "hours_since_booking": 200}}


async def decide(state):
    # made-up answers for: "I'd like to cancel my Denver trip, my plans changed. Yes, go ahead."
    return {"lookup_needed": ("yes", 0.93), "booking": ("R1", 0.88),
            "customer_said_yes": ("yes", 0.91), "reason": ("change of plan", 0.84)}


async def llm(state):
    return Reply("I've looked at your Denver trip.", [Change("cancel", "R1")])


async def fetch(bid):
    return BOOKINGS[bid]


reply, path = asyncio.run(turn({}, decide, llm, fetch))
print("path:", path)
print("changes run:", reply.changes)
print("changes held:", [(c.kind, c.booking_id, why) for c, why in reply.held])
