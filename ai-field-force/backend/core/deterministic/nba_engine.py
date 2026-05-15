NBA_RULES = [
    {
        "condition": lambda e: e.get("complaint_open") == True,
        "action":    "complaint_resolution",
        "detail":    "Resolve open complaint. Acknowledge the issue and bring replacement if applicable.",
        "priority":  1
    },
    {
        "condition": lambda e: e.get("pest_alert_severity") in ["medium", "high"],
        "action":    "pest_advisory",
        "detail":    "Discuss active pest alert. Recommend appropriate Syngenta crop protection product.",
        "priority":  2
    },
    {
        "condition": lambda e: e.get("inventory_shortage_level", 0) > 0.6,
        "action":    "inventory_replenishment",
        "detail":    "Inventory critically low. Facilitate reorder and check distributor pipeline.",
        "priority":  3
    },
    {
        "condition": lambda e: e.get("crop_stage") == "pre_sowing",
        "action":    "seed_recommendation",
        "detail":    "Pre-sowing window open. Present seed portfolio for upcoming season.",
        "priority":  4
    },
    {
        "condition": lambda e: e.get("days_since_last_visit", 0) > 20,
        "action":    "relationship_maintenance",
        "detail":    "General check-in. Capture field conditions and any competitor activity.",
        "priority":  5
    },
    {
        "condition": lambda e: e.get("competitor_activity") == True,
        "action":    "competitor_retention",
        "detail":    "Competitor activity spotted. Reinforce relationship and highlight Syngenta advantages.",
        "priority":  6
    },
]

def get_next_best_actions(entity_context: dict) -> list[dict]:
    triggered = []
    for rule in NBA_RULES:
        try:
            if rule["condition"](entity_context):
                triggered.append({
                    "action": rule["action"],
                    "detail": rule["detail"],
                })
        except Exception:
            continue
    triggered_sorted = sorted(
        triggered,
        key=lambda r: next(
            x["priority"] for x in NBA_RULES if x["action"] == r["action"]
        )
    )
    return triggered_sorted[:3]