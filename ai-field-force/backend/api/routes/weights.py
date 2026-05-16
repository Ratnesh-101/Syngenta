# backend/api/routes/weights.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from services.weight_service import WeightService
from core.auth.roles import require_role
from models.db.rep import Rep

router = APIRouter()


@router.post(
    "/recalibrate",
    summary="Recalibrate signal weights (manager/admin only)",
)
def recalibrate_weights(
    db: Session = Depends(get_db),
    current: Rep = Depends(require_role("manager", "admin")),
):
    # Managers/admins recalibrate against a target rep's outcomes. For the
    # hackathon demo we recalibrate using the manager's own rep_id if linked,
    # otherwise against REP_0338 (the seeded territory) so the call is always
    # demonstrable. In production this would take a `rep_id` body field plus
    # a check that the manager owns that rep_id's territory.
    target_rep_id = current.rep_id or "REP_0338"
    service = WeightService(db)
    return service.recalibrate(target_rep_id)