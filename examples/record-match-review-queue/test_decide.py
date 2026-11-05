"""Offline checks of the rules. Made-up probabilities, not model output."""

import unittest

from decide import final, match, score, sureness
from request import build_body

CASES = [{"id": i, "a": {}, "b": {}} for i in "abcdefg"]
JEV = {
    "a": {"same": 0.97, "different": 0.02, "unsure": 0.01},
    "b": {"same": 0.02, "different": 0.96, "unsure": 0.02},
    "c": {"same": 0.20, "different": 0.10, "unsure": 0.70},  # flagged unsure
    "d": {"same": 0.53, "different": 0.45, "unsure": 0.02},  # near coin flip
    "e": {"same": 0.91, "different": 0.08, "unsure": 0.01},
    "f": {"same": 0.30, "different": 0.30, "unsure": 0.40},  # flagged unsure
    "g": {"same": 0.88, "different": 0.11, "unsure": 0.01},
}


def jev(c):
    return JEV[c["id"]]


def llm(c):
    return {"same": 1.0}


class RuleTest(unittest.TestCase):
    def test_unsure_ranks_before_any_sure_answer(self):
        self.assertLess(sureness(JEV["c"]), sureness(JEV["d"]))

    def test_bar_holds_a_coin_flip_that_review_missed(self):
        r = match(CASES, jev, llm, max_reviews=2, bar=0.8)  # review takes c and f only
        self.assertEqual(r["d"], {"answer": "hold", "reviewed": False})

    def test_review_only_touches_the_least_sure(self):
        r = match(CASES, jev, llm, max_reviews=3)
        self.assertEqual({k for k, v in r.items() if v["reviewed"]}, {"c", "f", "d"})

    def test_sure_answers_go_through_without_review(self):
        r = match(CASES, jev, llm, max_reviews=3)
        self.assertEqual((r["a"]["answer"], r["b"]["answer"]), ("same", "different"))

    def test_decision_model_down_sends_case_to_review_first(self):
        def flaky(c):
            if c["id"] == "a":
                raise ConnectionError("down")
            return JEV[c["id"]]

        r = match(CASES, flaky, llm, max_reviews=1)
        self.assertTrue(r["a"]["reviewed"])

    def test_unsure_top_answer_is_held_even_above_the_bar(self):
        self.assertEqual(final({"unsure": 0.95, "same": 0.05}, 0.8), "hold")

    def test_score_counts_holds_apart_from_wrong(self):
        r = match(CASES, jev, llm, max_reviews=0)
        s = score(r, {k: "same" for k in JEV} | {"b": "different"})
        self.assertEqual((s["right"], s["held"], s["wrong"]), (4, 3, 0))

    def test_request_says_what_counts(self):
        crit = build_body({}, {})["questions"]["identity"]["criteria"]["same"]
        self.assertIn("Sufficient", crit)


if __name__ == "__main__":
    unittest.main()
