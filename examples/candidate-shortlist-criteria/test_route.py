"""Offline checks of the scoring and shortlist rules. Made-up answers, not model output."""

import unittest

from route import first_score, shortlist


def answers(team=2.0, market=2.0, stage=2.0):
    return {"team": {"score": team}, "market": {"score": market}, "stage": {"score": stage}}


class ScoreTest(unittest.TestCase):
    def test_top_level_on_every_criterion_scores_one(self):
        self.assertEqual(first_score(answers()), 1.0)

    def test_bottom_level_on_every_criterion_scores_zero(self):
        self.assertEqual(first_score(answers(0, 0, 0)), 0.0)

    def test_weights_apply(self):
        # Only the 0.4-weight criterion at the top level.
        self.assertEqual(first_score(answers(2, 0, 0)), 0.4)

    def test_a_score_between_levels_counts_in_proportion(self):
        self.assertEqual(first_score(answers(1, 1, 1)), 0.5)

    def test_missing_answer_counts_as_lowest_level(self):
        a = answers()
        a["stage"] = {"score": None}
        self.assertEqual(first_score(a), 0.7)

    def test_out_of_range_scores_are_clamped(self):
        self.assertEqual(first_score(answers(5, -1, 2)), 0.7)


class ShortlistTest(unittest.TestCase):
    def test_keeps_the_highest_scores(self):
        scored = [("a", 0.2), ("b", 0.9), ("c", 0.5)]
        self.assertEqual(shortlist(scored, size=2), ["b", "c"])

    def test_ties_keep_input_order(self):
        scored = [("a", 0.5), ("b", 0.5), ("c", 0.1)]
        self.assertEqual(shortlist(scored, size=2), ["a", "b"])


if __name__ == "__main__":
    unittest.main()
