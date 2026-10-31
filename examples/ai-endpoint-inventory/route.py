"""Turn the two probabilities into the inventory record, or send the endpoint to an LLM.

The band (0.2 to 0.8) is the one Harness says it is deploying. It was drawn from a
500-endpoint test; check it on your own labelled endpoints before relying on it.
"""

LOW, HIGH = 0.2, 0.8
RETURNS_BAR = 0.5  # placeholder


def route(answers: dict) -> dict:
    p = answers["is_ai_api"].get("noul")
    if p is None or LOW < p < HIGH:
        # Unsure: one LLM call decides and writes the reason.
        return {"action": "llm_review", "probability": p}
    is_ai = p >= HIGH
    record = {
        "action": "record",
        "is_ai_api": is_ai,
        "returns_ai_generated_content": is_ai and (answers["returns_ai"].get("noul") or 0.0) >= RETURNS_BAR,
        "probability": p,
    }
    if is_ai:
        record["reason"] = None  # written later by the LLM enrichment call that already runs on positives
    else:
        record["reason"] = "No prompt-like fields, no known AI vendor host, low AI-API probability"
    return record
