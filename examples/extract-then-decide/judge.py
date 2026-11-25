"""Extract, then decide: answer small questions about every AI conversation.

An LLM writes and tests a small extraction function once per question.
Code runs it on every conversation. A decision model answers from the
extract with a percentage per allowed answer. Anything the code can't
handle, or the decision model is unsure about, goes to an LLM agent that
reads the whole conversation.

Expected, not measured: the model calls are stand-ins here.
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass
class Question:
    name: str
    text: str
    answers: List[str]
    max_chars: int = 4000      # what the decision model can take in
    bar: float = 0.5           # how sure it must be before its answer stands


def sureness(probs: Dict[str, float]) -> float:
    """0 when the percentages are spread evenly, 1 when all sit on one answer."""
    n = len(probs)
    if n < 2:
        return 1.0
    top = max(probs.values())
    return max(0.0, (top - 1 / n) / (1 - 1 / n))


@dataclass
class Result:
    answer: str
    path: str                  # "decision model" or "agent"
    reason: str = ""


def answer(convo, q: Question, extract: Callable, decide: Callable, agent: Callable) -> Result:
    try:
        lines = extract(convo)
    except Exception as e:     # code failed: the conversation looks different
        return Result(agent(convo, q), "agent", f"extract failed: {e}")
    if not lines or len(lines) > q.max_chars:
        return Result(agent(convo, q), "agent", "nothing found or too long")
    probs = decide(q, lines)
    if set(probs) != set(q.answers):
        return Result(agent(convo, q), "agent", "unexpected answers")
    best = max(probs, key=probs.get)
    if sureness(probs) < q.bar:
        return Result(agent(convo, q), "agent", "below the bar")
    return Result(best, "decision model")


def first_user_message(convo) -> str:
    """Example extraction: keep only the opening request."""
    for turn in convo["turns"]:
        if turn["role"] == "user":
            text = turn["text"].strip()
            if not text:
                raise ValueError("empty request")
            return text
    raise ValueError("no user turn")


def all_user_messages(convo) -> str:
    """Example extraction: every user message, for a question like frustration."""
    msgs = [t["text"].strip() for t in convo["turns"] if t["role"] == "user" and t["text"].strip()]
    if not msgs:
        raise ValueError("no user turn")
    return "\n".join(msgs)


@dataclass
class SampleCheck:
    agreed: int = 0
    total: int = 0
    misses_outside_extract: List[str] = field(default_factory=list)

    @property
    def agreement(self) -> float:
        return self.agreed / self.total if self.total else 0.0


def check_sample(sample, q, extract, decide, agent, person_answers, answer_in_extract) -> SampleCheck:
    """Before switching a question over: compare with answers a person set.

    answer_in_extract(convo_id) says whether the person found the deciding
    lines inside what the code pulled out. Misses where it did not mean the
    extract is not enough, and the question should stay with the agent.
    """
    c = SampleCheck()
    for convo in sample:
        r = answer(convo, q, extract, decide, agent)
        c.total += 1
        if r.answer == person_answers[convo["id"]]:
            c.agreed += 1
        elif not answer_in_extract(convo["id"]):
            c.misses_outside_extract.append(convo["id"])
    return c


def ready_to_switch(check: SampleCheck, agent_agreement: float, slack: float = 0.02) -> bool:
    """Switch only if no miss came from lines the code left out, and agreement
    is within `slack` of the agent reading everything."""
    return not check.misses_outside_extract and check.agreement >= agent_agreement - slack


def drifted(recent_fast: List[str], recent_agent: List[str], floor: float = 0.85) -> bool:
    """Scheduled recheck: rerun a recent sample through the agent and compare."""
    if not recent_fast:
        return False
    same = sum(a == b for a, b in zip(recent_fast, recent_agent))
    return same / len(recent_fast) < floor


def scorecard(results: List[Result], cost_fast: float, cost_agent: float) -> Dict[str, float]:
    """Share answered by the decision model, and cost against sending all to the agent."""
    n = len(results)
    fast = sum(r.path == "decision model" for r in results)
    cost = fast * cost_fast + (n - fast) * (cost_agent + cost_fast)
    return {
        "share_decision_model": fast / n if n else 0.0,
        "cost_vs_agent_only": cost / (n * cost_agent) if n else 0.0,
    }
