# backend/core/auth/google_verify.py
"""
Verifies Google id_tokens against Google's public keys.

The frontend uses Google's JS SDK to get an id_token. The backend receives that
token and verifies it using Google's official library — which:
  - checks the signature against Google's rotating public keys
  - validates the audience (must match our Client ID)
  - validates the issuer (must be accounts.google.com or https://accounts.google.com)
  - validates expiry

Returns the verified token payload: sub (Google user id), email, email_verified, name, picture.
"""
from typing import Dict, Any
from fastapi import HTTPException

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from config import GOOGLE_CLIENT_ID


def verify_google_id_token(token: str) -> Dict[str, Any]:
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Server not configured for Google sign-in (missing GOOGLE_CLIENT_ID)",
        )
    if not token:
        raise HTTPException(status_code=400, detail="id_token required")

    try:
        info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=GOOGLE_CLIENT_ID,
        )
    except ValueError as e:
        # Invalid signature, expired, wrong audience, etc.
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {e}")

    # Defense in depth: explicitly check issuer (verify_oauth2_token already does this,
    # but the check is cheap and makes the security model explicit).
    if info.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        raise HTTPException(status_code=401, detail="Invalid Google token issuer")

    # We require an email — sub alone is not enough for account linking.
    if not info.get("email"):
        raise HTTPException(status_code=400, detail="Google account has no email")

    # Untrusted email = potential takeover vector. Reject unverified emails.
    if not info.get("email_verified"):
        raise HTTPException(status_code=400, detail="Google email is not verified")

    return info