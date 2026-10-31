"""One yes/no question about a support ticket. The same body works for any decision model
that accepts the Jev request format (Cloudflare says Clef does); change MODEL per candidate."""

MODEL = "jev-1.14.0"  # pin the version you tested; one value per candidate in a shadow test


def build_body(ticket_text: str, model: str = MODEL) -> dict:
    return {
        "state": ticket_text,
        "model": model,
        "questions": {
            "urgent": {
                "type": "noul",
                "instructions": "Does this ticket need a person within the hour?",
                "criteria": {
                    "true": "Data loss, an outage, a security problem, or a customer who cannot work",
                    "false": "A question, a request or a problem that can wait for the normal queue",
                },
            },
        },
    }
