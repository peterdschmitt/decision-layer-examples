"""One request per candidate product: one yes/no question, does this product match what the shopper
asked for? The shape Rakuten describes for Ichiba search (product photos, description, full context).
The wording is ours; Rakuten has not published its question or its model."""

MODEL = "jev-1.14"  # or any decision model that takes this request format; re-test before moving versions

QUESTION = "Does this product match what the shopper is looking for, including every requirement in the search?"


def build_body(search: str, product: dict) -> dict:
    return {
        "model": MODEL,
        "state": f"Shopper's search: {search}\nProduct title: {product['title']}\nDescription: {product.get('description', '')}",
        "images": product.get("images", []),
        "questions": {
            "match": {
                "type": "noul",
                "instructions": QUESTION,
                "criteria": {"true": "The product meets the shopper's requirements.", "false": "It does not."},
            }
        },
    }
