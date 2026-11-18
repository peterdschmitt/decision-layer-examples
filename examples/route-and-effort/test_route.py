import unittest

from route import (agreement_with_llm, choose_effort, choose_route, handle, share_by_source)


def model(table):
    return lambda key, options: table[key]["route" if "chat" in options else "effort"]


T = {
    "sure_chat": {"route": {"chat": 0.95, "agent": 0.05}, "effort": {"low": 0.9, "medium": 0.08, "high": 0.02}},
    "sure_agent": {"route": {"chat": 0.1, "agent": 0.9}, "effort": {"low": 0.1, "medium": 0.2, "high": 0.7}},
    "unsure": {"route": {"chat": 0.55, "agent": 0.45}, "effort": {"low": 0.45, "medium": 0.4, "high": 0.15}},
    "unsure_high": {"route": {"chat": 0.6, "agent": 0.4}, "effort": {"low": 0.1, "medium": 0.3, "high": 0.6}},
}


def down(*_):
    raise RuntimeError("down")


class RouteTests(unittest.TestCase):
    def test_confident_route_is_taken(self):
        self.assertEqual(choose_route("sure_agent", model(T), lambda r: "chat")[:2], ("agent", "decision_model"))

    def test_unsure_route_goes_to_llm_router(self):
        self.assertEqual(choose_route("unsure", model(T), lambda r: "agent")[:2], ("agent", "llm"))

    def test_both_down_uses_default(self):
        self.assertEqual(choose_route("sure_chat", down, down)[:2], ("chat", "rule"))

    def test_unsure_effort_steps_up(self):
        self.assertEqual(choose_effort("unsure", model(T))[:2], ("medium", "stepped_up"))

    def test_unsure_high_stays_high(self):
        self.assertEqual(choose_effort("unsure_high", model(T))[:2], ("high", "stepped_up"))

    def test_effort_model_down_uses_medium(self):
        self.assertEqual(choose_effort("x", down)[:2], ("medium", "rule"))

    def test_handle_sends_to_worker_with_effort(self):
        workers = {"chat": lambda r, e: f"chat:{e}", "agent": lambda r, e: f"agent:{e}"}
        rec = handle("sure_agent", model(T), lambda r: "chat", workers)
        self.assertEqual(rec["answer"], "agent:high")
        self.assertEqual(rec["route_by"], "decision_model")

    def test_agreement_and_share(self):
        past = [{"request": "sure_chat", "llm_route": "chat"}, {"request": "sure_agent", "llm_route": "agent"},
                {"request": "unsure", "llm_route": "agent"}]
        self.assertEqual(agreement_with_llm(model(T), past), {"same_route": 0.667, "decided_alone": 0.667})
        recs = [{"route_by": "decision_model"}, {"route_by": "decision_model"}, {"route_by": "llm"}]
        self.assertEqual(share_by_source(recs), {"decision_model": 0.667, "llm": 0.333})


if __name__ == "__main__":
    unittest.main()
