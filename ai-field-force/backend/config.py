# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI (already used elsewhere — re-exposed here for consistency)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# JWT settings
JWT_SECRET     = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM  = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))  # 7 days default