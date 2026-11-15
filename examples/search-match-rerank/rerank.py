"""Search finds up to 50 candidates. The decision model scores each one: does it match the shopper's
search? Results are re-sorted by that score. Ties keep search's order. If the decision model is down,
search's order stands, as before."""

import math


def rerank(search, candidates, judge, limit=50):
    """judge(search, product) -> chance the product matches. Returns (products, who_ranked)."""
    pool = candidates[:limit]
    try:
        scored = [(judge(search, p), i, p) for i, p in enumerate(pool)]
    except Exception:
        return pool, "search"
    scored.sort(key=lambda s: (-s[0], s[1]))
    return [p for _, _, p in scored], "decision_model"


def conversion_lift(control, treatment):
    """control/treatment: (orders, visits). Returns relative lift and a two-sided p-value from a
    two-proportion z-test. A small p-value means the gap is unlikely to be luck."""
    (c_o, c_n), (t_o, t_n) = control, treatment
    p_c, p_t = c_o / c_n, t_o / t_n
    pooled = (c_o + t_o) / (c_n + t_n)
    se = math.sqrt(pooled * (1 - pooled) * (1 / c_n + 1 / t_n))
    z = (p_t - p_c) / se if se else 0.0
    p_value = math.erfc(abs(z) / math.sqrt(2))
    return {"lift": p_t / p_c - 1, "p_value": p_value}


def split_credit(old_search, new_search, new_search_plus_model):
    """Three arms instead of two, so the decision model's share of the gain can be seen on its own.
    Each arm is (orders, visits)."""
    return {
        "new_search_alone": conversion_lift(old_search, new_search),
        "decision_model_on_top": conversion_lift(new_search, new_search_plus_model),
        "combined": conversion_lift(old_search, new_search_plus_model),
    }
