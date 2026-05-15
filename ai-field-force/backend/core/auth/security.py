# backend/core/auth/security.py
import re
import bcrypt
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES


# ---------- passwords ----------
_BCRYPT_MAX_BYTES = 72


def _truncate(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(_truncate(password), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_truncate(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ---------- jwt ----------
def create_access_token(subject: str, extra_claims: Optional[dict] = None) -> str:
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
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


# ---------- identifier helpers ----------
def normalize_phone(raw: str) -> str:
    return re.sub(r"\D", "", raw or "")


def is_email(identifier: str) -> bool:
    return "@" in (identifier or "")