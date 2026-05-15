# backend/core/auth/otp/store.py
import secrets
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from fastapi import HTTPException

from config import (
    OTP_LENGTH,
    OTP_EXPIRY_SECONDS,
    OTP_SEND_COOLDOWN_SECONDS,
    OTP_MAX_SENDS_PER_HOUR,
    OTP_MAX_VERIFY_ATTEMPTS,
)


@dataclass
class OtpEntry:
    code: str
    expires_at: float
    attempts_used: int = 0
    consumed: bool = False


@dataclass
class PhoneSendHistory:
    last_sent_at: float = 0.0
    timestamps: List[float] = field(default_factory=list)  # rolling 1-hour window


class OtpStore:
    """Thread-safe in-memory store. Restart wipes pending OTPs (acceptable for short TTL)."""

    def __init__(self):
        self._otps: Dict[str, OtpEntry] = {}
        self._history: Dict[str, PhoneSendHistory] = {}
        self._lock = threading.Lock()

    def _now(self) -> float:
        return time.time()

    def _generate_code(self) -> str:
        upper = 10 ** OTP_LENGTH
        return str(secrets.randbelow(upper)).zfill(OTP_LENGTH)

    def _enforce_rate_limits(self, phone: str) -> None:
        hist = self._history.setdefault(phone, PhoneSendHistory())
        now = self._now()

        if now - hist.last_sent_at < OTP_SEND_COOLDOWN_SECONDS:
            wait = int(OTP_SEND_COOLDOWN_SECONDS - (now - hist.last_sent_at))
            raise HTTPException(
                status_code=429,
                detail=f"Please wait {wait}s before requesting another code",
            )

        cutoff = now - 3600
        hist.timestamps = [t for t in hist.timestamps if t > cutoff]
        if len(hist.timestamps) >= OTP_MAX_SENDS_PER_HOUR:
            raise HTTPException(
                status_code=429,
                detail="Too many OTP requests. Try again later.",
            )

    def issue(self, phone: str) -> str:
        with self._lock:
            self._enforce_rate_limits(phone)
            code = self._generate_code()
            self._otps[phone] = OtpEntry(
                code=code,
                expires_at=self._now() + OTP_EXPIRY_SECONDS,
            )
            hist = self._history.setdefault(phone, PhoneSendHistory())
            hist.last_sent_at = self._now()
            hist.timestamps.append(self._now())
            return code

    def verify(self, phone: str, code: str) -> bool:
        with self._lock:
            entry: Optional[OtpEntry] = self._otps.get(phone)
            if not entry:
                raise HTTPException(status_code=400, detail="No OTP requested for this phone")
            if entry.consumed:
                raise HTTPException(status_code=400, detail="OTP already used")
            if self._now() > entry.expires_at:
                self._otps.pop(phone, None)
                raise HTTPException(status_code=400, detail="OTP expired")
            if entry.attempts_used >= OTP_MAX_VERIFY_ATTEMPTS:
                self._otps.pop(phone, None)
                raise HTTPException(status_code=429, detail="Too many wrong attempts. Request a new OTP.")

            entry.attempts_used += 1
            if entry.code != code:
                raise HTTPException(status_code=400, detail="Invalid OTP")

            entry.consumed = True
            return True


otp_store = OtpStore()