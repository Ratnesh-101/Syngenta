# backend/models/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    rep_id: Optional[str] = None  # optional: link to a known REP_XXXX from the dataset


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Email or phone number")
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    rep: "RepProfile"


class RepProfile(BaseModel):
    id: str
    rep_id: Optional[str] = None
    name: str
    email: EmailStr
    phone: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


TokenResponse.model_rebuild()