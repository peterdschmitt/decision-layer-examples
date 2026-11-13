"""One request per page: every known question rides along as its own yes/no question, so the page
image is paid for once. The shape Subworkflow tested. The questions are examples; use your own columns."""

MODEL = "jev-1.14"  # or any decision model that takes this request format; re-test before moving versions

QUESTIONS = {
    "invoice_total": "Does this page show the total amount due on invoice {invoice}?",
    "signatory": "Does this page show who signed the supply agreement?",
    "termination": "Does this page say when the supply agreement can be terminated?",
}


def build_body(page_image_b64: str, questions: dict) -> dict:
    return {
        "model": MODEL,
        "state": "One page from a document bundle.",
        "images": [page_image_b64],
        "questions": {
            key: {
                "type": "noul",
                "instructions": text,
                "criteria": {"true": "The answer is on this page.", "false": "The answer is not on this page."},
            }
            for key, text in questions.items()
        },
    }
