"""One question about a scheduled task: did it succeed? Answer descriptions do the work.
Kiva fixed its false "failed" notices by adding one sentence to needs_human (see README)."""

MODEL = "jev-1.13.0"  # the version Kiva wrote about; re-test before moving to a newer one


def build_body(last_message: str) -> dict:
    return {
        "model": MODEL,
        "state": {"last_message": last_message},
        "questions": {
            "outcome": {
                "type": "choice",
                "instructions": "Did the scheduled task achieve what it was asked to do?",
                "criteria": {
                    "succeeded": "The task finished the work it was asked to do",
                    "failed": "The task stopped early, errored, or did not do the work",
                    "needs_human": (
                        "The task could not go on without a person's decision. "
                        "Finishing the work and then handing results to a person does not count as this."
                    ),
                },
            }
        },
    }
