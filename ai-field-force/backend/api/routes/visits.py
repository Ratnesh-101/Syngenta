# backend/api/routes/visits.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from services.visit_service import VisitService
from core.auth.dependencies import get_current_rep
from models.db.rep import Rep

router = APIRouter()
service = VisitService()


def _require_linked_rep(current: Rep) -> str:
    """A logged-in account must be linked to a Syngenta rep_id to access territory data."""
    if not current.rep_id:
        raise HTTPException(
            status_code=403,
            detail="Account not linked to a Syngenta rep ID. Contact your administrator."
        )
    return current.rep_id


@router.get("/today")
def get_today_visits(current: Rep = Depends(get_current_rep)):
    rep_id = _require_linked_rep(current)
    return service.generate_daily_priority_list(rep_id)


@router.get("/{entity_id}/brief")
def get_visit_brief(entity_id: str, current: Rep = Depends(get_current_rep)):
    rep_id = _require_linked_rep(current)
    # TODO (real-world): verify `entity_id` belongs to this rep's territory before returning.
    return service.get_visit_brief(entity_id, rep_id)


@router.get("/{entity_id}/explain")
def get_visit_explanation(
    entity_id: str,
    rank: int = 1,
    current: Rep = Depends(get_current_rep),
):
    _require_linked_rep(current)
    # TODO (real-world): verify entity_id belongs to this rep's territory.
    return service.get_visit_explanation(entity_id, rank)


@router.get("/today/export")
def export_today_visits(current: Rep = Depends(get_current_rep)):
    rep_id = _require_linked_rep(current)
    visits = service.generate_daily_priority_list(rep_id)
    return {
        "exported_at": datetime.utcnow().isoformat(),
        "rep_id":      rep_id,
        "total":       len(visits),
        "visits":      visits,
    }