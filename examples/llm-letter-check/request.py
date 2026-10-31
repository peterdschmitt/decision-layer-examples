"""Questions the decision model asks about an LLM's draft letter.

The state holds two labeled parts: the facts from the claim file (from your
systems) and the LLM's draft. Every question compares the draft to the file.
"""

import json

MODEL = "jev-1.13.0"


def build_body(claim_file: dict, draft: str) -> dict:
    return {
        "state": {"claim_file": json.dumps(claim_file, indent=2), "draft_letter": draft},
        "model": MODEL,
        "questions": {
            "promises_outcome": {
                "type": "noul",
                "instructions": "Does the draft letter promise payment, coverage or a specific outcome that the claim file does not confirm?",
                "criteria": {
                    "true": "It promises payment, coverage or an outcome the file doesn't confirm",
                    "false": "It promises nothing beyond what the file confirms",
                },
            },
            "contradicts_file": {
                "type": "noul",
                "instructions": "Does any statement in the draft letter contradict the claim file?",
                "criteria": {
                    "true": "At least one statement conflicts with the file",
                    "false": "Every statement agrees with the file",
                },
            },
            "asks_for_all_documents": {
                "type": "noul",
                "instructions": "Does the draft letter ask for every document listed as needed in the claim file?",
                "criteria": {
                    "true": "Every needed document is requested",
                    "false": "At least one needed document is missing from the letter",
                },
            },
            "tone": {
                "type": "score",
                "instructions": "How appropriate is the tone of the draft letter for a customer who may be injured?",
                "criteria": [
                    "Dismissive, cold or overly casual",
                    "Polite but impersonal",
                    "Clear, respectful and acknowledges the customer's situation",
                ],
            },
        },
    }
