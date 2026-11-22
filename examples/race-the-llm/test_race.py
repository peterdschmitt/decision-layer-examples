import asyncio
import unittest
from race import route, scorecard, agreement_floor, pick_bar


def make(prob, label="order", llm_answer="order", decide_delay=0.0, fail=False):
    calls = {"llm_started": 0, "llm_finished": 0}

    async def decide(m):
        await asyncio.sleep(decide_delay)
        if fail:
            raise RuntimeError("down")
        return label, prob

    async def llm(m):
        calls["llm_started"] += 1
        await asyncio.sleep(0.05)
        calls["llm_finished"] += 1
        return llm_answer
    return decide, llm, calls


def run(coro):
    return asyncio.run(coro)


class RaceTest(unittest.TestCase):
    def test_sure_answer_wins_and_cancels_llm(self):
        d, l, c = make(0.97)
        self.assertEqual(run(route("m", d, l)), ("order", "decision model"))
        self.assertEqual(c["llm_finished"], 0)

    def test_unsure_uses_llm(self):
        d, l, c = make(0.6, llm_answer="question")
        self.assertEqual(run(route("m", d, l)), ("question", "llm"))
        self.assertEqual(c["llm_finished"], 1)

    def test_down_or_slow_falls_back(self):
        d, l, _ = make(0.99, fail=True)
        self.assertEqual(run(route("m", d, l))[1], "llm")
        d, l, _ = make(0.99, decide_delay=0.5)
        self.assertEqual(run(route("m", d, l, timeout=0.1))[1], "llm")

    def test_shadow_never_acts_but_logs(self):
        d, l, _ = make(0.99, label="order", llm_answer="order")
        log = []
        self.assertEqual(run(route("m", d, l, mode="shadow", log=log))[1], "llm")
        self.assertEqual(log[0]["label"], "order")

    def test_off_and_bad_mode(self):
        d, l, _ = make(0.99)
        self.assertEqual(run(route("m", d, l, mode="off"))[1], "llm")
        with self.assertRaises(ValueError):
            run(route("m", d, l, mode="maybe"))

    def test_scorecard(self):
        log = [{"label": "a", "prob": 0.95, "llm": "a"}, {"label": "a", "prob": 0.95, "llm": "b"},
               {"label": "a", "prob": 0.5, "llm": "a"}, {"label": "a", "prob": 0.92, "llm": "a"}]
        s = scorecard(log, 0.9)
        self.assertAlmostEqual(s["answer_rate"], 0.75)
        self.assertAlmostEqual(s["agreement"], 2 / 3)

    def test_agreement_floor_matches_post(self):
        self.assertAlmostEqual(agreement_floor(11, 11), 0.715, places=3)

    def test_pick_bar(self):
        log = [{"label": "a", "prob": p, "llm": "a" if p >= 0.8 else "b"} for p in (0.6, 0.7, 0.8, 0.9, 0.95)]
        bar, s = pick_bar(log, min_agreement=1.0)
        self.assertEqual(bar, 0.71)
        self.assertEqual(s["agreement"], 1.0)


if __name__ == "__main__":
    unittest.main()
