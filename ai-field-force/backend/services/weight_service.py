# backend/services/weight_service.py
from typing import Optional, Dict
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models.db.outcome import Outcome
from models.db.weight_history import WeightHistory
from core.ml.weight_updater import update_weights
from core.ml.weights import SIGNAL_WEIGHTS


class WeightService:
    def __init__(self, db: Session):
        self.db = db

    # ---------- public API ----------

    def get_current_weights(self) -> Dict[str, float]:
        """Returns the latest weight snapshot, or the seeded defaults if none."""
        last = (
            self.db.query(WeightHistory)
            .order_by(WeightHistory.created_at.desc())
            .first()
        )
        return last.weights if last else dict(SIGNAL_WEIGHTS)

    def record_snapshot(
        self,
        *,
        weights: Dict[str, float],
        trigger: str,
        rep_id: Optional[str] = None,
        outcome_id: Optional[int] = None,
    ) -> WeightHistory:
        """Append a new snapshot. Computes delta from the previous one."""
        previous = self.get_current_weights()
        delta = {
            k: round(weights.get(k, 0.0) - previous.get(k, 0.0), 6)
            for k in set(list(weights.keys()) + list(previous.keys()))
        }
        # Only keep non-zero deltas to reduce noise
        delta = {k: v for k, v in delta.items() if abs(v) > 1e-9}

        snap = WeightHistory(
            rep_id=rep_id,
            trigger=trigger,
            outcome_id=outcome_id,
            weights=weights,
            delta=delta or None,
            created_at=datetime.utcnow(),
        )
        self.db.add(snap)
        self.db.commit()
        self.db.refresh(snap)
        return snap

    def recalibrate(self, rep_id: str) -> dict:
        """Aggregate last 7 days of outcomes into a new set of weights AND
        persist a snapshot tagged 'manual_recalibration'.
        """
        since = datetime.utcnow() - timedelta(days=7)
        outcomes = (
            self.db.query(Outcome)
            .filter(
                Outcome.rep_id == rep_id,
                Outcome.recorded_at >= since,
            )
            .all()
        )

        if not outcomes:
            current = self.get_current_weights()
            return {
                "status": "no_data",
                "message": "No outcomes in last 7 days to recalibrate from",
                "weights": current,
            }

        # Start from the current snapshot so recalibration is cumulative, not
        # a reset back to SIGNAL_WEIGHTS every time.
        current_weights = self.get_current_weights()
        for outcome in outcomes:
            current_weights = update_weights(
                current_weights=current_weights,
                signals_at_visit=outcome.signals_at_visit or {},
                outcome_rating=int(outcome.outcome_rating),
            )

        snap = self.record_snapshot(
            weights=current_weights,
            trigger="manual_recalibration",
            rep_id=rep_id,
        )

        return {
            "status":          "recalibrated",
            "outcomes_used":   len(outcomes),
            "period_days":     7,
            "updated_weights": current_weights,
            "snapshot_id":     snap.id,
            "delta":           snap.delta,
        }