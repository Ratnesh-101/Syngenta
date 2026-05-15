from fastapi import APIRouter
from services.visit_service import VisitService

router = APIRouter()
service = VisitService()

@router.get("/today")
def get_today_visits(rep_id: str = "R-01"):
    return service.generate_daily_priority_list(rep_id)