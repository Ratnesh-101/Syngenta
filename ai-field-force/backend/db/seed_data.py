# db/seed_data.py
import csv, json, random, uuid
from collections import defaultdict
from datetime import datetime, date
from db.session import SessionLocal, engine, Base
from models.db.farmers import FarmerRetailer
from models.db.signal import Signal
from models.db import outcome, visit
from core.integrations.weather import fetch_weather_summary

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

# Fallback if Open-Meteo is unreachable at seed time
WEATHER_FALLBACK_SCORE = 0.5


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
    tehsil_retailers = defaultdict(list)
    with open("db/data/retailers.csv") as f:
        for r in csv.DictReader(f):
            if r["tehsil"] in rep_tehsils:
                tehsil_retailers[r["tehsil"]].append(r["retailer_id"])

    rep_retailer_set = set(
        rid for retailers in tehsil_retailers.values() for rid in retailers
    )

    retailer_inventory = defaultdict(list)
    with open("db/data/retailer_inventory_weekly.csv") as f:
        for r in csv.DictReader(f):
            if r["retailer_id"] in rep_retailer_set:
                retailer_inventory[r["retailer_id"]].append(r)

    if not retailer_inventory:
        return {}

    latest_week = max(
        r["week_end_date"]
        for rows in retailer_inventory.values()
        for r in rows
    )

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


def fetch_territory_weather():
    """One real weather call for the whole Bikaner territory. All growers
    in the territory share this value because they share the weather.
    """
    summary = fetch_weather_summary()
    if summary is None:
        print(f"  ⚠ Open-Meteo unreachable — falling back to {WEATHER_FALLBACK_SCORE}")
        return WEATHER_FALLBACK_SCORE, None
    print(
        f"  ✓ Live weather for Bikaner (Open-Meteo): score={summary['score']} "
        f"[precip={summary['components']['total_precipitation_mm_7d']}mm/7d, "
        f"hot_days≥38C={summary['components']['hot_days_above_38c_7d']}, "
        f"peak_wind={summary['components']['peak_wind_kmh_7d']}km/h]"
    )
    return summary["score"], summary


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

    # Fetch weather ONCE for the whole territory — all growers share it
    weather_risk_score, weather_summary = fetch_territory_weather()

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

        inv = tehsil_inv.get(g["tehsil"], {})
        inventory_pct      = inv.get("inventory_pct", 0.5)
        inventory_shortage = inv.get("inventory_shortage_level", 0.5)

        farm_size = float(g.get("grower_farm_size") or 1.0)
        revenue_potential = min(100000.0, farm_size * 12000)

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
                "weather_risk_score":       weather_risk_score,           # real, shared across territory
                "weather_source":           "open-meteo" if weather_summary else "fallback",
                "weather_components":       weather_summary["components"] if weather_summary else None,
                "inventory_shortage_level": inventory_shortage,
                "inventory_pct":            inventory_pct,
                "crop_stage":               crop,
                "crop_stage_sensitivity":   crop_sensitivity,
                "competitor_activity":      competitor_activity,
                "complaint_open":           not campaign_attended and random.random() < 0.3,
                "revenue_potential":        round(revenue_potential, 2),
                "max_ltv":                  100000.0,
                "days_since_last_visit":    days_since,
            },
            created_at=datetime.utcnow(),
        )
        db.add(signal)

    db.commit()
    db.close()
    print(f"✓ Seeded {len(entities)} growers and {len(entities)} signals for {TARGET_REP}")


if __name__ == "__main__":
    seed()