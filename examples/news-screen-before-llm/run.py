"""Screen the sample articles and show whether screening pays at two LLM prices.

    python3 run.py             # offline: uses the made-up probabilities in sample_input.json
    python3 run.py --dry-run   # print the request for the first article, send nothing
    python3 run.py --live      # ask the decision model for each article; needs TYPESAFE_API_KEY
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from request import build_body  # noqa: E402
from screen import bar_report, break_even_llm_price, net_saving, screen  # noqa: E402

if __name__ == "__main__":
    sample = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))
    articles, topic = sample["articles"], sample["topic"]
    if "--dry-run" in sys.argv:
        print(json.dumps(build_body(articles[0], topic), indent=2))
        sys.exit(0)
    if "--live" in sys.argv:
        from common.jev_client import ask  # noqa: E402

        def decide(a):
            return ask(build_body(a, topic))["on_topic"]["noul"]
    else:
        def decide(a):
            return a["p"]

    kept, dropped = screen(articles, decide, bar=0.70)
    print(f"kept {len(kept)} of {len(articles)}; dropped: {[a['title'] for a in dropped]}")
    for name, price in sample["llm_prices"].items():
        net = net_saving(dropped, articles, price, sample["screen_price"])
        print(f"{name} LLM: net {'saving' if net > 0 else 'LOSS'} of {abs(net):.1f} units")
    print("break-even LLM price:", round(break_even_llm_price(dropped, articles, sample["screen_price"]), 3))
    print("share dropped by bar:", bar_report(articles, [decide(a) for a in articles]))
