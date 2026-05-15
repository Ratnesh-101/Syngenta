from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from services.weight_service import WeightService

router = APIRouter()

@router.post("/recalibrate")
def recalibrate_weights(rep_id: str = "R-01", db: Session = Depends(get_db)):
    service = WeightService(db)
    return service.recalibrate(rep_id)