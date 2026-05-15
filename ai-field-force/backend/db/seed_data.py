# db/seed_data.py
import csv, json, random, uuid
from collections import defaultdict
from datetime import datetime, date
from db.session import SessionLocal, engine, Base
from models.db.farmers import FarmerRetailer
from models.db.signal import Signal
from models.db import outcome, visit

TARGET_REP = "REP_0338"
TODAY = date(2026, 5, 15)

PEST_SEVERITY_MAP = {
    "wheat":    "medium",
    "mustard":  "high",
    "chickpea": "low",
    "barley":   "low",
    "lentil":   "none",
    "safflower":"medium",
}

CROP_SENSITIVITY_MAP = {
    "wheat":    0.7,
    "mustard":  0.85,
    "chickpea": 0.5,
    "barley":   0.45,
    "lentil":   0.4,
    "safflower":0.6,
}

def load_rep_data():
    tehsil_to_rep = {}
    rep_info = {}
    with open("db/data/reps_territory.csv") as f:
        for r in csv.DictReader(f):
            rep_info[r["rep_id"]] = r
            for t in json.loads(r["tehsil_list"]):
                tehsil_to_rep[t] = r["rep_id"]
    return rep_info, tehsil_to_rep

def load_last_visits():
    last_visit = defaultdict(lambda: date(2025, 10, 1))
    with open("db/data/retailer_visit_log.csv") as f:
        for r in csv.DictReader(f):
            d = datetime.strptime(r["visit_date"], "%Y-%m-%d").date()
            if d > last_visit[r["rep_id"]]:
                last_visit[r["rep_id"]] = d
    return last_visit

def load_growers(rep_tehsils):
    growers = []
    with open("db/data/growers.csv") as f:
        for r in csv.DictReader(f):
            if r["tehsil"] in rep_tehsils:
                growers.append(r)
    return growers

def load_tehsil_inventory(rep_tehsils):
    # Step 1: tehsil -> retailer_ids
    tehsil_retailers = defaultdict(list)
    with open("db/data/retailers.csv") as f:
        for r in csv.DictReader(f):
            if r["tehsil"] in rep_tehsils:
                tehsil_retailers[r["tehsil"]].append(r["retailer_id"])

    rep_retailer_set = set(
        rid for retailers in tehsil_retailers.values() for rid in retailers
    )

    # Step 2: load inventory for these retailers
    retailer_inventory = defaultdict(list)
    with open("db/data/retailer_inventory_weekly.csv") as f:
        for r in csv.DictReader(f):
            if r["retailer_id"] in rep_retailer_set:
                retailer_inventory[r["retailer_id"]].append(r)

    if not retailer_inventory:
        return {}

    # Step 3: latest week
    latest_week = max(
        r["week_end_date"]
        for rows in retailer_inventory.values()
        for r in rows
    )

    # Step 4: compute per-tehsil inventory_pct
    tehsil_inv = {}
    for tehsil, retailers in tehsil_retailers.items():
        all_qtys = []
        for rid in retailers:
            latest = [r for r in retailer_inventory[rid] if r["week_end_date"] == latest_week]
            for r in latest:
                all_qtys.append(int(r["sku_qty"]))
        if all_qtys:
            oos = sum(1 for q in all_qtys if q == 0)
            pct = round(1.0 - (oos / len(all_qtys)), 2)
            tehsil_inv[tehsil] = {
                "inventory_pct": pct,
                "inventory_shortage_level": round(1.0 - pct, 2)
            }

    return tehsil_inv

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    db.query(Signal).delete()
    db.query(FarmerRetailer).delete()
    db.commit()

    rep_info, tehsil_to_rep = load_rep_data()
    last_visits = load_last_visits()

    rep_tehsils = set(json.loads(rep_info[TARGET_REP]["tehsil_list"]))
    rep_district = rep_info[TARGET_REP]["district"]
    rep_state    = rep_info[TARGET_REP]["state"]
    days_since   = (TODAY - last_visits[TARGET_REP]).days

    growers      = load_growers(rep_tehsils)
    tehsil_inv   = load_tehsil_inventory(rep_tehsils)

    print(f"Seeding {len(growers)} growers for {TARGET_REP} ({rep_district}, {rep_state})")
    print(f"Days since last visit: {days_since}")
    print(f"Tehsils with real inventory: {len(tehsil_inv)}")

    entities = []
    for g in growers:
        entity = FarmerRetailer(
            id=g["grower_id"],
            name=f"Grower {g['grower_id'][-5:]}",
            type="farmer",
            lat=round(random.uniform(27.0, 29.5), 4),
            lng=round(random.uniform(72.0, 74.5), 4),
            region=f"{g['district']}, {g['state']}",
            rep_id=TARGET_REP,
            last_visited_at=datetime.combine(
                last_visits[TARGET_REP], datetime.min.time()
            ),
        )
        db.add(entity)
        entities.append((entity, g))

    db.commit()

    for entity, g in entities:
        # Crop calendar
        try:
            cal   = json.loads(g["grower_crop_calendar"])
            crop  = cal.get("crop", "wheat")
            stages = [s["stage"] for s in cal.get("stages", [])]
            crop_stage = stages[-1] if stages else "unknown"
        except Exception:
            crop = "wheat"
            crop_stage = "unknown"

        pest_severity    = PEST_SEVERITY_MAP.get(crop, "low")
        crop_sensitivity = CROP_SENSITIVITY_MAP.get(crop, 0.5)

        # Real inventory from tehsil
        inv = tehsil_inv.get(g["tehsil"], {})
        inventory_pct      = inv.get("inventory_pct", 0.5)
        inventory_shortage = inv.get("inventory_shortage_level", 0.5)

        # Revenue from farm size
        farm_size = float(g.get("grower_farm_size") or 1.0)
        revenue_potential = min(100000.0, farm_size * 12000)

        # Engagement signals
        product_scanned    = g.get("product_scan", "false").lower() == "true"
        campaign_attended  = g.get("offline_campaign_attended", "false").lower() == "true"
        competitor_activity = not product_scanned and not campaign_attended

        signal = Signal(
            id=str(uuid.uuid4()),
            entity_id=entity.id,
            signal_type="composite",
            severity=pest_severity,
            payload={
                "pest_alert_severity":      pest_severity,
                "weather_risk_score":       round(random.uniform(0.3, 0.9), 2),
                "inventory_shortage_level": inventory_shortage,
                "inventory_pct":            inventory_pct,
                "crop_stage":              crop,
                "crop_stage_sensitivity":  crop_sensitivity,
                "competitor_activity":     competitor_activity,
                "complaint_open":          not campaign_attended and random.random() < 0.3,
                "revenue_potential":       round(revenue_potential, 2),
                "max_ltv":                 100000.0,
                "days_since_last_visit":   days_since,
            },
            created_at=datetime.utcnow(),
        )
        db.add(signal)

    db.commit()
    db.close()
    print(f"✓ Seeded {len(entities)} growers and {len(entities)} signals for {TARGET_REP}")

if __name__ == "__main__":
    seed()