import unittest
from pick import pick_notes, answer, score_picker, sweep_bar, relative_change, log_bias


def fake_decide(table):
    return lambda q, chunk: [table.get(n, 0.0) for n in chunk]


class TestPick(unittest.TestCase):
    def test_keeps_above_bar_best_first_with_cap(self):
        d = fake_decide({f"n{i}": i / 10 for i in range(10)})
        notes = [f"n{i}" for i in range(10)]
        self.assertEqual(pick_notes("q", notes, d, bar=0.5, cap=3), ["n9", "n8", "n7"])

    def test_batches_of_twenty(self):
        calls = []
        def d(q, chunk):
            calls.append(len(chunk))
            return [0.9] * len(chunk)
        pick_notes("q", [f"n{i}" for i in range(45)], d)
        self.assertEqual(calls, [20, 20, 5])

    def test_silent_when_nothing_clears(self):
        d = fake_decide({"a": 0.2, "b": 0.3})
        self.assertEqual(pick_notes("q", ["a", "b"], d), [])

    def test_answer_records_what_llm_read(self):
        d = fake_decide({"a": 0.9, "b": 0.1})
        out, read = answer("q", ["a", "b"], d, lambda q, notes: f"answer from {notes}")
        self.assertEqual(read, ["a"])
        self.assertIn("a", out)

    def test_score_picker(self):
        cases = [
            {"question": "q1", "notes": ["a", "b", "c"], "relevant": {"a"}},
            {"question": "q2", "notes": ["d", "e"], "relevant": set()},
        ]
        s = score_picker(cases, lambda q, n: ["a", "b"] if q == "q1" else [])
        self.assertAlmostEqual(s["precision"], 0.5)
        self.assertAlmostEqual(s["recall"], 1.0)
        self.assertAlmostEqual(s["silent_when_nothing_fits"], 1.0)

    def test_sweep_bar_prefers_recall_above_precision_floor(self):
        d = fake_decide({"a": 0.9, "b": 0.6, "c": 0.4, "x": 0.55})
        cases = [{"question": "q", "notes": ["a", "b", "c", "x"], "relevant": {"a", "b", "c"}}]
        bar, s = sweep_bar(cases, d, bars=[0.3, 0.5, 0.7], min_precision=0.7)
        self.assertEqual(bar, 0.3)
        self.assertAlmostEqual(s["recall"], 1.0)

    def test_relative_change_matches_unblocked(self):
        self.assertAlmostEqual(relative_change(0.348, 0.464), 0.333, places=3)
        self.assertAlmostEqual(relative_change(0.652, 0.536), -0.178, places=3)
        self.assertAlmostEqual(relative_change(1.87, 1.76), -0.059, places=3)

    def test_log_bias(self):
        self.assertAlmostEqual(log_bias(["a", "b", "c", "d"], {"a", "b", "c"}), 0.75)


if __name__ == "__main__":
    unittest.main()
