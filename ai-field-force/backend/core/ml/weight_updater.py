LEARNING_RATE = 0.05   # conservative — don't overfit to one visit

SEVERITY_MAP = {
    "none":     0.0,
    "low":      0.25,
    "medium":   0.5,
    "high":     0.75,
    "critical": 1.0,
}


def _coerce_signal_value(raw) -> float:
    """Coerce a raw signal value (number, bool, string, None) to a float in [0, 1]."""
    if raw is None:
        return 0.0
    # bool MUST be checked before int/float (bool is a subclass of int in Python)
    if isinstance(raw, bool):
        return 1.0 if raw else 0.0
    if isinstance(raw, (int, float)):
        return max(0.0, min(1.0, float(raw)))
    if isinstance(raw, str):
        return SEVERITY_MAP.get(raw.lower(), 0.0)
    return 0.0


def update_weights(
    current_weights: dict,
    signals_at_visit: dict,
    outcome_rating: int,        # 1–5
    baseline_rating: float = 3.0
) -> dict:
    """
    If outcome was good (rating > 3): reinforce signals that were active.
    If outcome was poor (rating < 3): slightly reduce their weight.
    Weights are clipped to [0.01, 0.5] per signal and renormalized to sum to 1.0.
    """
    normalized_feedback = (outcome_rating - baseline_rating) / 2.0
    # → ranges from -1.0 (terrible) to +1.0 (excellent)

    new_weights = {}
    for signal, weight in current_weights.items():
        raw = signals_at_visit.get(signal, 0.0)
        signal_value = _coerce_signal_value(raw)

        delta = LEARNING_RATE * normalized_feedback * signal_value
        new_weights[signal] = max(0.01, min(0.5, weight + delta))

    # Re-normalize so weights still sum to 1.0
    total = sum(new_weights.values())
    return {k: round(v / total, 4) for k, v in new_weights.items()}