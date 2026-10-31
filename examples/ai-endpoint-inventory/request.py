"""Two yes/no questions about one API endpoint, asked over a trimmed sample of its traffic."""

MODEL = "jev-1.14.0"  # pin the version you tested


def build_body(trimmed_spans: str) -> dict:
    return {
        "state": trimmed_spans,
        "model": MODEL,
        "questions": {
            "is_ai_api": {
                "type": "noul",
                "instructions": "Does this endpoint send request content to an AI model?",
                "criteria": {
                    "true": "Prompt-like fields, chat messages, or calls to a known AI vendor host",
                    "false": "Ordinary data in and out, with no sign of a model call",
                },
            },
            "returns_ai": {
                "type": "noul",
                "instructions": "Does this endpoint return AI-generated content?",
                "criteria": {
                    "true": "The response carries generated text, completions or model output",
                    "false": "The response is stored or computed data",
                },
            },
        },
    }
