"""One yes/no question per article, asked of its headline and summary only, the shape Currents used.
The question says what to drop. This wording is an example; write your own for your topic."""

MODEL = "jev-1.13.0"  # or any decision model that takes this request format; re-test before moving versions

QUESTION = (
    "Is this article substantive reporting, analysis or a technical update directly about {topic}? "
    "Answer no to generic watchlists, news about other companies, and law-firm ads seeking shareholders."
)


def build_body(article: dict, topic: str) -> dict:
    title = article.get("title", "").strip()
    summary = article.get("summary", "").strip()[:800]  # headline and summary only, never the full text
    return {
        "model": MODEL,
        "state": f"Title: {title}\nSummary: {summary}",
        "questions": {
            "on_topic": {
                "type": "noul",
                "instructions": QUESTION.format(topic=topic),
                "criteria": {"true": "The article is on topic and worth reading.", "false": "The article is noise for this topic."},
            }
        },
    }
