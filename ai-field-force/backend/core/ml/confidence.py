
def compute_confidence(features: dict, signals_meta: dict) -> dict:
    """
    Confidence is reduced by:
    - Missing signals (partial data)
    - Stale signals (old data)
    - Low visit history (new entity)
    """
    total_signals   = len(features)
    present_signals = sum(1 for v in features.values() if v is not None)
    coverage_score  = present_signals / total_signals

    # Staleness: average age of signals in hours
    ages = [signals_meta.get(k, {}).get("age_hours", 48) for k in features]
    avg_age_hours   = sum(ages) / len(ages) if ages else 48
    freshness_score = max(0.0, 1.0 - (avg_age_hours / 72))  # degrades over 72h

    # History depth
    visit_count       = signals_meta.get("visit_history_count", 0)
    history_score     = min(visit_count / 10.0, 1.0)  # saturates at 10 visits

    confidence = (
        coverage_score  * 0.4 +
        freshness_score * 0.35 +
        history_score   * 0.25
    )

    return {
        "score":        round(confidence, 2),
        "label":        _confidence_label(confidence),
        "missing":      [k for k, v in features.items() if v is None],
        "stale":        [k for k, v in signals_meta.items()
                         if v.get("age_hours", 0) > 24],
    }

def _confidence_label(score: float) -> str:
    if score >= 0.80: return "high"
    if score >= 0.55: return "medium"
    return "low"