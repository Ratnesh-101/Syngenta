# backend/core/auth/otp/console_sender.py
import logging
from core.auth.otp.base import OtpSender

log = logging.getLogger("otp.console")
log.setLevel(logging.INFO)
if not log.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(message)s"))
    log.addHandler(h)


class ConsoleOtpSender(OtpSender):
    """Dev sender: prints OTP to server logs. Pair with DEV_MODE=true to also
    echo the code in the API response so the frontend can auto-fill it."""

    name = "console"

    def send(self, phone: str, code: str) -> None:
        # Use a visible, scannable format. This is the line you watch during demos.
        log.info("┌─────────────────────────────────────────┐")
        log.info(f"│ OTP for {phone:>16}: {code}            │")
        log.info("└─────────────────────────────────────────┘")