"""Offline checks of qualify-then-cascade. Made-up numbers, not model output."""

import json
import os
import unittest

from cascade import agreement, cascade, qualify, share_by_source, speak_or_stay_quiet

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))
DECIDE = DATA["model_answers"].__getitem__


def down(*_):
    raise TimeoutError


class QualifyTest(unittest.TestCase):
    def test_agreement_counts_top_answers(self):
        self.assertEqual(agreement(DECIDE, DATA["steps"]["is_duplicate"]["examples"]), 0.75)

    def test_only_steps_that_clear_the_bar_move(self):
        moves, stays = qualify(DATA["steps"], DECIDE)
        self.assertEqual([m[0] for m in moves], ["is_record_noise", "group_chat_should_reply"])
        self.assertIn(("rubric_quality_of_reply", 0.5), stays)

    def test_a_step_can_carry_its_own_bar(self):
        moves, _ = qualify({"g": DATA["steps"]["group_chat_should_reply"]}, DECIDE, bar=0.99)
        self.assertEqual(moves, [("g", 0.75)])


class CascadeTest(unittest.TestCase):
    def test_confident_answer_is_accepted(self):
        self.assertEqual(cascade("r1", DECIDE, down, down), ("noise", "decision_model", 0.97))

    def test_unsure_goes_to_the_llm(self):
        self.assertEqual(cascade("d3", DECIDE, lambda i: "no", down), ("no", "llm", None))

    def test_decision_model_down_goes_to_the_llm_then_the_rule(self):
        self.assertEqual(cascade("x", down, lambda i: "a", down)[1], "llm")
        self.assertEqual(cascade("x", down, down, lambda i: "b"), ("b", "rule", None))

    def test_share_by_source(self):
        res = [("a", "decision_model", 0.9), ("b", "decision_model", 0.95), ("c", "llm", None), ("d", "rule", None)]
        self.assertEqual(share_by_source(res), {"decision_model": 0.5, "llm": 0.25, "rule": 0.25})

    def test_unsure_in_group_chat_means_stay_quiet(self):
        self.assertEqual(speak_or_stay_quiet("g3", DECIDE, down), ("stay_quiet", None))
        self.assertEqual(speak_or_stay_quiet("g1", DECIDE, lambda m: "hi"), ("reply", "hi"))


if __name__ == "__main__":
    unittest.main()
