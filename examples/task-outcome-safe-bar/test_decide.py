"""Offline checks of the decision rules. Made-up probabilities, not model output."""

import unittest

from decide import Decider, compare, notice
from request import build_body

MSG = "The investigation is complete. The two items that need a decision have been handed to the person in charge."


def fixed(probs):
    return lambda _text: probs


def down(_text):
    raise ConnectionError("decision model unavailable")


JEV = lambda probs: Decider("jev", fixed(probs), min_safe=0.7)
OLD_LLM = lambda probs: Decider("old_llm_prompt", fixed(probs), min_safe=0.9)


class NoticeTest(unittest.TestCase):
    def test_confident_success_sends_done(self):
        r = notice(MSG, JEV({"succeeded": 0.92, "failed": 0.03, "needs_human": 0.05}), OLD_LLM({}))
        self.assertEqual((r["notice"], r["by"]), ("done", "jev"))

    def test_bar_reads_the_safe_answer_not_the_top_pick(self):
        # The top pick is "succeeded" but only at 0.55: below the bar, so no "done" notice.
        r = notice(MSG, JEV({"succeeded": 0.55, "failed": 0.25, "needs_human": 0.20}), OLD_LLM({}))
        self.assertNotEqual(r["notice"], "done")

    def test_backup_keeps_its_own_higher_bar(self):
        # 0.8 would clear Jev's bar, but the old LLM's self-reported scores run high,
        # so the backup doesn't say "done": the user is asked to look instead.
        r = notice(MSG, Decider("jev", down, 0.7), OLD_LLM({"succeeded": 0.8, "failed": 0.2}))
        self.assertEqual((r["by"], r["notice"]), ("old_llm_prompt", "needs_you"))

    def test_backup_without_probabilities_does_not_silently_fail_everything(self):
        r = notice(MSG, Decider("jev", down, 0.7), Decider("fast_llm", fixed({}), 0.9))
        self.assertEqual(r["notice"], "hold")

    def test_handover_after_finishing_is_described_as_not_needs_human(self):
        crit = build_body(MSG)["questions"]["outcome"]["criteria"]["needs_human"]
        self.assertIn("does not count", crit)


class CompareTest(unittest.TestCase):
    def test_compare_lists_the_cases_each_decider_got_wrong(self):
        cases = [(MSG, "succeeded"), ("Error: login failed", "failed")]
        old = Decider("old", lambda t: {"failed": 0.7, "succeeded": 0.3} if "handed" in t else {"failed": 0.9}, 0.9)
        new = Decider("jev", lambda t: {"succeeded": 0.9} if "handed" in t else {"failed": 0.95, "succeeded": 0.05}, 0.7)
        rep = compare(cases, [old, new])
        self.assertEqual(rep["old"]["wrong"], [MSG])
        self.assertEqual(rep["jev"]["right"], 2)


if __name__ == "__main__":
    unittest.main()
