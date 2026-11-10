"""Offline checks of the rules. Made-up probabilities, not model output."""

import unittest

from decide import check, evaluate, honest_when_wrong
from request import build_body

W, O = "wrongly_joined", "one_person"


def never(*_):
    raise AssertionError("the LLM should not be called")


class CheckTest(unittest.TestCase):
    def test_sure_answers_stand_without_the_llm(self):
        self.assertEqual(check(0.95, never), (W, "decision_model"))
        self.assertEqual(check(0.10, never), (O, "decision_model"))

    def test_unsure_zone_goes_to_the_llm(self):
        self.assertEqual(check(0.55, lambda: O), (O, "llm"))
        self.assertEqual(check(0.30, lambda: W), (W, "llm"))  # low edge is inside the zone
        self.assertEqual(check(0.90, lambda: O), (O, "llm"))  # high edge is inside, as in "30% to 90%"

    def test_decision_model_down_falls_back_to_the_llm(self):
        self.assertEqual(check(None, lambda: W), (W, "llm"))


# A well-behaved decision model: its two mistakes (ids 3 and 4) sit in the zone.
HONEST = [
    {"p": 0.97, "llm": W, "truth": W},
    {"p": 0.05, "llm": O, "truth": O},
    {"p": 0.60, "llm": O, "truth": O},
    {"p": 0.45, "llm": W, "truth": W},
    {"p": 0.92, "llm": W, "truth": W},
]
# An overconfident one: its mistake (id 1) is at 0.95, so it never reaches the LLM.
OVERCONFIDENT = [
    {"p": 0.95, "llm": O, "truth": O},
    {"p": 0.05, "llm": O, "truth": O},
    {"p": 0.97, "llm": W, "truth": W},
    {"p": 0.02, "llm": O, "truth": O},
    {"p": 0.93, "llm": W, "truth": W},
]


class EvaluateTest(unittest.TestCase):
    def test_honest_model_reaches_full_accuracy_sending_two_in_five(self):
        r = evaluate(HONEST, dm_cost=0.01, llm_cost=1.0)
        self.assertEqual(r["share_sent"], 0.4)
        self.assertEqual(r["accuracy"], 1.0)
        self.assertAlmostEqual(r["cost_vs_llm_alone"], 0.41)

    def test_overconfident_model_keeps_its_mistake(self):
        r = evaluate(OVERCONFIDENT)
        self.assertEqual(r["share_sent"], 0.0)
        self.assertEqual(r["accuracy"], 0.8)

    def test_honesty_check_tells_the_two_apart(self):
        self.assertEqual(honest_when_wrong(HONEST), 1.0)
        self.assertEqual(honest_when_wrong(OVERCONFIDENT), 0.0)


class RequestTest(unittest.TestCase):
    def test_one_boolean_question_with_the_error_list(self):
        q = build_body([{}])["questions"]["wrongly_joined"]
        self.assertEqual(q["type"], "noul")
        self.assertIn("nicknames", q["criteria"]["false"])


if __name__ == "__main__":
    unittest.main()
