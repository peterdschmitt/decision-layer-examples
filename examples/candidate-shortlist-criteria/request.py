"""One Score question per criterion in the role's hiring brief, all in one request."""

MODEL = "jev-1.14.0"  # pin the version you tested

# A made-up brief. In practice the hiring team agrees the criteria and levels per role.
BRIEF = {
    "role": "Head of Sales, B2B software, 40-person startup, selling to mid-market finance teams.",
    "criteria": [
        {"id": "team", "name": "Has built and led a B2B sales team", "weight": 0.4,
         "levels": ["Never managed sellers", "Ran a small team (under 10)", "Grew a team past 20 sellers"]},
        {"id": "market", "name": "Has sold to finance buyers", "weight": 0.3,
         "levels": ["No finance buyers", "Some finance deals", "Finance teams were the main buyer"]},
        {"id": "stage", "name": "Has worked at an early-stage company", "weight": 0.3,
         "levels": ["Only large companies", "Some startup time", "Built sales from scratch at a startup"]},
    ],
}


def build_body(candidate: str, brief: dict = BRIEF) -> dict:
    return {
        "state": f"ROLE:\n{brief['role']}\n\nCANDIDATE:\n{candidate}",
        "model": MODEL,
        "questions": {
            c["id"]: {"type": "score", "instructions": c["name"], "criteria": c["levels"]}
            for c in brief["criteria"]
        },
    }
