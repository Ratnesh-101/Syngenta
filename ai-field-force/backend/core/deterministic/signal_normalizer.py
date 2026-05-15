def normalize_days_since_visit(days: int) -> float:
    if days <= 0:
        return 0.0
    return min(days / 21.0, 1.0)

def normalize_pest_severity(level: str) -> float:
    mapping = {"none": 0.0, "low": 0.3, "medium": 0.65, "high": 1.0}
    return mapping.get(level, 0.0)

def normalize_inventory(stock_pct: float) -> float:
    return max(0.0, 1.0 - stock_pct)

def normalize_revenue_potential(lifetime_value: float, max_ltv: float) -> float:
    return min(lifetime_value / max_ltv, 1.0) if max_ltv > 0 else 0.0