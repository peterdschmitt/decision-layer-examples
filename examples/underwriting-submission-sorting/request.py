"""Four narrow questions about a small commercial submission."""

MODEL = "jev-1.13.0"


def build_body(submission: str) -> dict:
    return {
        "state": submission,
        "model": MODEL,
        "questions": {
            "business_class": {
                "type": "choice",
                "instructions": "Which class best describes this business's main operations?",
                "criteria": {
                    "other_or_unclear": "None of the below, or the text doesn't say",
                    "contractor_interior": "Interior remodeling, carpentry, painting, flooring",
                    "contractor_exterior": "Roofing, siding, exterior or structural work",
                    "restaurant": "Restaurant, bar or food service",
                    "retail": "A shop selling goods to the public",
                    "office": "Professional or office-based services",
                },
            },
            "hazardous_work": {
                "type": "noul",
                # "Even occasionally" catches the line a tired reader skims past.
                "instructions": "Does the text say the business does any roofing, work at heights, or demolition, even occasionally?",
                "criteria": {
                    "true": "Any roofing, work at heights or demolition is mentioned",
                    "false": "None of these is mentioned",
                },
            },
            "prior_loss_mentioned": {
                "type": "noul",
                "instructions": "Does the text mention any past insurance claim or loss?",
                "criteria": {
                    "true": "A past claim or loss is mentioned",
                    "false": "No past claim or loss is mentioned",
                },
            },
            "detail": {
                "type": "score",
                "instructions": "How well does the text describe what the business actually does day to day?",
                "criteria": [
                    "Too vague to tell what the business does",
                    "Main activity is clear, details are missing",
                    "Activities, staff and subcontracting are all described",
                ],
            },
        },
    }
