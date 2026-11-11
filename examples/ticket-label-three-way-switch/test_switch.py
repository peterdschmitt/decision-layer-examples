"""Offline checks of the switch. Made-up probabilities, not model output."""

import unittest

from request import build_body
from switch import label_ticket, ready_to_switch, side_by_side_report

SURE = {"automated_alarm": 0.95, "capacity_request": 0.03, "none": 0.02}
UNSURE = {"automated_alarm": 0.55, "capacity_request": 0.40, "none": 0.05}
NONE = {"automated_alarm": 0.05, "none": 0.92}


def never(*_):
    raise AssertionError("should not be called")


class SwitchTest(unittest.TestCase):
    def test_llm_mode_never_calls_the_decision_model(self):
        self.assertEqual(label_ticket({}, "llm", never, lambda t: "capacity_request"), ("capacity_request", "llm"))

    def test_both_mode_uses_the_llm_and_logs_the_decision_model(self):
        log = []
        out = label_ticket({"id": "T1"}, "both", lambda t: SURE, lambda t: "capacity_request", log)
        self.assertEqual(out, ("capacity_request", "llm"))
        self.assertEqual(log[0]["decision_model"], "automated_alarm")

    def test_decision_model_mode_acts_above_the_bar_only(self):
        self.assertEqual(label_ticket({}, "decision_model", lambda t: SURE, never), ("automated_alarm", "decision_model"))
        self.assertEqual(label_ticket({}, "decision_model", lambda t: UNSURE, lambda t: "x"), ("x", "llm"))

    def test_none_goes_to_the_llm_even_when_sure(self):
        self.assertEqual(label_ticket({}, "decision_model", lambda t: NONE, lambda t: "x"), ("x", "llm"))

    def test_decision_model_down_falls_back_to_the_llm(self):
        def down(_):
            raise TimeoutError

        self.assertEqual(label_ticket({}, "decision_model", down, lambda t: "x"), ("x", "llm"))


LOG = [
    {"ticket": "T1", "llm": "automated_alarm", "decision_model": "automated_alarm", "sure": 0.95},
    {"ticket": "T2", "llm": "capacity_request", "decision_model": "capacity_request", "sure": 0.91},
    {"ticket": "T3", "llm": "security_finding", "decision_model": "access_request", "sure": 0.85},
    {"ticket": "T4", "llm": "customer_escalation", "decision_model": "automated_alarm", "sure": 0.40},
]


class ReportTest(unittest.TestCase):
    def test_report_counts_only_tickets_above_the_bar(self):
        r = side_by_side_report(LOG, bar=0.8)
        self.assertEqual(r["share_above_bar"], 0.75)
        self.assertAlmostEqual(r["agreement_above_bar"], 2 / 3)
        self.assertEqual([d["ticket"] for d in r["disagreements"]], ["T3"])

    def test_not_ready_until_disagreements_are_read_and_agreement_is_high(self):
        r = side_by_side_report(LOG, bar=0.8)
        self.assertFalse(ready_to_switch(r, min_agreement=0.6))  # T3 unread
        self.assertTrue(ready_to_switch(r, min_agreement=0.6, read=["T3"]))
        self.assertFalse(ready_to_switch(r, min_agreement=0.98, read=["T3"]))


class RequestTest(unittest.TestCase):
    def test_keys_are_sorted_and_none_is_an_option(self):
        body = build_body({"title": "a", "body": "b", "id": "c"})
        self.assertEqual(list(body["state"]["ticket"]), ["body", "id", "title"])
        self.assertIn("none", body["questions"]["label"]["criteria"])


if __name__ == "__main__":
    unittest.main()
