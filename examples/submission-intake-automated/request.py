"""One yes/no question per fact the LLM extracted: does the source support it?

The state holds the source document and the facts, each under its own label.
"""

import json

MODEL = "jev-1.13.0"


def build_body(source: str, facts: dict) -> dict:
    questions = {
        name: {
            "type": "noul",
            "instructions": (
                f"Is the extracted fact '{name}' fully supported by the source "
                "submission? Answer no if the source contradicts it or doesn't say it."
            ),
            "criteria": {
                "true": "The source states this fact or clearly implies it",
                "false": "The source contradicts this fact or does not mention it",
            },
        }
        for name in facts
    }
    return {
        "state": {"source_submission": source, "extracted_facts": json.dumps(facts, indent=2)},
        "model": MODEL,
        "questions": questions,
    }
