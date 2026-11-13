"""Search shortlists pages, the decision model judges each one, and the LLM writes from the best.
If no page clears the bar, the answer is "not found" and the LLM is never asked."""

NOT_FOUND = "not found"


def answer_question(question, shortlist, judge, llm_answer, bar=0.30, top_k=6):
    """judge(page, question) -> chance the page answers the question.
    If the decision model is down, the LLM reads search's pages, as before."""
    try:
        scored = sorted(((judge(page, question), page) for page in shortlist), key=lambda s: s[0], reverse=True)
    except Exception:
        return llm_answer(question, shortlist[:top_k]), "llm"
    if not scored or scored[0][0] < bar:
        return NOT_FOUND, "decision_model"
    best = [page for _, page in scored[:top_k]]
    return llm_answer(question, best), "llm"


def evaluate(cases, bar=0.30):
    """cases: [{"question", "answerable": bool, "answer_pages": [...], "scores": {page: p}}]
    Returns how many answerable questions got an answer page first, how many absent questions
    were caught, and how many answerable ones were wrongly blanked."""
    first_right = caught = wrongly_blank = answerable = absent = 0
    for c in cases:
        ranked = sorted(c["scores"].items(), key=lambda kv: kv[1], reverse=True)
        best_p = ranked[0][1] if ranked else 0.0
        if c["answerable"]:
            answerable += 1
            if ranked and ranked[0][0] in c["answer_pages"]:
                first_right += 1
            if best_p < bar:
                wrongly_blank += 1
        else:
            absent += 1
            if best_p < bar:
                caught += 1
    return {
        "answerable": answerable,
        "answer_page_first": first_right,
        "wrongly_not_found": wrongly_blank,
        "absent": absent,
        "absent_caught": caught,
    }


def pick_bar(cases, bars=(0.1, 0.2, 0.3, 0.4, 0.5)):
    """The highest bar that blanks no answerable question. Pick it on one batch, check it on another."""
    ok = [b for b in bars if evaluate(cases, b)["wrongly_not_found"] == 0]
    return max(ok) if ok else min(bars)
