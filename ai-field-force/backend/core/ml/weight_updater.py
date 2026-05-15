
LEARNING_RATE = 0.05   # conservative — don't overfit to one visit

def update_weights(
    current_weights: dict,
    signals_at_visit: dict,
    outcome_rating: int,        # 1–5
    baseline_rating: float = 3.0
) -> dict:
    """
    If outcome was good (rating > 3): reinforce signals that were active
    If outcome was poor (rating < 3): slightly reduce their weight
    """
    normalized_feedback = (outcome_rating - baseline_rating) / 2.0
    # → ranges from -1.0 (terrible) to +1.0 (excellent)

    new_weights = {}
    for signal, weight in current_weights.items():
        signal_value = signals_at_visit.get(signal, 0.0)
        # Only update weights for signals that were actually active
        delta = LEARNING_RATE * normalized_feedback * signal_value
        new_weights[signal] = max(0.01, min(0.5, weight + delta))

    # Re-normalize so weights still sum to 1.0
    total = sum(new_weights.values())
    return {k: round(v / total, 4) for k, v in new_weights.items()}