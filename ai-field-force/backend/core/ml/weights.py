SIGNAL_WEIGHTS = {
    "pest_alert_severity":      0.25,
    "inventory_shortage_level": 0.20,
    "days_since_last_visit":    0.18,
    "weather_risk_score":       0.12,
    "complaint_open":           0.10,
    "crop_stage_sensitivity":   0.08,
    "revenue_potential":        0.05,
    "competitor_activity":      0.02,
}

assert round(sum(SIGNAL_WEIGHTS.values()), 10) == 1.0