import unittest
from alerts import final_call, Explainer, compare_with_past, sweep_bar


def fixed(p):
    return lambda q, ctx: p


class FinalCall(unittest.TestCase):
    def test_hides_only_clear_false_alarm(self):
        self.assertFalse(final_call("x", fixed(0.2))["alert"])   # 80% sure it's noise
        self.assertTrue(final_call("x", fixed(0.6))["alert"])

    def test_exactly_at_bar_hides(self):
        self.assertFalse(final_call("x", fixed(0.5))["alert"])   # 1 - 0.5 >= 0.5

    def test_decision_model_failure_goes_to_llm(self):
        def broken(q, c): raise TimeoutError
        r = final_call("x", broken, llm_judge=lambda c: False)
        self.assertEqual(r, {"alert": False, "by": "LLM"})

    def test_bad_probability_counts_as_failure(self):
        r = final_call("x", fixed(1.7), llm_judge=lambda c: True)
        self.assertEqual(r["by"], "LLM")

    def test_both_fail_raises_alert(self):
        def broken(*a): raise RuntimeError
        self.assertEqual(final_call("x", broken, broken), {"alert": True, "by": "fail-safe"})
        self.assertEqual(final_call("x", broken)["by"], "fail-safe")


class Explain(unittest.TestCase):
    def test_llm_called_once_per_alert(self):
        e = Explainer(lambda d: "Query time is far above its normal range.")
        e.why("a1", {}); e.why("a1", {}); e.why("a2", {})
        self.assertEqual(e.calls, 2)

    def test_failure_stores_nothing(self):
        def boom(d): raise RuntimeError
        e = Explainer(boom)
        self.assertIsNone(e.why("a1", {}))
        self.assertNotIn("a1", e.store)

    def test_unopened_alerts_cost_nothing(self):
        e = Explainer(lambda d: "text")
        self.assertEqual(e.calls, 0)


class Compare(unittest.TestCase):
    cases = [{"context": "real", "past_alert": True}, {"context": "noise", "past_alert": False},
             {"context": "noise2", "past_alert": False}, {"context": "real2", "past_alert": True}]

    def test_direction_of_disagreement(self):
        p = {"real": 0.9, "noise": 0.1, "noise2": 0.7, "real2": 0.3}
        r = compare_with_past(self.cases, lambda q, c: p[c])
        self.assertEqual((r.agree, r.extra_alerts, r.hidden_real, r.total), (2, 1, 1, 4))
        self.assertAlmostEqual(r.agreement, 0.5)

    def test_sweep_shows_hidden_real_falling_as_bar_rises(self):
        p = {"real": 0.9, "noise": 0.1, "noise2": 0.25, "real2": 0.35}
        rows = sweep_bar(self.cases, lambda q, c: p[c], bars=(0.5, 0.7))
        self.assertEqual(rows[0][2], 1)   # at 0.5, real2 (65% "noise") is hidden
        self.assertEqual(rows[1][2], 0)   # at 0.7, it is raised


if __name__ == "__main__":
    unittest.main()
