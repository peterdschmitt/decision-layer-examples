"""Offline checks of the routing rules. These use made-up answers, not model output."""

import unittest

from route import route


def answers(promise=0.02, contradicts=0.03, docs=0.95, tone=1.8):
    return {
        "promises_outcome": {"noul": promise},
        "contradicts_file": {"noul": contradicts},
        "asks_for_all_documents": {"noul": docs},
        "tone": {"score": tone},
    }


class RouteTest(unittest.TestCase):
    def test_clean_draft_is_sent(self):
        self.assertEqual(route(answers()), ("send", []))

    def test_the_sample_draft_goes_back_with_precise_fixes(self):
        action, fixes = route(answers(promise=0.9, contradicts=0.8, docs=0.1, tone=0.9))
        self.assertEqual(action, "revise")
        self.assertEqual(len(fixes), 4)
        self.assertIn("Remove any promise", fixes[0])

    def test_a_small_promise_signal_still_triggers_a_fix(self):
        self.assertEqual(route(answers(promise=0.25))[0], "revise")

    def test_after_two_tries_a_person_takes_over(self):
        self.assertEqual(route(answers(promise=0.9), revision=2)[0], "person_reviews")


if __name__ == "__main__":
    unittest.main()
