
import numpy as np

def detect_statistical_anomaly(
    entity_id: str,
    metric: str,
    current_value: float,
    historical_values: list[float]
) -> dict | None:

    if len(historical_values) < 5:
        return None  # not enough history

    mean = np.mean(historical_values)
    std  = np.std(historical_values)

    if std == 0:
        return None

    z_score = (current_value - mean) / std

    if abs(z_score) > 2.0:   # 2 standard deviations
        return {
            "type":      "statistical_deviation",
            "metric":    metric,
            "z_score":   round(z_score, 2),
            "severity":  "high" if abs(z_score) > 3 else "medium",
            "message":   f"{metric} is {abs(z_score):.1f} std deviations from normal"
        }
    return None