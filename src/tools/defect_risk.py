def predict_defect_risk(order):
    score = 0.2
    reasons = []

    if order.material.lower() in ["oak", "walnut"]:
        score += 0.25
        reasons.append("material is prone to defects")

    if order.size.lower() == "large":
        score += 0.25
        reasons.append("large size increases complexity")

    if order.priority.lower() == "high":
        score += 0.15
        reasons.append("high priority may increase rush-related defects")

    score = min(score, 1.0)

    risk_level = "high" if score >= 0.6 else "low"
    qc_required = score >= 0.6

    reason = (
        f"Risk score {score:.2f} due to: " + ", ".join(reasons)
        if reasons
        else "Low complexity order with minimal risk factors."
    )

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "qc_required": qc_required,
        "reason": reason,
    }