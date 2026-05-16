# backend/api/routes/manager.py
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.session import get_db
from services.manager_service import ManagerService
from core.auth.roles import require_role
from models.db.rep import Rep
from models.schemas.manager import (
    ManagerOverview,
    RepMetrics,
    TopPriorityGrower,
)

router = APIRouter()


def _allowed_rep_ids(current: Rep, db: Session) -> List[str]:
    """Admins see ALL reps. Managers see only their `managed_rep_ids`."""
    if current.role == "admin":
        return [r.rep_id for r in db.query(Rep).filter(Rep.rep_id.isnot(None)).all()]
    return list(current.managed_rep_ids or [])


@router.get("/overview", response_model=ManagerOverview,
            summary="Top-level dashboard KPIs for the managed territory")
def overview(
    db: Session = Depends(get_db),
    current: Rep = Depends(require_role("manager", "admin")),
):
    allowed = _allowed_rep_ids(current, db)
    return ManagerService(db).overview(allowed)


@router.get("/reps", response_model=List[RepMetrics],
            summary="Per-rep performance metrics")
def reps_metrics(
    db: Session = Depends(get_db),
    current: Rep = Depends(require_role("manager", "admin")),
):
    allowed = _allowed_rep_ids(current, db)
    return ManagerService(db).rep_metrics(allowed)


@router.get("/reps/{rep_id}/details",
            summary="Drill into one rep: priority list, recent outcomes, anomalies")
def rep_details(
    rep_id: str,
    db: Session = Depends(get_db),
    current: Rep = Depends(require_role("manager", "admin")),
):
    allowed = _allowed_rep_ids(current, db)
    return ManagerService(db).rep_details(rep_id, allowed)


@router.get("/priorities/top", response_model=List[TopPriorityGrower],
            summary="Highest-priority growers across the entire managed territory")
def top_priorities(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current: Rep = Depends(require_role("manager", "admin")),
):
    allowed = _allowed_rep_ids(current, db)
    return ManagerService(db).top_priorities(allowed, limit=limit)