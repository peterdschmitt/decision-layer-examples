"""Turn the four answers into a queue. Thresholds are placeholders."""

INJURY_BAR = 0.2        # low on purpose: when in doubt, a person looks
TYPE_CONFIDENCE = 0.6
LOCATION_BAR = 0.5
GLASS_CONFIDENCE = 0.85
GLASS_COMPLEXITY = 0.5


def route(answers: dict) -> str:
    loss = answers["loss_type"]
    injury = answers["injury_mentioned"]["noul"]
    located = answers["location_given"]["noul"]
    complexity = answers["complexity"]["score"]  # 0 to 2
    # The API can return a null confidence; treat that as not sure.
    confidence = loss.get("confidence") or 0.0

    if injury > INJURY_BAR:
        return "injury_review"
    if confidence < TYPE_CONFIDENCE or loss["choice"] == "other_or_unclear":
        return "manual_triage"
    if located < LOCATION_BAR:
        return "needs_info"
    if (loss["choice"] == "auto_glass" and complexity < GLASS_COMPLEXITY
            and confidence > GLASS_CONFIDENCE):
        return "fast_track_glass"  # a person still approves payment
    return f"standard_{loss['choice']}"
