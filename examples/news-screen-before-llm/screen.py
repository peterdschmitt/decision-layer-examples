"""Screen every article with a decision model, then let the LLM write from what is left.
A second set of rules checks whether screening pays at a given LLM price."""


def screen(articles, decide, bar=0.70):
    """Return (kept, dropped). decide(article) -> chance the article is on topic.
    If the decision model is down, the article is kept, as before."""
    kept, dropped = [], []
    for a in articles:
        try:
            p = decide(a)
        except Exception:
            p = 1.0
        (kept if p >= bar else dropped).append(a)
    return kept, dropped


def screen_then_brief(articles, decide, brief, bar=0.70):
    kept, _ = screen(articles, decide, bar)
    share_kept = len(kept) / len(articles) if articles else 1.0
    return brief(kept), share_kept


def words(articles):
    """What the LLM reads per article. Use the provider's own token counts if you have them."""
    return sum(a.get("length", 0) for a in articles)


def net_saving(dropped, all_articles, llm_price, screen_price):
    """Money saved on the LLM's reading minus money spent screening.
    llm_price: what the LLM charges per unit of length it reads.
    screen_price: what the decision model charges per unit of length it screens (headline and summary)."""
    saved = words(dropped) * llm_price
    spent = sum(a.get("screen_length", 0) for a in all_articles) * screen_price
    return saved - spent


def screening_pays(dropped, all_articles, llm_price, screen_price):
    return net_saving(dropped, all_articles, llm_price, screen_price) > 0


def break_even_llm_price(dropped, all_articles, screen_price):
    """The lowest LLM price at which screening stops losing money."""
    dropped_len = words(dropped)
    if dropped_len == 0:
        return float("inf")
    return sum(a.get("screen_length", 0) for a in all_articles) * screen_price / dropped_len


def bar_report(articles, probs, bars=(0.5, 0.7, 0.85, 0.95)):
    """Share of articles dropped at each bar. probs: one probability per article, same order.
    Check quality at the bar you choose; dropping more is not the same as saving well."""
    out = {}
    for b in bars:
        dropped = sum(1 for p in probs if p < b)
        out[b] = dropped / len(articles) if articles else 0.0
    return out
