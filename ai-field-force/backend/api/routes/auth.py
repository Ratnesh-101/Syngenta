# backend/api/routes/auth.py
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db.session import get_db
from models.db.rep import Rep
from models.schemas.auth import (
    PasswordRegisterRequest,
    PasswordLoginRequest,
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
        extra_claims={"rep_id": rep.rep_id, "email": rep.primary_email, "role": rep.role},
    )
    return TokenResponse(
        access_token=token,
        expires_in_minutes=JWT_EXPIRE_MINUTES,
        rep=RepProfile.model_validate(rep),
    )


# ---------- password endpoints ----------

@router.post("/register/password", response_model=TokenResponse, status_code=201,
             summary="Register with email + password")
def register_password(data: PasswordRegisterRequest, db: Session = Depends(get_db)):
    rep = service.register_with_password(db, data)
    return _token_response(rep)


@router.post("/login/password", response_model=TokenResponse,
             summary="Login with email or phone + password")
def login_password(data: PasswordLoginRequest, db: Session = Depends(get_db)):
    rep = service.login_with_password(db, data.identifier, data.password)
    return _token_response(rep)


@router.post("/token", response_model=TokenResponse,
             summary="OAuth2 form-data login (for Swagger Authorize button)")
def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Treats the OAuth2 `username` field as our identifier (email or phone)."""
    rep = service.login_with_password(db, form.username, form.password)
    return _token_response(rep)


# ---------- profile ----------

@router.get("/me", response_model=RepProfile)
def me(current: Rep = Depends(get_current_rep)):
    return RepProfile.model_validate(current)


# ---------- backward-compat aliases (old paths used by your test scripts) ----------
# These will be removed once frontend has migrated.

@router.post("/register", response_model=TokenResponse, status_code=201,
             summary="[Deprecated] Use /auth/register/password",
             deprecated=True)
def register_legacy(data: PasswordRegisterRequest, db: Session = Depends(get_db)):
    rep = service.register_with_password(db, data)
    return _token_response(rep)


@router.post("/login", response_model=TokenResponse,
             summary="[Deprecated] Use /auth/login/password",
             deprecated=True)
def login_legacy(data: PasswordLoginRequest, db: Session = Depends(get_db)):
    rep = service.login_with_password(db, data.identifier, data.password)
    return _token_response(rep)