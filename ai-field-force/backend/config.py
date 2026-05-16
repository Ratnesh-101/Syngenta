# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# JWT
JWT_SECRET         = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM      = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))

# Dev mode
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

# OTP
OTP_PROVIDER              = os.getenv("OTP_PROVIDER", "console")
OTP_LENGTH                = int(os.getenv("OTP_LENGTH", "6"))
OTP_EXPIRY_SECONDS        = int(os.getenv("OTP_EXPIRY_SECONDS", "300"))
OTP_SEND_COOLDOWN_SECONDS = int(os.getenv("OTP_SEND_COOLDOWN_SECONDS", "30"))
OTP_MAX_SENDS_PER_HOUR    = int(os.getenv("OTP_MAX_SENDS_PER_HOUR", "5"))
OTP_MAX_VERIFY_ATTEMPTS   = int(os.getenv("OTP_MAX_VERIFY_ATTEMPTS", "5"))

# Twilio (unused)
TWILIO_ACCOUNT_SID    = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN     = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM  = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# ---------- Territory health score weights ----------
# These are tunable defaults. In production they'd be recalibrated quarterly
# against real outcome data. Sum should equal 1.0.
HEALTH_WEIGHT_COVERAGE  = float(os.getenv("HEALTH_WEIGHT_COVERAGE",  "0.4"))
HEALTH_WEIGHT_OUTCOMES  = float(os.getenv("HEALTH_WEIGHT_OUTCOMES",  "0.4"))
HEALTH_WEIGHT_URGENCY   = float(os.getenv("HEALTH_WEIGHT_URGENCY",   "0.2"))

# Thresholds
HEALTH_COVERAGE_WINDOW_DAYS = int(os.getenv("HEALTH_COVERAGE_WINDOW_DAYS", "30"))
HIGH_VPS_THRESHOLD          = int(os.getenv("HIGH_VPS_THRESHOLD", "80"))
HEALTH_LABEL_GOOD           = int(os.getenv("HEALTH_LABEL_GOOD", "80"))
HEALTH_LABEL_WATCH          = int(os.getenv("HEALTH_LABEL_WATCH", "60"))