"""Pass supported facts forward; send the rest back to the LLM or to a person.

Thresholds are placeholders. A fact must clear a high bar to pass, because an
unsupported fact that reaches an underwriter is worse than a missing one.
"""

SUPPORTED_BAR = 0.85
UNSUPPORTED_BAR = 0.3


def route(answers: dict) -> dict:
    result = {"pass_to_underwriter": [], "send_back_to_llm": [], "person_checks": []}
    for fact, answer in answers.items():
        p = answer["noul"]
        if p >= SUPPORTED_BAR:
            result["pass_to_underwriter"].append(fact)
        elif p <= UNSUPPORTED_BAR:
            result["send_back_to_llm"].append(fact)   # re-extract with the source quote
        else:
            result["person_checks"].append(fact)      # genuinely unclear
    return result
