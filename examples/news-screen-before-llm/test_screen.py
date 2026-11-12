"""Offline checks of the screening rules. Made-up probabilities and prices, not model output."""

import unittest

from request import build_body
from screen import bar_report, break_even_llm_price, net_saving, screen, screen_then_brief, screening_pays

A = [
    {"title": "on topic", "length": 100, "screen_length": 10, "p": 0.9},
    {"title": "noise", "length": 100, "screen_length": 10, "p": 0.2},
    {"title": "borderline", "length": 100, "screen_length": 10, "p": 0.7},
]


def by_p(a):
    return a["p"]


class ScreenTest(unittest.TestCase):
    def test_bar_is_inclusive(self):
        kept, dropped = screen(A, by_p, bar=0.70)
        self.assertEqual([a["title"] for a in kept], ["on topic", "borderline"])
        self.assertEqual([a["title"] for a in dropped], ["noise"])

    def test_decision_model_down_keeps_the_article(self):
        def down(_):
            raise TimeoutError

        kept, dropped = screen(A, down)
        self.assertEqual(len(kept), 3)
        self.assertEqual(dropped, [])

    def test_llm_writes_only_from_what_is_kept(self):
        seen = []
        _, share = screen_then_brief(A, by_p, lambda kept: seen.extend(kept) or "briefing")
        self.assertEqual(len(seen), 2)
        self.assertAlmostEqual(share, 2 / 3)

    def test_pays_with_expensive_llm_not_with_cheap_one(self):
        _, dropped = screen(A, by_p)
        # Dropped 100 units; screening read 30 units in total.
        self.assertTrue(screening_pays(dropped, A, llm_price=3.0, screen_price=1.0))  # 300 saved vs 30 spent
        self.assertFalse(screening_pays(dropped, A, llm_price=0.25, screen_price=1.0))  # 25 saved vs 30 spent
        self.assertAlmostEqual(net_saving(dropped, A, 3.0, 1.0), 270.0)

    def test_break_even_price(self):
        _, dropped = screen(A, by_p)
        self.assertAlmostEqual(break_even_llm_price(dropped, A, screen_price=1.0), 0.3)
        self.assertEqual(break_even_llm_price([], A, 1.0), float("inf"))

    def test_stricter_bar_drops_more(self):
        r = bar_report(A, [a["p"] for a in A], bars=(0.5, 0.95))
        self.assertLess(r[0.5], r[0.95])

    def test_request_sends_headline_and_summary_only(self):
        body = build_body({"title": "T", "summary": "S" * 2000, "body": "full text"}, "Acme")
        self.assertNotIn("full text", body["state"])
        self.assertLessEqual(len(body["state"]), len("Title: T\nSummary: ") + 800)
        self.assertEqual(body["questions"]["on_topic"]["type"], "noul")
        self.assertIn("Acme", body["questions"]["on_topic"]["instructions"])


if __name__ == "__main__":
    unittest.main()
