NBA_RULES = [
    {
        "condition": lambda e: e["complaint_open"],
        "action":    "complaint_resolution",
        "template":  "Resolve open complaint about {complaint_topic}. Bring replacement if applicable.",
        "priority":  1
    },
    {
        "condition": lambda e: e["pest_alert_severity"] in ["medium","high"],
        "action":    "pest_advisory",
        "template":  "Recommend {product} for {pest_type} control. Demonstrate application method.",
        "priority":  2
    },
    {
        "condition": lambda e: e["inventory_shortage_level"] > 0.6,
        "action":    "inventory_replenishment",
        "template":  "Facilitate reorder of {low_stock_products}. Check distributor pipeline.",
        "priority":  3
    },
    {
        "condition": lambda e: e["crop_stage"] == "pre_sowing",
        "action":    "seed_recommendation",
        "template":  "Present seed portfolio for upcoming {crop_type} season.",
        "priority":  4
    },
    {
        "condition": lambda e: e["days_since_last_visit"] > 20,
        "action":    "relationship_maintenance",
        "template":  "General check-in. Capture latest field conditions and competitor intel.",
        "priority":  5
    },
]

def get_next_best_actions(entity_context: dict) -> list[dict]:
    triggered = [
        rule for rule in NBA_RULES
        if rule["condition"](entity_context)
    ]
    triggered.sort(key=lambda r: r["priority"])
    return triggered[:3]  # top 3 actions max