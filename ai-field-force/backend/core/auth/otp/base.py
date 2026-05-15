# backend/core/auth/otp/base.py
from abc import ABC, abstractmethod


class OtpSender(ABC):
    """Abstract interface for OTP delivery. Implementations: console, twilio_whatsapp."""

    @abstractmethod
    def send(self, phone: str, code: str) -> None:
        """Deliver `code` to `phone`. Raise on failure."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...