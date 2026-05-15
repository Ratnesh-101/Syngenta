from fastapi import APIRouter
router = APIRouter()

@router.post("/record")
def record_outcome():
    return {"message": "outcomes coming soon"}