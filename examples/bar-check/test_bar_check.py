import unittest
from bar_check import bar_report, pick_bar, misses_by_answer, flip_rate, cost_saved


def case(truth, **probs):
    return {"truth": truth, "probs": probs}


CASES = (
    [case("yes", yes=0.99, no=0.01)] * 40
    + [case("no", yes=0.98, no=0.02)] * 2      # sure and wrong
    + [case("yes", yes=0.92, no=0.08)] * 20
    + [case("no", yes=0.91, no=0.09)] * 6      # sure-ish and wrong
    + [case("no", yes=0.30, no=0.70)] * 20
    + [case("yes", yes=0.40, no=0.60)] * 12
)


class BarCheck(unittest.TestCase):
    def test_share_and_errors(self):
        rows = {r["bar"]: r for r in bar_report(CASES, bars=(0.9, 0.95))}
        self.assertAlmostEqual(rows[0.9]["share"], 68 / 100)
        self.assertAlmostEqual(rows[0.9]["seen"], 8 / 68)
        self.assertAlmostEqual(rows[0.95]["seen"], 2 / 42)

    def test_seen_error_can_exceed_implied(self):
        r = bar_report(CASES, bars=(0.9,))[0]
        self.assertGreater(r["seen"], r["implied"])

    def test_empty_bar(self):
        r = bar_report(CASES, bars=(0.999,))[0]
        self.assertEqual(r["share"], 0.0)
        self.assertIsNone(r["seen"])

    def test_pick_bar(self):
        rows = bar_report(CASES, bars=(0.7, 0.9, 0.95, 0.99))
        self.assertEqual(pick_bar(rows, max_wrong=0.05)["bar"], 0.95)
        self.assertEqual(pick_bar(rows, max_wrong=0.01)["bar"], 0.99)
        self.assertIsNone(pick_bar(rows, max_wrong=0.01, min_kept=50))

    def test_pick_bar_needs_enough_cases(self):
        rows = bar_report(CASES, bars=(0.95,))
        self.assertIsNone(pick_bar(rows, max_wrong=0.05, min_kept=50))

    def test_misses_by_answer(self):
        m = misses_by_answer(CASES, 0.9)
        self.assertEqual(m["no"]["cases"], 8)
        self.assertEqual(m["no"]["missed"], 8)
        self.assertEqual(m["no"]["called_instead"], {"yes": 8})
        self.assertEqual(m["yes"]["missed"], 0)

    def test_flip_rate(self):
        same = [{"yes": 0.9, "no": 0.1}] * 3
        flip = [{"yes": 0.51, "no": 0.49}, {"yes": 0.49, "no": 0.51}, {"yes": 0.5, "no": 0.5}]
        self.assertAlmostEqual(flip_rate([same, same, same, flip]), 0.25)
        self.assertEqual(flip_rate([]), 0.0)

    def test_cost_saved(self):
        self.assertAlmostEqual(cost_saved(0.7, 0.0, 1.0), 0.7)
        self.assertAlmostEqual(cost_saved(0.0, 0.01, 1.0), -0.01)
        with self.assertRaises(ValueError):
            cost_saved(0.5, 0.01, 0)

    def test_no_cases(self):
        with self.assertRaises(ValueError):
            bar_report([])


if __name__ == "__main__":
    unittest.main()
