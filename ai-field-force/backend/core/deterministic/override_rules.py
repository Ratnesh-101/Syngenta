def apply_overrides(entity: dict, vps: float) -> tuple[float, list[str]]:
    overrides = []

    if entity.get("complaint_open"):
        vps = max(vps, 90.0)
        overrides.append("Open complaint requires immediate visit")

    if entity.get("pest_alert_severity") == "high":
        vps = max(vps, 85.0)
        overrides.append("Critical pest outbreak in region")

    if entity.get("days_since_last_visit", 0) >= 30:
        vps = max(vps, 75.0)
        overrides.append("Overdue visit — last contact over 30 days ago")

    return vps, overrides