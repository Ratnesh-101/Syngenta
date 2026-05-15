# backend/core/auth/security.py
import re
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------- passwords ----------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ---------- jwt ----------
def create_access_token(subject: str, extra_claims: Optional[dict] = None) -> str:
    """`subject` is the Rep.id (uuid). Extra claims can include rep_id, email."""
    now = datetime.utcnow()
    expire = now + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Raises JWTError on invalid/expired tokens."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


# ---------- identifier helpers ----------
def normalize_phone(raw: str) -> str:
    """Strip everything except digits. '+91 99999 99999' -> '919999999999'."""
    return re.sub(r"\D", "", raw or "")


def is_email(identifier: str) -> bool:
    return "@" in (identifier or "")