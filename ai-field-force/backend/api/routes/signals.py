# backend/api/routes/signals.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from services.signal_service import SignalService
from core.auth.dependencies import get_current_rep
from models.db.rep import Rep

router = APIRouter()


@router.get("/anomalies")
def get_anomalies(
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    if not current.rep_id:
        raise HTTPException(
            status_code=403,
            detail="Account not linked to a Syngenta rep ID. Contact your administrator."
        )
    service = SignalService(db)
    return service.get_anomalies(current.rep_id)