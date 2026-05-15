# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# JWT settings
JWT_SECRET         = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM      = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))  # 7 days default

# Dev/production mode. When true, OTPs are echoed in API responses and
# any other developer conveniences are enabled. Must be false in production.
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

# OTP settings
OTP_PROVIDER              = os.getenv("OTP_PROVIDER", "console")            # console | twilio_whatsapp
OTP_LENGTH                = int(os.getenv("OTP_LENGTH", "6"))
OTP_EXPIRY_SECONDS        = int(os.getenv("OTP_EXPIRY_SECONDS", "300"))     # 5 min
OTP_SEND_COOLDOWN_SECONDS = int(os.getenv("OTP_SEND_COOLDOWN_SECONDS", "30"))
OTP_MAX_SENDS_PER_HOUR    = int(os.getenv("OTP_MAX_SENDS_PER_HOUR", "5"))
OTP_MAX_VERIFY_ATTEMPTS   = int(os.getenv("OTP_MAX_VERIFY_ATTEMPTS", "5"))

# Twilio (unused while OTP_PROVIDER=console, but read here so .env stays consistent)
TWILIO_ACCOUNT_SID    = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN     = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM  = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")