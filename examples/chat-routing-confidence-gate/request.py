"""One routing decision about a customer's latest chat message. Facts the model can't see in
the text (who owns the chat, what the customer already gave us) are computed in code and sent."""

import re

MODEL = "jev-1.13.0"  # the version Entagl tested; re-test before moving to a newer one

# Click-to-chat ads open with a template line; it says nothing about what the customer wants.
TEMPLATE_LINES = [r"^i'?d like to know more about your services\.?$"]


def strip_template(messages):
    return [m for m in messages if not any(re.match(p, m.strip(), re.I) for p in TEMPLATE_LINES)]


def build_body(chat: dict) -> dict:
    return {
        "model": MODEL,
        "state": {
            "messages": strip_template(chat["messages"])[-8:],
            "chat_owner": chat.get("chat_owner"),
            "contact_already_collected": bool(chat.get("contact_already_collected")),
        },
        "questions": {
            "action": {
                "type": "choice",
                "instructions": "What should we do with the customer's latest message?",
                "criteria": {
                    "answer": "We can answer it from the client's information",
                    "hand_over": "A person on the client's team needs to take it",
                    "canned_reply": "One of the client's standard replies fits",
                    "ignore": "Nothing to do: thanks, emojis, spam",
                },
            },
            "stop_contact": {
                "type": "noul",
                "instructions": "Does the customer ask us to stop contacting them?",
                "criteria": {
                    "true": "An explicit request to stop messages or calls, in any language",
                    "false": "Anything else, including 'not interested right now'",
                },
            },
        },
    }
