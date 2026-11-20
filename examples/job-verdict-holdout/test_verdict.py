import unittest
from verdict import top, choose_bar, answer, holdout_report, verdict, cost_cut


def case(p_yes, right, llm):
    return {"probs": {"yes": p_yes, "no": 1 - p_yes}, "right": right, "llm": llm}


class TestVerdict(unittest.TestCase):
    def test_top(self):
        self.assertEqual(top({"a": 0.2, "b": 0.8}), ("b", 0.8))

    def test_choose_bar_finds_lowest_good_bar(self):
        cal = [({"yes": 0.95, "no": 0.05}, "yes")] * 9 + [({"yes": 0.6, "no": 0.4}, "no")]
        self.assertEqual(choose_bar(cal, target=0.95), 0.61)

    def test_choose_bar_none_when_never_good(self):
        cal = [({"yes": 0.99, "no": 0.01}, "no")] * 5
        self.assertIsNone(choose_bar(cal))

    def test_answer_hands_unsure_to_llm(self):
        self.assertEqual(answer({"yes": 0.55, "no": 0.45}, "no", 0.8), ("no", "llm", None))
        self.assertEqual(answer({"yes": 0.9, "no": 0.1}, "no", 0.8)[1], "decision_model")
        self.assertEqual(answer({"yes": 0.99, "no": 0.01}, "no", None)[1], "llm")

    def test_switch_when_close_enough(self):
        hold = [case(0.9, "yes", "yes")] * 98 + [case(0.9, "no", "no")] * 2
        rep = holdout_report(hold, 0.8)
        self.assertEqual(verdict(rep), "switch")

    def test_couple_when_alone_falls_short(self):
        sure_right = [case(0.95, "yes", "yes")] * 60
        unsure_wrong = [case(0.55, "no", "no")] * 40  # decision model picks yes, wrongly
        rep = holdout_report(sure_right + unsure_wrong, 0.8)
        self.assertAlmostEqual(rep["decision_model_alone"], 0.6)
        self.assertAlmostEqual(rep["coupled"], 1.0)
        self.assertEqual(verdict(rep), "couple")

    def test_keep_llm_when_share_too_small(self):
        hold = [case(0.95, "yes", "yes")] * 10 + [case(0.55, "no", "no")] * 90
        self.assertEqual(verdict(holdout_report(hold, 0.8)), "keep_llm")

    def test_cost_cut(self):
        self.assertAlmostEqual(cost_cut(0.021, 0.09), 0.767, places=3)
        self.assertAlmostEqual(cost_cut(0.23, 1.27), 0.819, places=3)


if __name__ == "__main__":
    unittest.main()
