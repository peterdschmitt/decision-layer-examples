"""Offline checks of the routing rules. These use made-up answers, not model output."""

import unittest

from route import route


def answers(glass=0.97, injury=0.01, planted=0.02):
    return {
        "glass_only": {"noul": glass},
        "injury_mentioned": {"noul": injury},
        "addressed_to_insurer": {"noul": planted},
    }


class RouteTest(unittest.TestCase):
    def test_clean_glass_claim_is_fast_tracked(self):
        self.assertEqual(route(answers()), "glass_fast_track")

    def test_planted_line_stops_the_fast_track_even_with_perfect_scores(self):
        self.assertEqual(route(answers(glass=0.99, injury=0.0, planted=0.8)), "adjuster_review")

    def test_no_coverage_never_fast_tracks(self):
        self.assertEqual(route(answers(), coverage_ok=False), "adjuster_review")

    def test_close_calls_go_to_a_person(self):
        self.assertEqual(route(answers(glass=0.85)), "adjuster_queue")
        self.assertEqual(route(answers(injury=0.1)), "adjuster_queue")


if __name__ == "__main__":
    unittest.main()
