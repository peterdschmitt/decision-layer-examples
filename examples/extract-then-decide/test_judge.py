import unittest
from judge import (Question, Result, answer, sureness, first_user_message, all_user_messages,
                   check_sample, ready_to_switch, drifted, scorecard)

TOPIC = Question("topic", "What is the opening request mainly about?",
                 ["bug fix", "feature", "refactor", "other"])


def convo(cid, *turns):
    return {"id": cid, "turns": [{"role": r, "text": t} for r, t in turns]}


def agent(c, q):
    return "agent-answer"


def sure_decide(q, lines):
    return {"bug fix": 0.94, "feature": 0.03, "refactor": 0.02, "other": 0.01}


def unsure_decide(q, lines):
    return {"bug fix": 0.40, "feature": 0.35, "refactor": 0.15, "other": 0.10}


class TestJudge(unittest.TestCase):
    def test_sureness_bounds(self):
        self.assertAlmostEqual(sureness({"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25}), 0.0)
        self.assertAlmostEqual(sureness({"a": 1.0, "b": 0.0}), 1.0)
        self.assertAlmostEqual(sureness({"a": 0.35, "b": 0.25, "c": 0.2, "d": 0.2}), 0.1333, places=3)

    def test_sure_answer_stands(self):
        c = convo("1", ("user", "The login page crashes"), ("assistant", "Looking"))
        r = answer(c, TOPIC, first_user_message, sure_decide, agent)
        self.assertEqual((r.answer, r.path), ("bug fix", "decision model"))

    def test_below_bar_goes_to_agent(self):
        c = convo("2", ("user", "Can you look at this?"))
        r = answer(c, TOPIC, first_user_message, unsure_decide, agent)
        self.assertEqual((r.path, r.reason), ("agent", "below the bar"))

    def test_extract_failure_goes_to_agent(self):
        c = convo("3", ("assistant", "Hello"))
        r = answer(c, TOPIC, first_user_message, sure_decide, agent)
        self.assertEqual(r.path, "agent")
        self.assertIn("no user turn", r.reason)

    def test_too_long_goes_to_agent(self):
        q = Question("topic", "?", TOPIC.answers, max_chars=10)
        c = convo("4", ("user", "x" * 50))
        self.assertEqual(answer(c, q, first_user_message, sure_decide, agent).path, "agent")

    def test_unexpected_answers_go_to_agent(self):
        c = convo("5", ("user", "fix it"))
        r = answer(c, TOPIC, first_user_message, lambda q, l: {"yes": 0.9, "no": 0.1}, agent)
        self.assertEqual(r.reason, "unexpected answers")

    def test_all_user_messages(self):
        c = convo("6", ("user", "a"), ("assistant", "b"), ("user", "c"))
        self.assertEqual(all_user_messages(c), "a\nc")

    def test_sample_check_blocks_switch_when_extract_misses(self):
        sample = [convo("a", ("user", "fix crash")), convo("b", ("user", "fix crash"))]
        person = {"a": "bug fix", "b": "feature"}
        chk = check_sample(sample, TOPIC, first_user_message, sure_decide, agent, person,
                           answer_in_extract=lambda cid: cid != "b")
        self.assertEqual(chk.agreement, 0.5)
        self.assertEqual(chk.misses_outside_extract, ["b"])
        self.assertFalse(ready_to_switch(chk, agent_agreement=0.5))

    def test_ready_to_switch(self):
        sample = [convo(str(i), ("user", "fix crash")) for i in range(10)]
        person = {str(i): "bug fix" for i in range(10)}
        chk = check_sample(sample, TOPIC, first_user_message, sure_decide, agent, person, lambda cid: True)
        self.assertTrue(ready_to_switch(chk, agent_agreement=0.95))

    def test_drift(self):
        self.assertFalse(drifted(["a"] * 10, ["a"] * 9 + ["b"]))
        self.assertTrue(drifted(["a"] * 10, ["a"] * 8 + ["b"] * 2))

    def test_scorecard(self):
        rs = [Result("x", "decision model")] * 8 + [Result("y", "agent")] * 2
        s = scorecard(rs, cost_fast=0.05, cost_agent=0.74)
        self.assertAlmostEqual(s["share_decision_model"], 0.8)
        self.assertAlmostEqual(s["cost_vs_agent_only"], (8 * 0.05 + 2 * 0.79) / 7.4)


if __name__ == "__main__":
    unittest.main()
