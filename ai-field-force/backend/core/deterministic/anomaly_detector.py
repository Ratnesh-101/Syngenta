ANOMALY_RULES = [
    {
        "name":     "stock_critically_low",
        "check":    lambda e: e.get("inventory_pct", 1.0) < 0.10,
        "severity": "critical",
        "message":  "Stock below 10% — risk of stockout within 3 days"
    },
    {
        "name":     "visit_gap_exceeded",
        "check":    lambda e: e.get("days_since_last_visit", 0) > 21,
        "severity": "high",
        "message":  "No visit in 3+ weeks during active crop season"
    },
    {
        "name":     "competitor_spotted",
        "check":    lambda e: e.get("competitor_activity") == True,
        "severity": "medium",
        "message":  "Competitor activity reported in this area"
    },
    {
        "name":     "complaint_unresolved",
        "check":    lambda e: e.get("complaint_open") == True,
        "severity": "high",
        "message":  "Open complaint requires immediate resolution"
    },
]

def run_anomaly_checks(entity: dict) -> list[dict]:
    triggered = []
    for rule in ANOMALY_RULES:
        try:
            if rule["check"](entity):
                triggered.append({
                    "type":     rule["name"],
                    "severity": rule["severity"],
                    "message":  rule["message"]
                })
        except Exception:
            continue
    return triggered