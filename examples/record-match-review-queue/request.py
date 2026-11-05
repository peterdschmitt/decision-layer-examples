"""One question per pair of donor records: same donor, different donor, or unsure.
The criteria say what counts as enough evidence, the change that fixed Southbridge's household question."""

MODEL = "jev-1.13.0"  # the version Southbridge tested; re-test before moving to a newer one


def build_body(record_a: dict, record_b: dict) -> dict:
    return {
        "model": MODEL,
        "state": {"record_a": record_a, "record_b": record_b},
        "questions": {
            "identity": {
                "type": "choice",
                "instructions": "Do these two donation records come from the same donor?",
                "criteria": {
                    "same": (
                        "Sufficient: the same surname and the same or clerically equivalent given name "
                        "(spelling, nickname, initial, or a middle name or suffix on only one record) "
                        "at the same residential street address, or at the same postal code with the same employer. "
                        "Differences only in employer, one blank field, or address formatting (DR vs DRIVE) do not distinguish donors."
                    ),
                    "different": "Different given names, or different addresses with no shared employer, or one is a business and the other a person",
                    "unsure": "The records do not give enough to say either way",
                },
            }
        },
    }
