
def apply_overrides(entity: dict, vps: float) -> tuple[float, list[str]]:
    overrides = []

    # Rule 1: Open complaint → minimum score of 90
    if entity.get("complaint_open"):
        vps = max(vps, 90.0)
        overrides.append("Open complaint requires immediate visit")

    # Rule 2: Critical pest alert → minimum score of 85
    if entity.get("pest_alert_severity") == "high":
        vps = max(vps, 85.0)
        overrides.append("Critical pest outbreak in region")

    # Rule 3: Not visited in 30+ days → minimum score of 75
    if entity.get("days_since_last_visit", 0) >= 30:
        vps = max(vps, 75.0)
        overrides.append("Overdue visit — last contact over 30 days ago")

    return vps, overrides