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
    def test_letter_that_matches_the_file_is_sent_automatically(self):
        self.assertEqual(route(answers()), ("send_automatically", []))

    def test_sample_letter_goes_to_an_adjuster_with_reasons(self):
        action, reasons = route(answers(promise=0.9, contradicts=0.8, docs=0.1, tone=0.9))
        self.assertEqual(action, "adjuster_sends")
        self.assertEqual(len(reasons), 4)

    def test_even_a_small_chance_of_a_wrong_promise_keeps_a_person_in(self):
        self.assertEqual(route(answers(promise=0.25))[0], "adjuster_sends")


if __name__ == "__main__":
    unittest.main()
