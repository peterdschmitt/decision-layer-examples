"""Offline checks of the routing rules. Made-up answers, not model output."""

import unittest

from request import build_body, strip_template
from route import accuracy_by_language, route

CHAT = {"messages": ["I'd like to know more about your services", "How much is the visa package?"],
        "chat_owner": "specialist_a", "contact_already_collected": False}


def answers(choice="answer", conf=0.95, stop=0.02):
    return {"action": {"choice": choice, "confidence": conf}, "stop_contact": {"noul": stop}}


class RouteTest(unittest.TestCase):
    def test_confident_answer_acts_without_the_llm(self):
        r = route(answers("answer", 0.93), CHAT)
        self.assertEqual((r["action"], r["by"]), ("answer", "decision_model"))

    def test_unsure_or_missing_confidence_goes_to_the_llm(self):
        for c in (0.84, 0.4, None):
            self.assertEqual(route(answers("hand_over", c), CHAT)["action"], "llm_review")

    def test_stop_request_wins_over_everything(self):
        self.assertEqual(route(answers("answer", 0.99, stop=0.7), CHAT)["action"], "stop_contact")

    def test_no_repeat_handover_after_contact_collected(self):
        chat = dict(CHAT, contact_already_collected=True, handed_over=True)
        self.assertEqual(route(answers("hand_over", 0.9), chat)["action"], "answer")

    def test_template_line_is_stripped_before_the_model_sees_it(self):
        self.assertEqual(strip_template(CHAT["messages"]), ["How much is the visa package?"])
        self.assertNotIn("I'd like to know more about your services", build_body(CHAT)["state"]["messages"])

    def test_known_facts_are_sent_not_guessed(self):
        state = build_body(CHAT)["state"]
        self.assertEqual(state["chat_owner"], "specialist_a")
        self.assertFalse(state["contact_already_collected"])

    def test_accuracy_by_language_shows_the_weak_one(self):
        acc = accuracy_by_language([("en", True)] * 9 + [("en", False)] + [("ar", True)] * 3 + [("ar", False)])
        self.assertEqual(acc["en"], 0.9)
        self.assertEqual(acc["ar"], 0.75)


if __name__ == "__main__":
    unittest.main()
