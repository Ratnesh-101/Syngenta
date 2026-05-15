# db/seed_data.py

import uuid, random
from datetime import datetime, timedelta

REGIONS   = ["Surat", "Vadodara", "Rajkot", "Anand"]
CROPS     = ["cotton", "groundnut", "wheat", "sugarcane"]
PEST_LVLS = ["none", "low", "medium", "high"]
TYPES     = ["farmer", "retailer", "distributor"]

def generate_entities(n: int = 20) -> list[dict]:
    return [
        {
            "id":               f"F-{1000 + i}",
            "name":             f"Farmer {i}",
            "type":             random.choice(TYPES),
            "lat":              round(random.uniform(21.0, 24.0), 4),
            "lng":              round(random.uniform(70.0, 74.0), 4),
            "region":           random.choice(REGIONS),
            "rep_id":           "R-01",
            "last_visited_at":  datetime.now() - timedelta(
                                    days=random.randint(0, 30)
                                ),
        }
        for i in range(n)
    ]

def generate_signals(entity_ids: list) -> list[dict]:
    return [
        {
            "id":           str(uuid.uuid4()),
            "entity_id":    eid,
            "signal_type":  random.choice(["pest", "weather", "inventory"]),
            "severity":     random.choice(PEST_LVLS),
            "payload": {
                "pest_alert_severity":      random.choice(PEST_LVLS),
                "weather_risk_score":       round(random.uniform(0, 1), 2),
                "inventory_shortage_level": round(random.uniform(0, 1), 2),
                "crop_stage":               random.choice(CROPS),
                "competitor_activity":      random.choice([True, False]),
            },
            "created_at":   datetime.now(),
        }
        for eid in entity_ids
    ]

if __name__ == "__main__":
    entities = generate_entities(20)
    signals  = generate_signals([e["id"] for e in entities])
    # write to DB here
    print(f"Seeded {len(entities)} entities and {len(signals)} signals")