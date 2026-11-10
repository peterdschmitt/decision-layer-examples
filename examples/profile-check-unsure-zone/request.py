"""One yes/no question per customer profile: do these records describe more than one person?
The criteria list the errors that appear in one person's records, which helped every model most in Hightouch's test."""

MODEL = "jev-1.13.0"  # re-test before moving to a newer version


def build_body(records: list) -> dict:
    return {
        "model": MODEL,
        "state": {"records": records},
        "questions": {
            "wrongly_joined": {
                "type": "noul",
                "instructions": "Do these records, joined into one customer profile, describe more than one real person?",
                "criteria": {
                    "true": "A completely different birth date (not a small typo), different given names that are not nicknames, "
                    "or two people in one household, such as a parent and child or twins",
                    "false": "Differences explained by data-entry errors in one person's records: typos (1978 -> 1973), "
                    "misread characters (Sam -> 5am), spelling by sound (Phillips -> Filips), nicknames (Robert -> Bob), "
                    "month and day swapped, a blank field, or a new address after a move",
                },
            }
        },
    }
