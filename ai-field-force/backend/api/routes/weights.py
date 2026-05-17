# backend/api/routes/weights.py
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.session import get_db
from services.weight_service import WeightService
from core.auth.dependencies import get_current_rep
from core.auth.roles import require_role
from models.db.rep import Rep
from models.db.weight_history import WeightHistory
from models.schemas.weights import WeightsCurrent, WeightHistoryItem
from core.ml.weights import SIGNAL_WEIGHTS

router = APIRouter()


@router.get("/current", response_model=WeightsCurrent,
            summary="Get the current signal weights")
def current_weights(
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    """All authenticated users can see current weights (transparency).
    This is what powers the priority list — so reps deserve to understand it.
    """
    last = (
        db.query(WeightHistory)
        .order_by(WeightHistory.created_at.desc())
        .first()
    )
    return WeightsCurrent(
        weights=(last.weights if last else dict(SIGNAL_WEIGHTS)),
        last_updated_at=(last.created_at if last else None),
        last_trigger=(last.trigger if last else None),
    )


@router.get("/history", response_model=List[WeightHistoryItem],
            summary="Recent weight changes — see how the model has learned")
def weight_history(
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    return (
        db.query(WeightHistory)
        .order_by(WeightHistory.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("/recalibrate",
             summary="Recalibrate signal weights (manager/admin only)")
def recalibrate_weights(
    db: Session = Depends(get_db),
    current: Rep = Depends(require_role("manager", "admin")),
):
    target_rep_id = current.rep_id or "REP_0338"
    service = WeightService(db)
    return service.recalibrate(target_rep_id)