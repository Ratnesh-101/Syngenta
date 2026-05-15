from core.deterministic.signal_normalizer import (
    normalize_days_since_visit,
    normalize_pest_severity,
    normalize_inventory,
    normalize_revenue_potential,
)

def build_feature_vector(entity: dict, signals: dict) -> dict:
    payload = signals.get(entity["id"], {})

    return {
        "pest_alert_severity":      normalize_pest_severity(
                                        payload.get("pest_alert_severity", "none")
                                    ),
        "inventory_shortage_level": normalize_inventory(
                                        payload.get("inventory_shortage_level", 0.5)
                                    ),
        "days_since_last_visit":    normalize_days_since_visit(
                                        payload.get("days_since_last_visit", 0)
                                    ),
        "weather_risk_score":       payload.get("weather_risk_score", 0.0),
        "complaint_open":           1.0 if payload.get("complaint_open") else 0.0,
        "crop_stage_sensitivity":   payload.get("crop_stage_sensitivity", 0.0),
        "revenue_potential":        normalize_revenue_potential(
                                        payload.get("revenue_potential", 0.0),
                                        payload.get("max_ltv", 1.0)
                                    ),
        "competitor_activity":      1.0 if payload.get("competitor_activity") else 0.0,
    }