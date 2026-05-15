# tests/test_scorer.py

from core.ml.priority_scorer      import compute_vps
from core.ml.weights              import SIGNAL_WEIGHTS
from core.deterministic.override_rules import apply_overrides

def test_basic_scoring():
    features = {
        "pest_alert_severity":      0.65,
        "inventory_shortage_level": 0.80,
        "days_since_last_visit":    0.81,
        "weather_risk_score":       0.71,
        "crop_stage_sensitivity":   0.85,
        "revenue_potential":        0.60,
        "complaint_open":           0.0,
        "competitor_activity":      1.0,
    }
    vps = compute_vps(features, SIGNAL_WEIGHTS)
    assert 0 <= vps <= 100
    print(f"VPS: {vps}")

def test_override_bumps_score():
    entity  = {"complaint_open": True, "pest_alert_severity": "low"}
    vps, reasons = apply_overrides(entity, 40.0)
    assert vps >= 90.0
    assert len(reasons) > 0

if __name__ == "__main__":
    test_basic_scoring()
    test_override_bumps_score()
    print("All tests passed.")