# Re-rank search results by whether each product matches, and test the decision model on its own

**Area:** any search where a shopper, buyer or user types requirements: retail and marketplace search, catalog search, job and property listings, help-center search. **Model:** jev-1.14 in the request (Rakuten has not named its decision model; any decision model that takes a yes/no question about a product and its photos works). **Status:** re-rank and test read-out checked offline with made-up numbers; model call not yet run by us (expected, not measured).

Full write-up: How Rakuten’s decision model and new search lifted conversion 32.3% in a test (draft, Decision Layer, Nov. 15, 2026).

## The process

Search pulls up to 50 candidates. The decision model asks of each one: does this product match what the shopper is looking for? It answers yes or no with a percentage. Results are re-sorted by that percentage, and ties keep search's order. If the decision model is down, search's order stands, as before.

Rakuten describes this shape for Ichiba search in its Q3 2026 results. In an October A/B test against its live search, the decision model together with a new search engine raised conversion 32.3% (p < 0.01). Rakuten says the test does not separate the two.

## The rules

[`rerank.py`](rerank.py):

- **`rerank`**: score up to 50 candidates and re-sort by the chance each one matches.
- **`conversion_lift`**: relative lift between two arms and a two-sided p-value (two-proportion z-test).
- **`split_credit`**: three arms instead of two (old search, new search, new search plus the decision model), so the decision model's share of the gain shows on its own.

## Try it

    python3 -m unittest -q test_rerank   # offline, made-up numbers
    python3 run.py                       # re-rank a sample search, then read a three-arm test
    python3 run.py --dry-run             # print the request for one product

## Where it breaks

- Judging 50 products per search is 50 decision-model answers per search. Price that against your traffic before you build.
- A two-arm test that changes search and adds the decision model at once cannot tell you which one earned the gain. Run the third arm.
- If paid placements sit next to re-ranked results, check what the new order does to them.
