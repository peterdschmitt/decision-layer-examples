"""Turn the answers into a queue plus notes for the account manager. Thresholds are placeholders."""

HAZARD_BAR = 0.3
LOSS_BAR = 0.3
CLASS_CONFIDENCE = 0.6
DETAIL_FLOOR = 1.0


def route(answers: dict) -> tuple[str, list[str]]:
    cls = answers["business_class"]
    hazard = answers["hazardous_work"]["noul"]
    loss = answers["prior_loss_mentioned"]["noul"]
    detail = answers["detail"]["score"]  # 0 to 2
    confidence = cls.get("confidence") or 0.0  # null means not sure

    flags = []
    if hazard > HAZARD_BAR:
        flags.append("hazardous operations mentioned")
    if loss > LOSS_BAR:
        flags.append("prior loss mentioned: request loss runs")

    if cls["choice"] == "other_or_unclear" or confidence < CLASS_CONFIDENCE:
        queue = "account_manager_review"
    elif detail < DETAIL_FLOOR:
        queue = "call_back_for_details"
    else:
        queue = f"market_to_{cls['choice']}_carriers"
    return queue, flags
