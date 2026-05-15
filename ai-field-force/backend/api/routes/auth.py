# backend/api/routes/auth.py
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db.session import get_db
from models.db.rep import Rep
from models.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RepProfile,
)
from services.auth_service import AuthService
from core.auth.security import create_access_token
from core.auth.dependencies import get_current_rep
from config import JWT_EXPIRE_MINUTES

router = APIRouter()
service = AuthService()


def _token_response(rep: Rep) -> TokenResponse:
    token = create_access_token(
        subject=rep.id,
        extra_claims={"rep_id": rep.rep_id, "email": rep.email},
    )
    return TokenResponse(
        access_token=token,
        expires_in_minutes=JWT_EXPIRE_MINUTES,
        rep=RepProfile.model_validate(rep),
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    rep = service.register(db, data)
    return _token_response(rep)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """JSON login. Body: {"identifier": "...", "password": "..."}"""
    rep = service.authenticate(db, data.identifier, data.password)
    return _token_response(rep)


@router.post("/token", response_model=TokenResponse)
def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 form-data login. Used by Swagger's Authorize button.
    Treats the `username` field as our `identifier` (email or phone).
    """
    rep = service.authenticate(db, form.username, form.password)
    return _token_response(rep)


@router.get("/me", response_model=RepProfile)
def me(current: Rep = Depends(get_current_rep)):
    return RepProfile.model_validate(current)