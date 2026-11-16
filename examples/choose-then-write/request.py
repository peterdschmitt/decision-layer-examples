"""One request for a whole batch: the shared rules go in once, and each item becomes one choice question.

This is the shape a parent described for routing school-letter events to family calendars with
Gemini Decision 1 (Zenn, Nov. 15, 2026): shared rules billed once, one choice per item, weekday and
holiday worked out in code and written into the question. The wording here is ours.
"""

MODEL = "gemini-decision-1"  # or any decision model that takes a shared input plus many choice questions

# One option per owner, plus "drop". Describe each owner the way the rules do.
OPTIONS = {
    "eldest_daughter": "Elementary-school events for her grade or class, or the whole school.",
    "eldest_son": "Kindergarten events for his class or all children.",
    "younger_son": "Events for the youngest child.",
    "father": "Events a parent must attend or act on, assigned to the father.",
    "mother": "Events a parent must attend or act on, assigned to the mother.",
    "family": "Days that change the whole family's plans.",
    "event": "Optional gatherings, sign-up events, exhibitions you may choose to visit.",
    "drop": "Events only for other grades or classes, and anything the rules exclude.",
}


def build_body(rules: str, items: list) -> dict:
    questions = {}
    for item in items:
        day = item["weekday"] + (", holiday" if item.get("holiday") else "")
        questions[item["id"]] = {
            "type": "choice",
            "criteria": OPTIONS,
            "instructions": (
                f"Which calendar should this event go on? Date: {item['date']} ({day}). "
                f"Event: {item['title']}. Grade or class: {item.get('grade') or 'not stated'}."
            ),
        }
    return {"model": MODEL, "input": rules, "questions": questions}
