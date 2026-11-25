"""Offline demo with made-up conversations and a stand-in decision model."""
from judge import Question, answer, first_user_message, scorecard

TOPIC = Question("topic", "What is the opening request mainly about?",
                 ["bug fix", "feature", "refactor", "other"])

CONVOS = [
    {"id": "1", "turns": [{"role": "user", "text": "Checkout throws a 500 since this morning"}]},
    {"id": "2", "turns": [{"role": "user", "text": "Add CSV export to the report page"}]},
    {"id": "3", "turns": [{"role": "user", "text": "hmm"}]},
    {"id": "4", "turns": [{"role": "assistant", "text": "Welcome back"}]},
]


def stand_in_decide(q, lines):
    t = lines.lower()
    if "500" in t or "crash" in t:
        return {"bug fix": 0.93, "feature": 0.04, "refactor": 0.02, "other": 0.01}
    if "add" in t:
        return {"bug fix": 0.03, "feature": 0.91, "refactor": 0.03, "other": 0.03}
    return {"bug fix": 0.30, "feature": 0.30, "refactor": 0.20, "other": 0.20}


def stand_in_agent(convo, q):
    return "other"


if __name__ == "__main__":
    results = [answer(c, TOPIC, first_user_message, stand_in_decide, stand_in_agent) for c in CONVOS]
    for c, r in zip(CONVOS, results):
        print(c["id"], r.answer, "via", r.path, r.reason)
    print(scorecard(results, cost_fast=0.05, cost_agent=0.74))
