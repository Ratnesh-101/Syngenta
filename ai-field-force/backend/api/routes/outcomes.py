# backend/api/routes/outcomes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from services.outcome_service import OutcomeService
from models.schemas.outcome import OutcomeRecord
from core.auth.dependencies import get_current_rep
from models.db.rep import Rep

router = APIRouter()


@router.post("/record")
def record_outcome(
    outcome: OutcomeRecord,
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    if not current.rep_id:
        raise HTTPException(
            status_code=403,
            detail="Account not linked to a Syngenta rep ID. Contact your administrator."
        )

    # SECURITY: never trust client-supplied rep_id. Always overwrite with
    # the rep_id derived from the JWT, regardless of what the client sent.
    outcome.rep_id = current.rep_id

    service = OutcomeService(db)
    return service.record_outcome(outcome)