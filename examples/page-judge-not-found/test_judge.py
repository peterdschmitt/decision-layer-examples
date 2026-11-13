"""Offline checks of the page judge. Made-up probabilities, not model output."""

import json
import os
import unittest

from judge import NOT_FOUND, answer_question, evaluate, pick_bar
from request import build_body

PAGES = ["a", "b", "c", "d", "e", "f", "g", "h"]


def never(*_):
    raise AssertionError("the LLM should not be called")


class JudgeTest(unittest.TestCase):
    def test_no_page_clears_the_bar_means_not_found_without_the_llm(self):
        out = answer_question("q", PAGES, lambda p, q: 0.05, never)
        self.assertEqual(out, (NOT_FOUND, "decision_model"))

    def test_llm_reads_the_best_six_pages_in_order(self):
        scores = dict(zip(PAGES, [0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.4, 0.6]))
        seen = []
        answer_question("q", PAGES, lambda p, q: scores[p], lambda q, pages: seen.extend(pages) or "ans")
        self.assertEqual(seen, ["b", "d", "f", "h", "g", "e"])

    def test_decision_model_down_uses_search_pages(self):
        def down(*_):
            raise TimeoutError

        seen = []
        out = answer_question("q", PAGES, down, lambda q, pages: seen.extend(pages) or "ans")
        self.assertEqual(out, ("ans", "llm"))
        self.assertEqual(seen, PAGES[:6])

    def test_empty_shortlist_is_not_found(self):
        self.assertEqual(answer_question("q", [], lambda p, q: 1.0, never), (NOT_FOUND, "decision_model"))

    def test_sample_counts(self):
        here = os.path.dirname(os.path.abspath(__file__))
        cases = json.load(open(os.path.join(here, "sample_input.json"), encoding="utf-8"))["cases"]
        r = evaluate(cases, 0.30)
        self.assertEqual(r["answer_page_first"], 3)  # the price-change reason is ranked second
        self.assertEqual(r["wrongly_not_found"], 0)
        self.assertEqual(r["absent_caught"], 2)  # the two near misses fool the judge
        self.assertEqual(pick_bar(cases), 0.5)

    def test_request_asks_every_question_once_per_page(self):
        body = build_body("IMG", {"a": "Is A here?", "b": "Is B here?"})
        self.assertEqual(body["images"], ["IMG"])
        self.assertEqual(set(body["questions"]), {"a", "b"})
        self.assertTrue(all(q["type"] == "noul" for q in body["questions"].values()))


if __name__ == "__main__":
    unittest.main()
