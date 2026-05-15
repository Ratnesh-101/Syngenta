from fastapi import APIRouter
from services.visit_service import VisitService
from datetime import datetime

router = APIRouter()
service = VisitService()

@router.get("/today")
def get_today_visits(rep_id: str = "R-01"):
    return service.generate_daily_priority_list(rep_id)

@router.get("/{entity_id}/brief")
def get_visit_brief(entity_id: str, rep_id: str = "R-01"):
    return service.get_visit_brief(entity_id, rep_id)

@router.get("/{entity_id}/explain")
def get_visit_explanation(entity_id: str, rank: int = 1):
    return service.get_visit_explanation(entity_id, rank)

@router.get("/today/export")
def export_today_visits(rep_id: str = "R-01"):
    visits = service.generate_daily_priority_list(rep_id)
    return {
        "exported_at": datetime.utcnow().isoformat(),
        "rep_id":      rep_id,
        "total":       len(visits),
        "visits":      visits
    }