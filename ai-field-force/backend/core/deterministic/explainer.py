REASON_TEMPLATES = {
    "pest_alert_severity": {
        "high":   "Critical pest outbreak active in {region}",
        "medium": "Pest alert reported — crop at risk",
    },
    "inventory_shortage_level": {
        lambda v: v > 0.8: "Inventory critically low — stockout imminent",
        lambda v: v > 0.5: "Inventory running low — reorder needed",
    },
    "days_since_last_visit": {
        lambda v: v > 21: "Overdue visit — {days} days since last contact",
        lambda v: v > 14: "Visit recommended — {days} days since last contact",
    },
    "complaint_open": {
        True: "Open complaint requires immediate resolution"
    },
    "competitor_activity": {
        True: "Competitor activity spotted — retention risk"
    },
}

def extract_top_reasons(
    features: dict,
    weights: dict,
    overrides: list[str]
) -> list[str]:
    # Start with hard override reasons
    reasons = list(overrides)

    # Add top weighted signal explanations
    contributions = {
        signal: features.get(signal, 0.0) * weight
        for signal, weight in weights.items()
    }
    top_signals = sorted(contributions, key=contributions.get, reverse=True)

    for signal in top_signals:
        if len(reasons) >= 3:
            break
        reason = resolve_reason_template(signal, features.get(signal))
        if reason:
            reasons.append(reason)

    return reasons