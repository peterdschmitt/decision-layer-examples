"""Offline checks of the routing rules. Made-up answers, not model output."""

import unittest

from route import route


def answers(p=0.95, r=0.9):
    return {"is_ai_api": {"noul": p}, "returns_ai": {"noul": r}}


class RouteTest(unittest.TestCase):
    def test_confident_yes_is_recorded_as_an_ai_api(self):
        rec = route(answers(0.96, 0.9))
        self.assertEqual(rec["action"], "record")
        self.assertTrue(rec["is_ai_api"])
        self.assertTrue(rec["returns_ai_generated_content"])
        self.assertIsNone(rec["reason"])  # the LLM writes it later

    def test_confident_no_gets_a_standard_reason(self):
        rec = route(answers(0.04, 0.1))
        self.assertFalse(rec["is_ai_api"])
        self.assertFalse(rec["returns_ai_generated_content"])
        self.assertIn("No prompt-like fields", rec["reason"])

    def test_unsure_band_goes_to_the_llm(self):
        for p in (0.21, 0.5, 0.79):
            self.assertEqual(route(answers(p))["action"], "llm_review")

    def test_band_edges_are_decided_by_the_decision_model(self):
        self.assertEqual(route(answers(0.2))["action"], "record")
        self.assertEqual(route(answers(0.8))["action"], "record")

    def test_missing_probability_goes_to_the_llm(self):
        self.assertEqual(route({"is_ai_api": {"noul": None}, "returns_ai": {"noul": 0.9}})["action"], "llm_review")

    def test_not_an_ai_api_never_returns_ai_content(self):
        self.assertFalse(route(answers(0.1, 0.99))["returns_ai_generated_content"])


if __name__ == "__main__":
    unittest.main()
