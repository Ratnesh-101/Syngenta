# backend/services/outcome_service.py
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from models.db.outcome import Outcome
from models.db.farmers import FarmerRetailer
from models.schemas.outcome import (
    OutcomeRecord,
    SyncRequest,
    SyncOutcomeItem,
    SyncResponse,
    SyncResultItem,
)
from services.device_service import DeviceService
from core.ml.weight_updater import update_weights
from core.ml.weights import SIGNAL_WEIGHTS


class OutcomeService:
    def __init__(self, db: Session):
        self.db = db

    # ---------- new batch sync path (primary entrypoint) ----------

    def sync_outcomes(self, rep_id: str, payload: SyncRequest) -> SyncResponse:
        """Idempotent batch ingestion. Same (device_id, client_outcome_id) twice
        is detected and reported as 'duplicate', not double-inserted.
        """
        device_svc = DeviceService(self.db)
        device = device_svc.upsert_device(
            device_id=payload.device_id,
            rep_id=rep_id,
            name=payload.device_name,
            platform=payload.device_platform,
        )

        results: list[SyncResultItem] = []
        created = duplicate = failed = 0
        last_weights = SIGNAL_WEIGHTS

        for item in payload.outcomes:
            try:
                outcome, was_duplicate = self._upsert_outcome(
                    rep_id=rep_id,
                    device_id=device.id,
                    item=item,
                )
                if was_duplicate:
                    duplicate += 1
                    results.append(SyncResultItem(
                        client_outcome_id=item.client_outcome_id,
                        server_outcome_id=outcome.id,
                        status="duplicate",
                    ))
                    continue

                # Only "created" outcomes affect weights — otherwise replaying
                # the same batch would inflate them.
                last_weights = update_weights(
                    current_weights=last_weights,
                    signals_at_visit={},
                    outcome_rating=item.outcome_rating,
                )
                created += 1
                results.append(SyncResultItem(
                    client_outcome_id=item.client_outcome_id,
                    server_outcome_id=outcome.id,
                    status="created",
                ))
            except Exception as e:
                failed += 1
                results.append(SyncResultItem(
                    client_outcome_id=item.client_outcome_id,
                    server_outcome_id=None,
                    status="failed",
                    error=str(e),
                ))

        if created > 0:
            device_svc.mark_sync(device, created)

        return SyncResponse(
            synced_at=datetime.utcnow(),
            device_id=device.id,
            total=len(payload.outcomes),
            created_count=created,
            duplicate_count=duplicate,
            failed_count=failed,
            results=results,
        )

    def _upsert_outcome(
        self,
        *,
        rep_id: str,
        device_id: Optional[str],
        item: SyncOutcomeItem,
    ) -> tuple[Outcome, bool]:
        """Returns (outcome, was_duplicate). Raises on failure."""
        # Idempotency check
        if device_id and item.client_outcome_id:
            existing = (
                self.db.query(Outcome)
                .filter(
                    Outcome.device_id == device_id,
                    Outcome.client_outcome_id == item.client_outcome_id,
                )
                .first()
            )
            if existing:
                return existing, True

        # Validate entity exists
        entity = (
            self.db.query(FarmerRetailer)
            .filter(FarmerRetailer.id == item.entity_id)
            .first()
        )
        if not entity:
            raise ValueError(f"Entity {item.entity_id} not found")

        # Insert
        outcome = Outcome(
            client_outcome_id=item.client_outcome_id,
            device_id=device_id,
            entity_id=item.entity_id,
            rep_id=rep_id,
            visited_at=item.recorded_at or datetime.utcnow(),
            recorded_at=item.recorded_at or datetime.utcnow(),
            synced_at=datetime.utcnow(),
            outcome_rating=item.outcome_rating,
            outcome_type=item.outcome_type,
            actions_taken=item.actions_taken + item.actions_accepted,
            notes=item.notes,
            signals_at_visit={},
        )
        self.db.add(outcome)
        self.db.commit()
        self.db.refresh(outcome)
        return outcome, False

    # ---------- backward-compatible single-outcome path ----------

    def record_outcome(self, outcome: OutcomeRecord) -> dict:
        """Single-outcome submission. Internally routes through sync_outcomes
        so the idempotency + device-tracking story is identical.
        Falls back to a synthetic device_id when the legacy client doesn't supply one.
        """
        # Synthesize device_id / client_outcome_id for online-only legacy clients
        device_id = outcome.device_id or f"legacy:{outcome.rep_id}"
        client_outcome_id = outcome.client_outcome_id or str(uuid.uuid4())

        sync_req = SyncRequest(
            device_id=device_id,
            device_name="Legacy online client" if not outcome.device_id else None,
            device_platform="web" if not outcome.device_id else None,
            outcomes=[SyncOutcomeItem(
                client_outcome_id=client_outcome_id,
                entity_id=outcome.entity_id,
                outcome_rating=outcome.outcome_rating,
                outcome_type=outcome.outcome_type,
                actions_taken=outcome.actions_taken,
                actions_accepted=outcome.actions_accepted,
                notes=outcome.notes,
                recorded_at=outcome.recorded_at,
            )],
        )
        sync_resp = self.sync_outcomes(outcome.rep_id, sync_req)

        result = sync_resp.results[0]
        success = result.status == "created" and outcome.outcome_rating >= 4

        # Shape the response to match the legacy contract
        acceptance_rate = (
            round(len(outcome.actions_accepted) / len(outcome.actions_taken), 2)
            if outcome.actions_taken else 0.0
        )

        return {
            "status":                       result.status,
            "outcome_id":                   result.server_outcome_id,
            "entity_id":                    outcome.entity_id,
            "outcome_rating":               outcome.outcome_rating,
            "success":                      success,
            "recommendation_acceptance_rate": acceptance_rate,
            "client_outcome_id":            client_outcome_id,
            "device_id":                    device_id,
        }