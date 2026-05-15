# backend/core/auth/otp/factory.py
from config import OTP_PROVIDER
from core.auth.otp.base import OtpSender
from core.auth.otp.console_sender import ConsoleOtpSender


def get_otp_sender() -> OtpSender:
    """Returns the configured OTP sender. Add new providers here as they're built."""
    if OTP_PROVIDER == "console":
        return ConsoleOtpSender()
    # Future:
    # if OTP_PROVIDER == "twilio_whatsapp":
    #     from core.auth.otp.twilio_sender import TwilioWhatsAppSender
    #     return TwilioWhatsAppSender()
    raise RuntimeError(f"Unknown OTP_PROVIDER: {OTP_PROVIDER}")


# Module-level singleton
otp_sender = get_otp_sender()