"""One request per summary: both narrow yes/no questions ride along together, so the text is paid
for once. The shape PostHog describes for Replay Vision. The wording is PostHog's; tune it to your data."""

MODEL = "jev-1.14"  # or any decision model that takes this request format; re-test the bar before moving versions

QUESTIONS = {
    "real_person": "Does this name a real person?",
    "contact_or_id": "Does this show contact details or an ID?",
}


def build_body(summary: str, questions: dict = QUESTIONS) -> dict:
    return {
        "model": MODEL,
        "state": summary,
        "questions": {
            key: {
                "type": "noul",
                "instructions": text,
                "criteria": {"true": "Yes, the summary contains it.", "false": "No, it does not."},
            }
            for key, text in questions.items()
        },
    }
