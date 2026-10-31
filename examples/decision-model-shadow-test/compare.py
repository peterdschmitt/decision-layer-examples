"""Compare candidate decision models on logged shadow answers, offline.

    python3 compare.py               # uses sample_cases.json (made-up numbers)
    python3 compare.py my_cases.json  # your own logged probabilities and labels
"""

import json
import os
import sys

from route import pick_bar, shadow_test

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_cases.json")
data = json.load(open(path))
labels = data["labels"]
for name, probs in data["candidates"].items():
    for bar in (0.8, 0.9, 0.95):
        print(name, bar, shadow_test(probs, labels, bar))
    print(name, "best bar:", pick_bar(probs, labels)[0])
