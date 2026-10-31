"""Offline checks of the routing and shadow-test rules. Made-up answers, not model output."""

import json
import unittest

from request import build_body
from route import pick_bar, route, shadow_test

DATA = json.load(open("sample_cases.json"))
LABELS = DATA["labels"]


class RouteTest(unittest.TestCase):
    def test_confident_answers_act_without_the_llm(self):
        self.assertEqual(route({"urgent": {"noul": 0.97}})["action"], "page_on_call")
        self.assertEqual(route({"urgent": {"noul": 0.02}})["action"], "normal_queue")

    def test_unsure_or_missing_goes_to_the_llm(self):
        for p in (0.5, 0.89, 0.11, None):
            self.assertEqual(route({"urgent": {"noul": p}})["action"], "llm_review")

    def test_shadow_test_counts_only_cases_it_acts_on(self):
        r = shadow_test([0.95, 0.5, 0.02], [True, True, False], 0.9)
        self.assertAlmostEqual(r["runs_without_llm"], 2 / 3)
        self.assertEqual(r["wrong_when_acting"], 0.0)

    def test_confident_wrong_urgent_is_counted_as_missed(self):
        r = shadow_test([0.03], [True], 0.9)
        self.assertEqual(r["missed_urgent"], 1)
        self.assertEqual(r["wrong_when_acting"], 1.0)

    def test_a_copied_bar_undersells_the_second_model(self):
        b = DATA["candidates"]["model_b"]
        copied = shadow_test(b, LABELS, 0.9)       # model_a's comfortable bar, copied across
        bar_b, own = pick_bar(b, LABELS)           # model_b's own bar, set from the same cases
        self.assertEqual(copied["runs_without_llm"], 0.0)
        self.assertEqual(bar_b, 0.7)
        self.assertEqual(own["runs_without_llm"], 0.5)
        self.assertEqual(own["wrong_when_acting"], 0.0)

    def test_the_sharper_model_runs_more_without_the_llm(self):
        _, a = pick_bar(DATA["candidates"]["model_a"], LABELS)
        _, b = pick_bar(DATA["candidates"]["model_b"], LABELS)
        self.assertGreater(a["runs_without_llm"], b["runs_without_llm"])

    def test_same_body_for_every_candidate(self):
        a, b = build_body("x", "jev-1.14.0"), build_body("x", "@cf/cloudflare/clef")
        self.assertEqual(a["questions"], b["questions"])
        self.assertNotEqual(a["model"], b["model"])


if __name__ == "__main__":
    unittest.main()
