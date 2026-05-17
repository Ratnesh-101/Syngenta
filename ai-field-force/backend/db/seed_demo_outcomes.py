# backend/db/seed_demo_outcomes.py
"""
Idempotent demo outcome seeder. Populates ~8 realistic outcomes against the
demo rep's territory AND records the corresponding WeightHistory snapshots
so the manager dashboard's 'learning over time' story is visible.

Safe to call on every startup — uses sentinel client_outcome_id values so
re-running won't duplicate.
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models.db.outcome import Outcome
from models.db.device import Device
from models.db.farmers import FarmerRetailer
from models.db.weight_history import WeightHistory
from core.ml.weight_updater import update_weights
from core.ml.weights import SIGNAL_WEIGHTS

DEMO_REP_ID = "REP_0338"
DEMO_DEVICE_ID = "demo-seed-device"

# (entity_id, days_ago, rating, type, actions, notes)
_DEMO_OUTCOMES = [
    ("GRW_00774", 12, 5, "sale",              ["product_demo", "fungicide_recommended"], "Closed deal on fungicide pack. Grower receptive."),
    ("GRW_02680", 10, 4, "complaint_resolved", ["site_visit", "expert_consultation"],     "Addressed earlier complaint about pest control. Grower satisfied."),
    ("GRW_03018", 8,  5, "sale",              ["pest_demo", "follow_up_scheduled"],       "Sold pest control package after seeing crop damage."),
    ("GRW_03789", 7,  3, "follow_up_needed",  ["discussion", "literature_shared"],        "Interested but needs to consult son. Follow up in 1 week."),
    ("GRW_04114", 5,  4, "sale",              ["product_demo"],                            "Initial sale of fungicide. Good rapport built."),
    ("GRW_00311", 4,  2, "no_interest",       ["discussion"],                              "Using competitor product, not switching this season."),
    ("GRW_00707", 3,  4, "sale",              ["pest_demo", "discount_offered"],           "Closed with seasonal discount."),
    ("GRW_00922", 1,  5, "sale",              ["product_demo", "bundle_sold"],             "Bundle sale: fungicide + pest control. Strong relationship."),
]


def _compute_delta(new: dict, old: dict) -> dict:
    delta = {
        k: round(new.get(k, 0.0) - old.get(k, 0.0), 6)
        for k in set(list(new.keys()) + list(old.keys()))
    }
    return {k: v for k, v in delta.items() if abs(v) > 1e-9}


def seed_demo_outcomes(db: Session) -> dict:
    from models.db.rep import Rep

    rep_row = db.query(Rep).filter(Rep.rep_id == DEMO_REP_ID).first()
    if not rep_row:
        return {"created": 0, "skipped": 0, "reason": f"{DEMO_REP_ID} rep not found"}

    # Demo device
    device = db.query(Device).filter(Device.id == DEMO_DEVICE_ID).first()
    if not device:
        device = Device(
            id=DEMO_DEVICE_ID,
            rep_id=rep_row.id,
            name="Demo seed device",
            platform="web",
            first_seen_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
            sync_count="0",
        )
        db.add(device)
        db.commit()

    # Start the weight chain from the latest existing snapshot (or defaults).
    # This makes the seeder play nicely with any future weight changes.
    latest_snap = (
        db.query(WeightHistory)
        .order_by(WeightHistory.created_at.desc())
        .first()
    )
    running_weights = latest_snap.weights if latest_snap else dict(SIGNAL_WEIGHTS)

    created = 0
    skipped = 0

    for i, (entity_id, days_ago, rating, otype, actions, notes) in enumerate(_DEMO_OUTCOMES):
        client_outcome_id = f"demo-seed-{i:03d}"

        existing = (
            db.query(Outcome)
            .filter(
                Outcome.device_id == DEMO_DEVICE_ID,
                Outcome.client_outcome_id == client_outcome_id,
            )
            .first()
        )
        if existing:
            skipped += 1
            continue

        entity = db.query(FarmerRetailer).filter(FarmerRetailer.id == entity_id).first()
        if not entity:
            skipped += 1
            continue

        when = datetime.utcnow() - timedelta(days=days_ago, hours=i)
        outcome = Outcome(
            client_outcome_id=client_outcome_id,
            device_id=DEMO_DEVICE_ID,
            entity_id=entity_id,
            rep_id=DEMO_REP_ID,
            visited_at=when,
            recorded_at=when,
            synced_at=when,
            outcome_rating=rating,
            outcome_type=otype,
            actions_taken=actions,
            notes=notes,
            signals_at_visit={},
        )
        db.add(outcome)
        db.commit()
        db.refresh(outcome)

        # Apply Bayesian update and persist a snapshot, mirroring what
        # OutcomeService.sync_outcomes does. This is what makes the
        # weight-history endpoint show a real learning trail.
        new_weights = update_weights(
            current_weights=running_weights,
            signals_at_visit={},
            outcome_rating=rating,
        )
        delta = _compute_delta(new_weights, running_weights)
        db.add(WeightHistory(
            rep_id=DEMO_REP_ID,
            trigger="outcome_logged",
            outcome_id=outcome.id,
            weights=new_weights,
            delta=delta or None,
            # Backdate so the history reflects when the outcome happened, not now.
            created_at=when,
        ))
        db.commit()

        running_weights = new_weights
        created += 1

    if created > 0:
        try:
            current_count = int(device.sync_count or "0")
        except (TypeError, ValueError):
            current_count = 0
        device.sync_count = str(current_count + created)
        device.last_sync_at = datetime.utcnow()
        db.commit()

    return {"created": created, "skipped": skipped}