import asyncio
import unittest
from harness import turn, allowed, scorecard, Change, Reply

BOOKINGS = {
    "R1": {"cabin": "economy", "insured": True, "hours_since_booking": 200},
    "R2": {"cabin": "basic_economy", "hours_since_booking": 200},
    "R3": {"cabin": "economy", "insured": False, "hours_since_booking": 2},
}


def run(coro):
    return asyncio.run(coro)


def fakes(answers, changes=()):
    calls = {"llm": 0, "fetch": 0}

    async def decide(state):
        return answers

    async def llm(state):
        calls["llm"] += 1
        return Reply("ok", list(changes))

    async def fetch(bid):
        calls["fetch"] += 1
        return BOOKINGS[bid]
    return decide, llm, fetch, calls


class Rules(unittest.TestCase):
    def test_insurance_reason(self):
        c = Change("cancel", "R1")
        self.assertTrue(allowed(c, BOOKINGS["R1"], "health")[0])
        self.assertFalse(allowed(c, BOOKINGS["R1"], "change of plan")[0])

    def test_basic_economy(self):
        self.assertFalse(allowed(Change("change_flight", "R2"), BOOKINGS["R2"])[0])

    def test_recent_booking_can_cancel(self):
        self.assertTrue(allowed(Change("cancel", "R3"), BOOKINGS["R3"])[0])


class Turn(unittest.TestCase):
    def test_fast_path(self):
        d, llm, fetch, calls = fakes({"lookup_needed": ("yes", 0.2)})
        reply, path = run(turn({}, d, llm, fetch))
        self.assertEqual(path, "fast")
        self.assertEqual(calls["fetch"], 0)

    def test_lookup_and_allowed_change(self):
        ans = {"lookup_needed": ("yes", 0.9), "booking": ("R1", 0.8),
               "customer_said_yes": ("yes", 0.9), "reason": ("health", 0.7)}
        d, llm, fetch, calls = fakes(ans, [Change("cancel", "R1")])
        reply, path = run(turn({}, d, llm, fetch))
        self.assertEqual(calls["fetch"], 1)
        self.assertEqual(len(reply.changes), 1)

    def test_not_covered_reason_is_held(self):
        ans = {"lookup_needed": ("yes", 0.9), "booking": ("R1", 0.8),
               "customer_said_yes": ("yes", 0.9), "reason": ("change of plan", 0.9)}
        d, llm, fetch, _ = fakes(ans, [Change("cancel", "R1")])
        reply, _ = run(turn({}, d, llm, fetch))
        self.assertEqual(reply.changes, [])
        self.assertEqual(reply.held[0][1], "not covered")

    def test_no_clear_yes_is_held(self):
        ans = {"lookup_needed": ("yes", 0.9), "booking": ("R3", 0.9),
               "customer_said_yes": ("yes", 0.3)}
        d, llm, fetch, _ = fakes(ans, [Change("cancel", "R3")])
        reply, _ = run(turn({}, d, llm, fetch))
        self.assertEqual(reply.held[0][1], "no clear yes from the customer")

    def test_unsure_booking_means_no_lookup(self):
        ans = {"lookup_needed": ("yes", 0.9), "booking": ("R1", 0.3), "customer_said_yes": ("no", 0.9)}
        d, llm, fetch, calls = fakes(ans)
        run(turn({}, d, llm, fetch))
        self.assertEqual(calls["fetch"], 0)


class Score(unittest.TestCase):
    def test_scorecard(self):
        before = [{"forbidden_change": i < 4, "llm_calls": 3, "messages": 1, "cost": 1.0} for i in range(50)]
        after = [{"forbidden_change": i < 1, "llm_calls": 2, "messages": 1, "cost": 0.8} for i in range(50)]
        s = scorecard(before, after)
        self.assertAlmostEqual(s["rule_breaking_share"]["change"], -0.75)
        self.assertAlmostEqual(s["llm_calls_per_message"]["change"], -1 / 3)
        self.assertAlmostEqual(s["cost_per_chat"]["change"], -0.2)


if __name__ == "__main__":
    unittest.main()
