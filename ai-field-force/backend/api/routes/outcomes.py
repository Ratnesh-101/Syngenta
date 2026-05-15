from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from services.outcome_service import OutcomeService
from models.schemas.outcome import OutcomeRecord

router = APIRouter()

@router.post("/record")
def record_outcome(outcome: OutcomeRecord, db: Session = Depends(get_db)):
    service = OutcomeService(db)
    return service.record_outcome(outcome)