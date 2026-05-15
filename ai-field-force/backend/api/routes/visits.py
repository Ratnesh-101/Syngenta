from fastapi import APIRouter
router = APIRouter()

@router.get("/today")
def get_today_visits():
    return {"message": "visits coming soon"}