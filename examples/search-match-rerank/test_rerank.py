"""Offline checks of the search re-rank and the test read-out. Made-up numbers, not model output."""

import json
import os
import unittest

from request import build_body
from rerank import conversion_lift, rerank, split_credit

HERE = os.path.dirname(os.path.abspath(__file__))
PRODUCTS = [{"title": t} for t in "abcdef"]


class RerankTest(unittest.TestCase):
    def test_sorted_by_match_chance(self):
        scores = dict(zip("abcdef", [0.1, 0.9, 0.5, 0.7, 0.2, 0.3]))
        out, who = rerank("q", PRODUCTS, lambda s, p: scores[p["title"]])
        self.assertEqual(who, "decision_model")
        self.assertEqual([p["title"] for p in out], ["b", "d", "c", "f", "e", "a"])

    def test_ties_keep_search_order(self):
        out, _ = rerank("q", PRODUCTS, lambda s, p: 0.5)
        self.assertEqual(out, PRODUCTS)

    def test_decision_model_down_keeps_search_order(self):
        def down(*_):
            raise TimeoutError

        self.assertEqual(rerank("q", PRODUCTS, down), (PRODUCTS, "search"))

    def test_only_the_first_fifty_are_judged(self):
        many = [{"title": str(i)} for i in range(80)]
        seen = []
        rerank("q", many, lambda s, p: seen.append(p) or 0.5)
        self.assertEqual(len(seen), 50)

    def test_no_difference_means_no_lift(self):
        r = conversion_lift((300, 10000), (300, 10000))
        self.assertAlmostEqual(r["lift"], 0.0)
        self.assertAlmostEqual(r["p_value"], 1.0)

    def test_three_arms_split_the_credit(self):
        arms = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))["test_arms"]
        r = split_credit(tuple(arms["old_search"]), tuple(arms["new_search"]), tuple(arms["new_search_plus_model"]))
        self.assertAlmostEqual(r["combined"]["lift"], 0.32, places=6)
        self.assertAlmostEqual(r["new_search_alone"]["lift"], 0.10, places=6)
        self.assertAlmostEqual(r["decision_model_on_top"]["lift"], 0.20, places=6)
        self.assertLess(r["decision_model_on_top"]["p_value"], 0.01)

    def test_request_carries_search_and_product(self):
        body = build_body("wide boots", {"title": "Boot", "description": "Wide", "images": ["IMG"]})
        self.assertIn("wide boots", body["state"])
        self.assertEqual(body["images"], ["IMG"])
        self.assertEqual(body["questions"]["match"]["type"], "noul")


if __name__ == "__main__":
    unittest.main()
