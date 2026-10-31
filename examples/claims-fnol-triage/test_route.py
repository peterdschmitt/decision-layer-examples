"""Offline checks of the routing rules. These use made-up answers, not model output."""

import unittest

from route import route


def answers(choice="auto_collision", confidence=0.9, injury=0.01, located=0.95, complexity=0.4):
    return {
        "loss_type": {"choice": choice, "confidence": confidence},
        "injury_mentioned": {"noul": injury},
        "location_given": {"noul": located},
        "complexity": {"score": complexity},
    }


class RouteTest(unittest.TestCase):
    def test_any_hint_of_injury_goes_to_a_person_first(self):
        self.assertEqual(route(answers(injury=0.35, choice="auto_glass")), "injury_review")

    def test_unsure_loss_type_goes_to_manual_triage(self):
        self.assertEqual(route(answers(confidence=0.5)), "manual_triage")
        self.assertEqual(route(answers(choice="other_or_unclear")), "manual_triage")
        self.assertEqual(route(answers(confidence=None)), "manual_triage")

    def test_missing_location_asks_the_customer(self):
        self.assertEqual(route(answers(located=0.2)), "needs_info")

    def test_simple_confident_glass_claim_is_fast_tracked(self):
        self.assertEqual(route(answers(choice="auto_glass", confidence=0.92, complexity=0.1)), "fast_track_glass")

    def test_glass_that_looks_complex_stays_standard(self):
        self.assertEqual(route(answers(choice="auto_glass", confidence=0.92, complexity=1.2)), "standard_auto_glass")

    def test_ordinary_collision_goes_to_its_queue(self):
        self.assertEqual(route(answers()), "standard_auto_collision")


if __name__ == "__main__":
    unittest.main()
