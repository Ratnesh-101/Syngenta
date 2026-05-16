# backend/api/routes/outcomes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from services.outcome_service import OutcomeService
from models.schemas.outcome import OutcomeRecord, SyncRequest, SyncResponse
from core.auth.dependencies import get_current_rep
from models.db.rep import Rep

router = APIRouter()


def _require_linked(current: Rep) -> tuple[str, str]:
    """Returns (rep_pk, rep_id_str) for a linked rep, or raises 403."""
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
    # SECURITY: ignore client-supplied rep_id (we never trust the client for identity).
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