from sqlalchemy.orm import Session
from models.db.outcome import Outcome
from core.ml.weight_updater import update_weights
from core.ml.weights import SIGNAL_WEIGHTS
from datetime import datetime, timedelta


class WeightService:

    def __init__(self, db: Session):
        self.db = db

    def recalibrate(self, rep_id: str) -> dict:
        # Get last 7 days of outcomes
        since = datetime.utcnow() - timedelta(days=7)
        outcomes = self.db.query(Outcome).filter(
            Outcome.rep_id == rep_id,
            Outcome.visited_at >= since
        ).all()

        if not outcomes:
            return {
                "status": "no_data",
                "message": "No outcomes in last 7 days to recalibrate from",
                "weights": SIGNAL_WEIGHTS
            }

        # Aggregate weight updates across all outcomes
        current_weights = dict(SIGNAL_WEIGHTS)
        for outcome in outcomes:
            current_weights = update_weights(
                current_weights=current_weights,
                signals_at_visit={},
                outcome_rating=int(outcome.outcome_rating)
            )

        return {
            "status":          "recalibrated",
            "outcomes_used":   len(outcomes),
            "period_days":     7,
            "updated_weights": current_weights
        }