def predict_defect_risk(order):
    score = 0.2

    if order.material.lower() in ["oak", "walnut"]:
        score += 0.25

    if order.size.lower() == "large":
        score += 0.25

    if order.priority.lower() == "high":
        score += 0.15

    score = min(score, 1.0)

    return {
        "risk_score": score,
        "risk_level": "high" if score >= 0.6 else "low",
        "qc_required": score >= 0.6,
    }