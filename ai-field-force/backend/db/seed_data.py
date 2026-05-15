# db/seed_data.py

import uuid, random
from datetime import datetime, timedelta
from db.session import SessionLocal, engine, Base
from models.db.farmers import FarmerRetailer
from models.db.signal import Signal
from models.db import outcome, visit  # ensure all tables are created

REGIONS   = ["Surat", "Vadodara", "Rajkot", "Anand"]
CROPS     = ["cotton", "groundnut", "wheat", "sugarcane"]
PEST_LVLS = ["none", "low", "medium", "high"]
TYPES     = ["farmer", "retailer", "distributor"]

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data
    db.query(Signal).delete()
    db.query(FarmerRetailer).delete()
    db.commit()

    # Seed farmers
    entities = []
    for i in range(20):
        entity = FarmerRetailer(
            id              = f"F-{1000 + i}",
            name            = f"Farmer {i}",
            type            = random.choice(TYPES),
            lat             = round(random.uniform(21.0, 24.0), 4),
            lng             = round(random.uniform(70.0, 74.0), 4),
            region          = random.choice(REGIONS),
            rep_id          = "R-01",
            last_visited_at = datetime.now() - timedelta(days=random.randint(0, 30)),
        )
        db.add(entity)
        entities.append(entity)

    db.commit()

    # Seed signals
    for entity in entities:
        signal = Signal(
            id          = str(uuid.uuid4()),
            entity_id   = entity.id,
            signal_type = random.choice(["pest", "weather", "inventory"]),
            severity    = random.choice(PEST_LVLS),
            payload     = {
                "pest_alert_severity":      random.choice(PEST_LVLS),
                "weather_risk_score":       round(random.uniform(0, 1), 2),
                "inventory_shortage_level": round(random.uniform(0, 1), 2),
                "inventory_pct":            round(random.uniform(0, 1), 2),
                "crop_stage":               random.choice(CROPS),
                "crop_stage_sensitivity":   round(random.uniform(0, 1), 2),
                "competitor_activity":      random.choice([True, False]),
                "complaint_open":           random.choice([True, False]),
                "revenue_potential":        round(random.uniform(0, 100000), 2),
                "max_ltv":                  100000.0,
                "days_since_last_visit":    random.randint(0, 30),
            },
            created_at  = datetime.now(),
        )
        db.add(signal)

    db.commit()
    db.close()
    print(f"✓ Seeded 20 farmers and 20 signals into DB")

if __name__ == "__main__":
    seed()