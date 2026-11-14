"""Offline checks of the personal-details gate. Made-up probabilities, not model output."""

import json
import os
import unittest

from gate import QUESTIONS, evaluate, pick_bar, scrub
from request import build_body

HERE = os.path.dirname(os.path.abspath(__file__))


def never(_):
    raise AssertionError("the LLM should not be called")


class GateTest(unittest.TestCase):
    def test_clean_summary_skips_the_llm(self):
        self.assertEqual(scrub("browsed pricing", lambda t, q: 0.05, never), ("browsed pricing", 0))

    def test_either_question_at_the_bar_sends_it_to_the_llm(self):
        scores = {QUESTIONS[0]: 0.10, QUESTIONS[1]: 0.40}
        out = scrub("typed jane@example.com", lambda t, q: scores[q] if "jane" in t else 0.01, lambda t: "typed an email")
        self.assertEqual(out, ("typed an email", 1))

    def test_rewrite_is_checked_again_and_held_if_still_flagged(self):
        out = scrub("Maria Lopez", lambda t, q: 0.9, lambda t: t)  # the rewrite never removes the name
        self.assertEqual(out, (None, 2))

    def test_decision_model_down_counts_as_flagged(self):
        def down(*_):
            raise TimeoutError

        out = scrub("anything", down, lambda t: t)
        self.assertEqual(out, (None, 2))  # never stored unchecked

    def test_sample_counts_at_the_low_bar(self):
        cases = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))["cases"]
        r = evaluate(cases, 0.40)
        self.assertEqual((r["total"], r["skip_llm"], r["false_alarms"], r["misses"]), (12, 6, 3, 1))

    def test_bar_follows_the_costlier_mistake(self):
        cases = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))["cases"]
        self.assertEqual(pick_bar(cases, cost_false_alarm=1, cost_miss=100), 0.3)  # a miss is costly: low bar
        self.assertEqual(pick_bar(cases, cost_false_alarm=1, cost_miss=1), 0.6)  # mistakes cost the same: higher bar

    def test_request_asks_both_questions_once(self):
        body = build_body("a summary")
        self.assertEqual(body["state"], "a summary")
        self.assertEqual(len(body["questions"]), 2)
        self.assertTrue(all(q["type"] == "noul" for q in body["questions"].values()))


if __name__ == "__main__":
    unittest.main()
