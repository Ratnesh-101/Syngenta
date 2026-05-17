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
from services.weight_service import WeightService
from core.ml.weight_updater import update_weights


class OutcomeService:
    """All outcome paths funnel through sync_outcomes() — it handles idempotency,
    device tracking, weight updates, AND weight-history snapshots.

    Identifier conventions:
      - rep_pk     : Rep.id (uuid) — used for Device foreign keys
      - rep_id_str : Rep.rep_id (e.g. 'REP_0338') — used for business filtering
    """
    def __init__(self, db: Session):
        self.db = db
        self.weight_svc = WeightService(db)

    # ---------- batch sync (primary entrypoint) ----------

    def sync_outcomes(self, rep_pk: str, rep_id_str: str, payload: SyncRequest) -> SyncResponse:
        device_svc = DeviceService(self.db)
        device = device_svc.upsert_device(
            device_id=payload.device_id,
            rep_pk=rep_pk,
            name=payload.device_name,
            platform=payload.device_platform,
        )

        results: list[SyncResultItem] = []
        created = duplicate = failed = 0

        # Each newly-created outcome updates the cumulative weights AND writes a snapshot
        running_weights = self.weight_svc.get_current_weights()

        for item in payload.outcomes:
            try:
                outcome, was_duplicate = self._upsert_outcome(
                    rep_id_str=rep_id_str,
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

                # Apply Bayesian update and persist as a snapshot tagged to this outcome
                running_weights = update_weights(
                    current_weights=running_weights,
                    signals_at_visit={},
                    outcome_rating=item.outcome_rating,
                )
                self.weight_svc.record_snapshot(
                    weights=running_weights,
                    trigger="outcome_logged",
                    rep_id=rep_id_str,
                    outcome_id=outcome.id,
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
        rep_id_str: str,
        device_id: Optional[str],
        item: SyncOutcomeItem,
    ) -> tuple[Outcome, bool]:
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

        entity = (
            self.db.query(FarmerRetailer)
            .filter(FarmerRetailer.id == item.entity_id)
            .first()
        )
        if not entity:
            raise ValueError(f"Entity {item.entity_id} not found")

        outcome = Outcome(
            client_outcome_id=item.client_outcome_id,
            device_id=device_id,
            entity_id=item.entity_id,
            rep_id=rep_id_str,
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

    # ---------- legacy single-outcome path ----------

    def record_outcome(self, rep_pk: str, rep_id_str: str, outcome: OutcomeRecord) -> dict:
        device_id = outcome.device_id or f"legacy:{rep_id_str}"
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
        sync_resp = self.sync_outcomes(rep_pk, rep_id_str, sync_req)

        result = sync_resp.results[0]
        success = result.status == "created" and outcome.outcome_rating >= 4
        acceptance_rate = (
            round(len(outcome.actions_accepted) / len(outcome.actions_taken), 2)
            if outcome.actions_taken else 0.0
        )

        return {
            "status":                        result.status,
            "outcome_id":                    result.server_outcome_id,
            "entity_id":                     outcome.entity_id,
            "outcome_rating":                outcome.outcome_rating,
            "success":                       success,
            "recommendation_acceptance_rate": acceptance_rate,
            "client_outcome_id":             client_outcome_id,
            "device_id":                     device_id,
        }