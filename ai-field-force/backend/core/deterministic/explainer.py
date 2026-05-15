def resolve_reason_template(signal: str, value) -> str | None:
    if signal == "pest_alert_severity":
        if value >= 0.65:
            return "Critical pest outbreak active — crop at risk"
        if value >= 0.3:
            return "Pest alert reported — monitor closely"

    elif signal == "inventory_shortage_level":
        if value >= 0.8:
            return "Inventory critically low — stockout imminent"
        if value >= 0.5:
            return "Inventory running low — reorder needed"

    elif signal == "days_since_last_visit":
        if value >= 1.0:
            return "Overdue visit — not contacted in 21+ days"
        if value >= 0.67:
            return "Visit recommended — not contacted in 14+ days"

    elif signal == "complaint_open":
        if value == 1.0:
            return "Open complaint requires immediate resolution"

    elif signal == "competitor_activity":
        if value == 1.0:
            return "Competitor activity spotted — retention risk"

    elif signal == "weather_risk_score":
        if value >= 0.7:
            return "High weather risk — crop may need urgent attention"

    elif signal == "crop_stage_sensitivity":
        if value >= 0.7:
            return "Critical crop stage — high receptivity to recommendations"

    return None


def extract_top_reasons(
    features: dict,
    weights: dict,
    overrides: list[str]
) -> list[str]:
    reasons = list(overrides)

    contributions = {
        signal: features.get(signal, 0.0) * weight
        for signal, weight in weights.items()
    }
    top_signals = sorted(contributions, key=contributions.get, reverse=True)

    for signal in top_signals:
        if len(reasons) >= 3:
            break
        reason = resolve_reason_template(signal, features.get(signal, 0.0))
        if reason:
            reasons.append(reason)

    return reasons