"""Minimal client for the TypeSafe System One API.

Standard library only. The request shape follows TypeSafe's API reference:
https://docs.typesafe.ai/api.md

The API key is read from the TYPESAFE_API_KEY environment variable when a
request is sent. It is never printed, logged or returned.
"""

import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://api.typesafe.ai/v1/systemone"


def ask(body: dict, timeout: float = 10.0) -> dict:
    """Send one request and return the "answers" object."""
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        sys.exit("TYPESAFE_API_KEY is not set. Export your own key, or use --dry-run.")
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.load(resp)["answers"]
    except urllib.error.HTTPError as err:
        # Report the status only; never echo the request, which carries the key.
        sys.exit(f"API returned HTTP {err.code}.")


def main(build_body, route, sample_path: str) -> None:
    """Shared command line for each example's run.py."""
    with open(sample_path, encoding="utf-8") as f:
        text = f.read().strip()
    body = build_body(text)
    if "--dry-run" in sys.argv:
        print(json.dumps(body, indent=2))
        return
    answers = ask(body)
    print(json.dumps(answers, indent=2))
    print("queue:", route(answers))
