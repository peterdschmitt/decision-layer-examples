"""Offline checks of the routing rules and the replay scorer. Made-up answers, not model output."""

import unittest

from experts import NONE, OPTIONS, build_body, handle, read_answer, replay, route_request, score_routes, sweep_bar


def fixed(probs):
    return lambda request: probs


def broken(*args):
    raise TimeoutError


def llm(choice):
    return lambda request: choice


class RouteRequest(unittest.TestCase):
    def test_confident_top_option_is_routed_by_the_decision_model(self):
        r = route_request("x", fixed({"benefits": 0.9, "none": 0.1}), llm("expenses"))
        self.assertEqual(r, {"expert": "benefits", "by": "decision model", "p": 0.9})

    def test_exactly_at_bar_is_routed_by_the_decision_model(self):
        r = route_request("x", fixed({"it_access": 0.6, "none": 0.4}), llm("none"))
        self.assertEqual(r["by"], "decision model")

    def test_below_bar_the_llm_decides_as_before(self):
        r = route_request("x", fixed({"expenses": 0.55, "none": 0.45}), llm("benefits"))
        self.assertEqual(r, {"expert": "benefits", "by": "LLM", "p": 0.55})

    def test_bar_can_be_raised(self):
        r = route_request("x", fixed({"benefits": 0.9}), llm("none"), bar=0.95)
        self.assertEqual(r["by"], "LLM")

    def test_decision_model_failure_goes_to_the_llm(self):
        r = route_request("x", broken, llm("it_access"))
        self.assertEqual(r, {"expert": "it_access", "by": "LLM", "p": None})

    def test_unknown_option_counts_as_failure(self):
        r = route_request("x", fixed({"payroll": 0.95}), llm("expenses"))
        self.assertEqual((r["expert"], r["by"]), ("expenses", "LLM"))

    def test_probabilities_outside_0_to_1_count_as_failure(self):
        for bad in ({"benefits": 1.7}, {"benefits": -0.1}, {"benefits": float("nan")}, {}, None):
            r = route_request("x", fixed(bad), llm("benefits"))
            self.assertEqual(r["by"], "LLM", bad)

    def test_both_fail_keeps_it_with_the_general_assistant(self):
        r = route_request("x", broken, broken)
        self.assertEqual(r, {"expert": NONE, "by": "fail-safe", "p": None})

    def test_llm_naming_an_unknown_expert_is_fail_safe(self):
        r = route_request("x", fixed({"benefits": 0.4, "none": 0.35}), llm("legal"))
        self.assertEqual((r["expert"], r["by"]), (NONE, "fail-safe"))


class Handle(unittest.TestCase):
    def test_the_llm_writes_the_answer_as_the_routed_expert(self):
        calls = []

        def answer(expert, request):
            calls.append((expert, request))
            return f"{expert} reply"

        r = handle("my card was declined", fixed({"expenses": 0.8}), llm("none"), answer)
        self.assertEqual(calls, [("expenses", "my card was declined")])
        self.assertEqual(r["reply"], "expenses reply")

    def test_fail_safe_still_gets_an_answer_from_the_general_assistant(self):
        r = handle("hello", broken, broken, lambda e, q: f"{e} reply")
        self.assertEqual((r["expert"], r["reply"]), (NONE, "none reply"))


class Request(unittest.TestCase):
    def test_every_option_is_offered_and_probabilities_are_read(self):
        q = build_body("x")["questions"]["expert"]
        self.assertEqual((q["type"], list(q["criteria"])), ("choice", OPTIONS))
        ans = {"type": "choice", "choice": "benefits", "confidence": 0.8,
               "probabilities": {"benefits": 0.8, "it_access": 0.1, "expenses": 0.05, "none": 0.05}}
        self.assertEqual(read_answer(ans)["benefits"], 0.8)


# Five hand-checked past requests.
CASES = [
    {"request": "1", "gold": "benefits", "old_route": "benefits", "probs": {"benefits": 0.9, "none": 0.1}},
    {"request": "2", "gold": "benefits", "old_route": "none", "probs": {"benefits": 0.7, "none": 0.3}},
    {"request": "3", "gold": "it_access", "old_route": "it_access",
     "probs": {"it_access": 0.5, "expenses": 0.3, "none": 0.2}},
    {"request": "4", "gold": "none", "old_route": "benefits", "probs": {"none": 1.4}},  # invalid
    {"request": "5", "gold": "expenses", "old_route": "expenses", "probs": {"it_access": 0.65, "expenses": 0.35}},
]


class Replay(unittest.TestCase):
    def test_precision_and_recall_arithmetic(self):
        gold = ["benefits", "benefits", "it_access", "none"]
        chosen = ["benefits", "none", "it_access", "benefits"]
        s = score_routes(gold, chosen)
        self.assertEqual(s.per_route["benefits"], (0.5, 0.5))   # 1 of 2 sent, 1 of 2 belonging
        self.assertEqual(s.per_route["it_access"], (1.0, 1.0))
        self.assertEqual(s.per_route["none"], (0.0, 0.0))       # 1 sent there, wrongly
        self.assertEqual(s.per_route["expenses"], (None, None))  # nothing sent, nothing belonged
        self.assertEqual((s.accuracy, s.wrong, s.total), (0.5, 2, 4))

    def test_old_and_new_routers_on_the_same_past_requests(self):
        r = replay(CASES, bar=0.6)
        old, new = r["old"], r["new"]
        # Old: benefits, none, it_access, benefits, expenses
        self.assertEqual(old.per_route["benefits"], (0.5, 0.5))
        self.assertEqual(old.per_route["none"], (0.0, 0.0))
        self.assertEqual(old.per_route["expenses"], (1.0, 1.0))
        self.assertEqual((old.accuracy, old.wrong), (0.6, 2))
        # New: benefits, benefits (decision model), it_access, benefits (LLM), it_access (decision model, wrong)
        self.assertAlmostEqual(new.per_route["benefits"][0], 2 / 3)
        self.assertEqual(new.per_route["benefits"][1], 1.0)
        self.assertEqual(new.per_route["it_access"], (0.5, 1.0))
        self.assertEqual(new.per_route["expenses"], (None, 0.0))
        self.assertEqual(new.per_route["none"], (None, 0.0))
        self.assertEqual((new.accuracy, new.wrong), (0.6, 2))   # same count as old, different mistakes

    def test_raising_the_bar_fixes_the_confident_mistake(self):
        new = replay(CASES, bar=0.7)["new"]   # request 5 goes back to the LLM, which had it right
        self.assertEqual((new.accuracy, new.wrong), (0.8, 1))


class Sweep(unittest.TestCase):
    def test_settled_versus_sent_to_the_llm_at_each_bar(self):
        rows = sweep_bar(CASES, bars=(0.6, 0.7, 0.95))
        self.assertEqual(rows[0], (0.6, 3, 2, 1))   # request 5 settled wrongly at 0.65
        self.assertEqual(rows[1], (0.7, 2, 3, 0))   # 0.7 is at the bar, so request 2 is settled
        self.assertEqual(rows[2], (0.95, 0, 5, 0))


if __name__ == "__main__":
    unittest.main()
