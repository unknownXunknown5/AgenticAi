import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
X_AUTH_TOKEN = os.getenv("X_AUTH_TOKEN")
X_CT0 = os.getenv("X_CT0")

raw_hours = os.getenv("POST_HOURS", os.getenv("POST_HOUR", "10,15,20"))
POST_HOURS = [int(h.strip()) for h in raw_hours.split(",") if h.strip()]
POST_MINUTE = int(os.getenv("POST_MINUTE", "0"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")