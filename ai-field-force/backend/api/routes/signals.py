from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from services.signal_service import SignalService

router = APIRouter()

@router.get("/anomalies")
def get_anomalies(rep_id: str = "R-01", db: Session = Depends(get_db)):
    service = SignalService(db)
    return service.get_anomalies(rep_id)