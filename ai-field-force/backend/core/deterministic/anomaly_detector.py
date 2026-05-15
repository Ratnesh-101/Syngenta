ANOMALY_RULES = [
    {
        "name":      "stock_critically_low",
        "check":     lambda e: e["inventory_pct"] < 0.10,
        "severity":  "critical",
        "message":   "Stock below 10% — risk of stockout within 3 days"
    },
    {
        "name":      "visit_gap_exceeded",
        "check":     lambda e: e["days_since_visit"] > 21,
        "severity":  "high",
        "message":   "No visit in 3+ weeks during active crop season"
    },
    {
        "name":      "sudden_purchase_drop",
        "check":     lambda e: e["purchase_trend_7d"] < -0.4,
        "severity":  "high",
        "message":   "Purchase volume dropped 40%+ vs last week"
    },
    {
        "name":      "competitor_spotted",
        "check":     lambda e: e["competitor_activity"] == True,
        "severity":  "medium",
        "message":   "Competitor activity reported in this area"
    },
]