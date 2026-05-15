
def compute_vps(features: dict, weights: dict) -> float:
    """
    Visit Priority Score = weighted sum of normalized signals × 100
    Returns a float 0.0 – 100.0
    """
    raw_score = sum(
        features.get(signal, 0.0) * weight
        for signal, weight in weights.items()
    )
    return round(raw_score * 100, 2)