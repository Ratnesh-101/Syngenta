# backend/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException
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
from models.schemas.otp import (
    OtpSendRequest,
    OtpSendResponse,
    OtpVerifyRequest,
)
from models.schemas.google import GoogleVerifyRequest
from services.auth_service import AuthService
from core.auth.security import create_access_token, normalize_phone
from core.auth.dependencies import get_current_rep
from core.auth.otp.store import otp_store
from core.auth.otp.factory import otp_sender
from core.auth.google_verify import verify_google_id_token
from config import JWT_EXPIRE_MINUTES, OTP_EXPIRY_SECONDS, DEV_MODE

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


# ---------- password ----------

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
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    rep = service.login_with_password(db, form.username, form.password)
    return _token_response(rep)


# ---------- OTP login ----------

@router.post("/otp/send", response_model=OtpSendResponse,
             summary="Send a one-time code to a phone number")
def otp_send(data: OtpSendRequest):
    phone = normalize_phone(data.phone)
    if not phone or len(phone) < 7:
        raise HTTPException(status_code=400, detail="Invalid phone number")

    code = otp_store.issue(phone)
    otp_sender.send(phone, code)

    return OtpSendResponse(
        phone=phone,
        expires_in_seconds=OTP_EXPIRY_SECONDS,
        sent_via=otp_sender.name,
        dev_otp=code if DEV_MODE else None,
    )


@router.post("/otp/verify", response_model=TokenResponse,
             summary="Verify the OTP and log in (auto-creates account if new)")
def otp_verify(data: OtpVerifyRequest, db: Session = Depends(get_db)):
    phone = normalize_phone(data.phone)
    otp_store.verify(phone, data.code)
    rep = service.login_or_signup_with_phone(db, phone)
    return _token_response(rep)


# ---------- Google login ----------

@router.post("/google/verify", response_model=TokenResponse,
             summary="Verify a Google id_token and log in (auto-creates / auto-links)")
def google_verify(data: GoogleVerifyRequest, db: Session = Depends(get_db)):
    info = verify_google_id_token(data.id_token)
    rep = service.login_or_signup_with_google(db, info)
    return _token_response(rep)


# ---------- account linking (requires auth) ----------

@router.post("/link/google", response_model=RepProfile,
             summary="Link a Google account to the currently logged-in rep")
def link_google(
    data: GoogleVerifyRequest,
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    info = verify_google_id_token(data.id_token)
    rep = service.link_google_to_current(db, current, info)
    return RepProfile.model_validate(rep)


@router.post("/link/phone/send", response_model=OtpSendResponse,
             summary="Send an OTP to a phone the user wants to link to their account")
def link_phone_send(
    data: OtpSendRequest,
    current: Rep = Depends(get_current_rep),
):
    phone = normalize_phone(data.phone)
    if not phone or len(phone) < 7:
        raise HTTPException(status_code=400, detail="Invalid phone number")

    code = otp_store.issue(phone)
    otp_sender.send(phone, code)

    return OtpSendResponse(
        phone=phone,
        expires_in_seconds=OTP_EXPIRY_SECONDS,
        sent_via=otp_sender.name,
        dev_otp=code if DEV_MODE else None,
    )


@router.post("/link/phone/verify", response_model=RepProfile,
             summary="Verify the OTP and attach the phone to the current account")
def link_phone_verify(
    data: OtpVerifyRequest,
    db: Session = Depends(get_db),
    current: Rep = Depends(get_current_rep),
):
    phone = normalize_phone(data.phone)
    otp_store.verify(phone, data.code)
    rep = service.link_phone_to_current(db, current, phone)
    return RepProfile.model_validate(rep)


# ---------- profile ----------

@router.get("/me", response_model=RepProfile)
def me(current: Rep = Depends(get_current_rep)):
    return RepProfile.model_validate(current)