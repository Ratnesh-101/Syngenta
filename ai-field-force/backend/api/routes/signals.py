from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_farmers():
    return {"message": "farmers coming soon"}