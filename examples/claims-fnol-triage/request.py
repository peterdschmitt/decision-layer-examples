"""Four narrow questions about a first notice of loss report."""

MODEL = "jev-1.13.0"


def build_body(report: str) -> dict:
    return {
        "state": report,
        "model": MODEL,
        "questions": {
            "loss_type": {
                "type": "choice",
                "instructions": "What kind of loss does this report describe?",
                "criteria": {
                    # Listed first so an unplaceable report leans toward a person.
                    "other_or_unclear": "None of the below, or the report doesn't say",
                    "auto_collision": "A vehicle hit another vehicle or an object",
                    "auto_glass": "Only windshield or window glass is damaged",
                    "property_water": "Water damage to a home or building",
                    "theft": "Something was stolen",
                },
            },
            "injury_mentioned": {
                "type": "noul",
                # Worded broadly on purpose: "a bit sore" should reach a person today.
                "instructions": "Does the reporter say anyone was hurt, sore, or in pain, even slightly?",
                "criteria": {
                    "true": "Any injury, pain or soreness is mentioned",
                    "false": "No one is described as hurt",
                },
            },
            "location_given": {
                "type": "noul",
                "instructions": "Does the report say where the loss happened?",
                "criteria": {
                    "true": "A place, road or address is named",
                    "false": "No location is given",
                },
            },
            "complexity": {
                "type": "score",
                "instructions": "How complicated does this claim look to handle?",
                "criteria": [
                    "One item, one party, facts are clear",
                    "A few items or a second party involved",
                    "Injuries, several parties, or disputed facts",
                ],
            },
        },
    }
