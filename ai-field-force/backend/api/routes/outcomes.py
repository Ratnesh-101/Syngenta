# backend/api/routes/outcomes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.session import get_db
from services.outcome_service import OutcomeService
from models.schemas.outcome import OutcomeRecord, SyncRequest, SyncResponse
from core.auth.dependencies import get_current_rep
from models.db.rep import Rep
from models.db.outcome import Outcome

router = APIRouter()


def _require_linked(current: Rep) -> tuple[str, str]:
    if not current.rep_id:
        raise HTTPException(
            status_code=403,
            detail="Account not linked to a Syngenta rep ID. Contact your administrator.",
        )
    return current.id, current.rep_id


@router.post("/record",
             summary="Record a single outcome (online). Internally idempotent via /sync.")
def record_outcome(
    outcome: OutcomeRecord,
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    rep_pk, rep_id_str = _require_linked(current)
    outcome.rep_id = rep_id_str
    service = OutcomeService(db)
    return service.record_outcome(rep_pk, rep_id_str, outcome)


@router.post("/sync", response_model=SyncResponse,
             summary="Bulk-sync outcomes recorded offline. Idempotent by (device_id, client_outcome_id).")
def sync_outcomes(
    payload: SyncRequest,
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    rep_pk, rep_id_str = _require_linked(current)
    service = OutcomeService(db)
    return service.sync_outcomes(rep_pk, rep_id_str, payload)


@router.get("/recent",
            summary="Recent outcomes logged by the current rep")
def recent_outcomes(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    _, rep_id_str = _require_linked(current)
    rows = (
        db.query(Outcome)
        .filter(Outcome.rep_id == rep_id_str)
        .order_by(Outcome.recorded_at.desc().nullslast(), Outcome.visited_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id":               o.id,
            "entity_id":        o.entity_id,
            "outcome_rating":   o.outcome_rating,
            "outcome_type":     o.outcome_type,
            "actions_taken":    o.actions_taken,
            "notes":            o.notes,
            "recorded_at":      o.recorded_at,
            "synced_at":        o.synced_at,
            "client_outcome_id": o.client_outcome_id,
            "device_id":        o.device_id,
        }
        for o in rows
    ]