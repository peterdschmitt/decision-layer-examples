"""Fast track routing. Thresholds are placeholders; the fast-track bar is high on purpose."""

PLANTED_BAR = 0.3
GLASS_BAR = 0.9
INJURY_CEILING = 0.05


def route(answers: dict, coverage_ok: bool = True) -> str:
    """coverage_ok must come from your policy system, never from the claimant's text."""
    glass = answers["glass_only"]["noul"]
    injury = answers["injury_mentioned"]["noul"]
    planted = answers["addressed_to_insurer"]["noul"]

    if planted > PLANTED_BAR:
        return "adjuster_review"   # someone reads it and checks any "approval"
    if not coverage_ok:
        return "adjuster_review"
    if glass > GLASS_BAR and injury < INJURY_CEILING:
        return "glass_fast_track"  # a person still approves the payment
    return "adjuster_queue"        # anything close goes to a person
