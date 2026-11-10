# Is this customer profile really one person? A decision model checks every profile, an LLM takes the unsure zone

**Area:** marketing, customer data and analytics teams that join records into one profile per customer. **Model:** jev-1.13.0. **Status:** decision rules checked offline with made-up probabilities; model call not yet run by us (expected, not measured). The sample profile is made up, in the style of Hightouch's example.

Full write-up: How a marketing platform cut the cost of checking customer records 77% with a decision model (draft, Decision Layer, Nov. 10, 2026).

## The process, fully automated

The decision model checks every profile with one yes/no question: do these records describe more than one person? It returns a probability. When it is very sure either way, its answer stands. When it is in the middle, the unsure zone, the profile goes to an LLM for a second look.

In Hightouch's test on 1,000 made-up profiles, this shape gave up 0.2 points of accuracy against Claude Opus alone at 77% lower cost. On a harder set, the decision model was unsure more often, so more profiles went to the LLM; accuracy held and cost was still 45% lower.

## The question

| Question | Type | Why |
|---|---|---|
| `wrongly_joined` | Yes/no | The criteria list the errors that appear in one person's records. In Hightouch's test, that list helped every model most. |

## The rules

[`decide.py`](decide.py):

- **`check`**: above the zone, "wrongly joined" stands; below it, "one person" stands; inside it, the LLM decides. Decision model down: the LLM checks, as before.
- **`evaluate`**: on a test set with known answers, measures the share sent to the LLM, accuracy, and cost relative to the LLM alone.
- **`honest_when_wrong`**: run this before you couple. It measures what share of the decision model's own mistakes fall inside the zone. Hightouch found most of Jev's mistakes did and most of GPT-6 Luna's did not, which is why coupled Luna fell short on the harder set.

## Try it

    python3 -m unittest -q test_decide   # offline, made-up probabilities
    python3 run.py --dry-run             # print the request for the sample profile

## Where it breaks

- Hightouch picked its zone (30% to 90%) on the same profiles it scored. Pick yours on one batch and check it on another.
- An overconfident decision model gains little from an LLM partner: its wrong answers look sure, so they never reach the LLM. Check `honest_when_wrong` first.
- This checks profiles that are already built. It does not catch the opposite mistake, one person split into two profiles.
- Pin the version you tested and re-test before moving.
