"""One choice question per ticket: which label fits? Each label is one or two plain sentences,
plus a "none" option, the shape Amazon's engineers used. These labels are examples; use your own list."""

MODEL = "jev-1.13.0"  # or any decision model that takes this request format; re-test before moving versions

LABELS = {
    "customer_escalation": "A customer, or someone on a customer's behalf, reports a problem that needs a fast answer.",
    "capacity_request": "Someone asks for more computing, storage or quota for a service.",
    "automated_alarm": "A monitoring system opened the ticket because a metric crossed a limit.",
    "security_finding": "A scan or a person reports a possible security weakness or exposure.",
    "access_request": "Someone asks for permission to a system, tool or data set.",
    "none": "None of the other labels fits this ticket.",
}


def build_body(ticket: dict) -> dict:
    # Sort keys: Amazon found that field order alone moved probabilities by up to 0.19.
    return {
        "model": MODEL,
        "state": {"ticket": dict(sorted(ticket.items()))},
        "questions": {
            "label": {
                "type": "choice",
                "instructions": "Which label fits this ticket best?",
                "criteria": LABELS,
            }
        },
    }
