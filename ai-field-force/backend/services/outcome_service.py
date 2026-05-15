from sqlalchemy.orm import Session
from models.db.outcome import Outcome
from models.db.farmers import FarmerRetailer
from models.schemas.outcome import OutcomeRecord
from core.ml.weight_updater import update_weights
from core.ml.weights import SIGNAL_WEIGHTS
from datetime import datetime


class OutcomeService:

    def __init__(self, db: Session):
        self.db = db

    def record_outcome(self, outcome: OutcomeRecord) -> dict:
        # 1. Verify entity exists
        entity = self.db.query(FarmerRetailer).filter(
            FarmerRetailer.id == outcome.entity_id
        ).first()

        if not entity:
            return {"error": "Entity not found"}

        # 2. Derive success from outcome_rating (4+ = success)
        success = outcome.outcome_rating >= 4

        # 3. Save to DB
        db_outcome = Outcome(
            entity_id=outcome.entity_id,
            rep_id=outcome.rep_id,
            visited_at=datetime.utcnow(),
            outcome_rating=outcome.outcome_rating,
            outcome_type=outcome.outcome_type,
            actions_taken=outcome.actions_taken + outcome.actions_accepted,
            notes=outcome.notes,
            signals_at_visit={}
        )
        self.db.add(db_outcome)
        self.db.commit()
        self.db.refresh(db_outcome)

        # 4. Bayesian weight update
        updated_weights = update_weights(
            current_weights=SIGNAL_WEIGHTS,
            signals_at_visit={},
            outcome_rating=outcome.outcome_rating
        )

        # 5. Recommendation acceptance rate
        acceptance_rate = (
            round(len(outcome.actions_accepted) / len(outcome.actions_taken), 2)
            if outcome.actions_taken else 0.0
        )

        return {
            "status":                       "recorded",
            "outcome_id":                   db_outcome.id,
            "entity_id":                    outcome.entity_id,
            "outcome_rating":               outcome.outcome_rating,
            "success":                      success,
            "recommendation_acceptance_rate": acceptance_rate,
            "weights_updated":              updated_weights
        }