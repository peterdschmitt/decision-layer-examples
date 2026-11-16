"""Choose, then write. The decision model picks an owner (or "drop") for every item, code does the
calendar math, and a cheaper LLM merges repeats and writes names and notes. Offline: the decision
model, the LLM and the old path are passed in as functions.
"""

import datetime as dt

FIXED_HOLIDAYS = {(1, 1), (2, 11), (2, 23), (4, 29), (5, 3), (5, 4), (5, 5), (8, 11), (11, 3), (11, 23)}
EQUINOXES = {dt.date(2026, 3, 20), dt.date(2026, 9, 23), dt.date(2027, 3, 21), dt.date(2027, 9, 23)}
# Offline fallback only: Monday holidays and other years need jpholiday.


def _named_holiday(day: dt.date) -> bool:
    return (day.month, day.day) in FIXED_HOLIDAYS or day in EQUINOXES


def is_holiday(day: dt.date) -> bool:
    """Calendar facts come from code, not the model. Uses jpholiday when installed; otherwise a
    short fixed list plus the substitute-holiday rule (a Sunday holiday moves to Monday)."""
    try:
        import jpholiday  # type: ignore

        return jpholiday.is_holiday(day)
    except ImportError:
        if _named_holiday(day):
            return True
        return day.weekday() == 0 and _named_holiday(day - dt.timedelta(days=1))


def add_calendar_flags(items):
    """Write weekday and holiday into each item before the model sees it, and drop days that are
    holidays in their own right ("Substitute holiday" is a calendar fact, not an event)."""
    out = []
    for item in items:
        day = dt.date.fromisoformat(item["date"])
        flagged = {**item, "weekday": day.strftime("%A"), "holiday": is_holiday(day)}
        if flagged["holiday"] and item.get("is_holiday_name"):
            continue
        out.append(flagged)
    return out


def newest_document_wins(items, scores, bar=0.8):
    """Same date and same name: if the newest document's copy is dropped at `bar` or higher,
    drop the older copies too."""
    newest = {}
    for item in items:
        key = (item["date"], item["title"])
        if key not in newest or item["doc_date"] > newest[key]["doc_date"]:
            newest[key] = item
    for item in items:
        top = newest[(item["date"], item["title"])]
        if scores[top["id"]].get("drop", 0) >= bar:
            scores[item["id"]] = {**scores[item["id"]], "drop": 1.0}
    return scores


def route(items, decide, write, fallback, drop_bar=0.5):
    """Lean toward keeping: drop an item only when the chance of "drop" is at least `drop_bar`.
    If either step fails, run the old LLM-only path. Anything the LLM leaves out goes back in."""
    try:
        scores = newest_document_wins(items, decide(items))  # decision model: chance per option
        kept = []
        for item in items:
            probs = scores[item["id"]]
            if probs.get("drop", 0) >= drop_bar:
                continue
            owner = max((o for o in probs if o != "drop"), key=probs.get)
            kept.append({**item, "owner": owner, "confidence": probs[owner]})
        merged = write(kept)  # LLM: merge repeats, write names and notes
    except Exception:
        return fallback(items), "old_llm"
    covered = {i for m in merged for i in m["ids"]}
    lost = [{"ids": [k["id"]], "owner": k["owner"], "name": k["title"]} for k in kept if k["id"] not in covered]
    return merged + lost, "decision_model"


def split_cases(items, scores, low=0.5, high=0.6):
    """Items whose top answer sits in the split zone. Read these before go-live and turn each
    pattern into a written rule; don't queue them for a person forever."""
    out = []
    for item in items:
        top = max(scores[item["id"]].values())
        if low <= top <= high:
            out.append((item["id"], item["title"], round(top, 2)))
    return out


def compare(new, old):
    """Dry-run diff against today's output: what was added, removed or moved to another owner."""
    new_map = {m["name"]: m["owner"] for m in new}
    old_map = {m["name"]: m["owner"] for m in old}
    return {
        "added": sorted(set(new_map) - set(old_map)),
        "removed": sorted(set(old_map) - set(new_map)),
        "moved": sorted(n for n in set(new_map) & set(old_map) if new_map[n] != old_map[n]),
    }
