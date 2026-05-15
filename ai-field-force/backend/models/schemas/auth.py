# backend/models/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Literal


# ---- requests ----

class PasswordRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    rep_id: Optional[str] = None  # optional link to a Syngenta REP_XXXX


class PasswordLoginRequest(BaseModel):
    identifier: str = Field(..., description="Email or phone number")
    password: str


# ---- responses ----

class LinkedIdentity(BaseModel):
    provider: Literal["password", "whatsapp_otp", "google"]
    identifier: str
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RepProfile(BaseModel):
    id: str
    rep_id: Optional[str] = None
    name: str
    primary_email: Optional[EmailStr] = None
    role: str
    is_active: bool
    created_at: datetime
    identities: List[LinkedIdentity] = []

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    rep: RepProfile


# ---- backward-compat aliases for the original endpoint names ----
# These keep old client code working while the frontend team migrates.
RegisterRequest = PasswordRegisterRequest
LoginRequest = PasswordLoginRequest