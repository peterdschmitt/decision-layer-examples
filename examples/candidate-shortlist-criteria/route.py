"""Combine the criterion scores into one first score, then shortlist.

The weights and the shortlist size are placeholders. Set them from a test on your
own past roles: every candidate a hiring manager asked to meet, plus a fair sample
of the rest. Count how many of those "winners" each setting keeps.
"""

from request import BRIEF

SHORTLIST_SIZE = 2000  # Jack & Jill's published first-stage cut; yours will differ


def first_score(answers: dict, brief: dict = BRIEF) -> float:
    """Weighted average of each criterion's score, each scaled to 0..1."""
    total = 0.0
    for c in brief["criteria"]:
        top = len(c["levels"]) - 1          # a Score lands between 0 and the last level
        score = answers[c["id"]].get("score")
        if score is None:                   # no answer: count it as the lowest level
            score = 0.0
        total += c["weight"] * min(max(score, 0.0), top) / top
    return round(total, 4)


def shortlist(scored: list, size: int = SHORTLIST_SIZE) -> list:
    """scored: [(candidate_id, first_score), ...]. Highest first; ties keep input order."""
    return [cid for cid, _ in sorted(scored, key=lambda x: x[1], reverse=True)[:size]]


def route(answers: dict) -> str:
    """For run.py: show the one sample candidate's first score."""
    return f"first_score={first_score(answers)}"
