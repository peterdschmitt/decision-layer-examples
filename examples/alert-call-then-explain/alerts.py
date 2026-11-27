"""Alert call, then explain: a decision model makes the yes-or-no call on each
alert. An LLM writes an explanation only when a person asks, once per alert.
Every failure raises the alert.

Before switching, compare each decision model with your past calls and check
which way it is wrong: extra alerts (safer) or hidden real ones (dangerous).

Expected, not measured: the model calls here are stand-ins.
"""
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional

QUESTION = "Is this a real issue that requires attention?"


def final_call(context: str, decide: Callable, llm_judge: Optional[Callable] = None,
               hide_bar: float = 0.5) -> dict:
    """Hide an alert only when the decision model is at least `hide_bar` sure it is
    a false alarm. Decision model fails -> LLM decides. Both fail -> alert."""
    try:
        p_real = float(decide(QUESTION, context))
        if not 0.0 <= p_real <= 1.0:
            raise ValueError("probability out of range")
        return {"alert": (1 - p_real) < hide_bar, "by": "decision model", "p_real": p_real}
    except Exception:
        if llm_judge is not None:
            try:
                return {"alert": bool(llm_judge(context)), "by": "LLM"}
            except Exception:
                pass
        return {"alert": True, "by": "fail-safe"}


class Explainer:
    """Pay for the LLM's words once, and only when a person opens the alert."""

    def __init__(self, llm_explain: Callable):
        self.llm_explain = llm_explain
        self.store: Dict[str, str] = {}
        self.calls = 0

    def why(self, alert_id: str, details: dict) -> Optional[str]:
        if alert_id in self.store:
            return self.store[alert_id]
        try:
            text = self.llm_explain(details)
        except Exception:
            return None            # nothing stored, so the next request tries again
        self.calls += 1
        if text:
            self.store[alert_id] = text[:4000]
        return text or None


@dataclass
class Comparison:
    agree: int
    extra_alerts: int          # model alerts, past call hid it: noisier but safe
    hidden_real: int           # model hides, past call alerted: the dangerous kind
    total: int

    @property
    def agreement(self) -> float:
        return self.agree / self.total if self.total else 0.0


def compare_with_past(cases: Iterable[dict], decide: Callable, hide_bar: float = 0.5) -> Comparison:
    """cases: {'context': str, 'past_alert': bool}. No answer key needed, but
    remember this measures agreement with past calls, not accuracy."""
    agree = extra = hidden = total = 0
    for c in cases:
        now = final_call(c["context"], decide, None, hide_bar)["alert"]
        total += 1
        if now == c["past_alert"]:
            agree += 1
        elif now:
            extra += 1
        else:
            hidden += 1
    return Comparison(agree, extra, hidden, total)


def sweep_bar(cases: List[dict], decide: Callable, bars=(0.3, 0.5, 0.7, 0.9)) -> List[tuple]:
    """Agreement and hidden-real count at each bar, to choose one on your own data."""
    out = []
    for b in bars:
        r = compare_with_past(cases, decide, b)
        out.append((b, round(r.agreement, 3), r.hidden_real, r.extra_alerts))
    return out
