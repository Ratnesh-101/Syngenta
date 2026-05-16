# backend/models/schemas/google.py
from pydantic import BaseModel, Field


class GoogleVerifyRequest(BaseModel):
    id_token: str = Field(..., description="The id_token returned by Google's JS SDK")