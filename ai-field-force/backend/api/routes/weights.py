# backend/api/routes/weights.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from services.weight_service import WeightService
from core.auth.dependencies import get_current_rep
from models.db.rep import Rep

router = APIRouter()


@router.post("/recalibrate")
def recalibrate_weights(
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    # TODO (real-world): restrict to admin role / service token only.
    # Weekly recalibration is typically a cron job, not user-triggered.
    if not current.rep_id:
        raise HTTPException(
            status_code=403,
            detail="Account not linked to a Syngenta rep ID. Contact your administrator."
        )
    service = WeightService(db)
    return service.recalibrate(current.rep_id)