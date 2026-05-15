# backend/models/schemas/otp.py
from pydantic import BaseModel, Field
from typing import Optional


class OtpSendRequest(BaseModel):
    phone: str = Field(..., min_length=7, max_length=20, description="Phone number, any format")


class OtpSendResponse(BaseModel):
    phone: str
    expires_in_seconds: int
    sent_via: str
    dev_otp: Optional[str] = Field(
        None,
        description="OTP code echoed in the response when DEV_MODE=true. Absent in production."
    )


class OtpVerifyRequest(BaseModel):
    phone: str = Field(..., min_length=7, max_length=20)
    code: str = Field(..., min_length=4, max_length=10)