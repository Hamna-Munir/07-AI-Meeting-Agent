"""
config.py
Central place for environment variables, model settings, and constants.

Follows the same pattern as Week 2 (Groq's OpenAI-compatible endpoint,
key name OPENAI_API_KEY, model 'openai/gpt-oss-120b').
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# LLM (Groq / OpenAI-compatible endpoint)
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

# ---------------------------------------------------------------------------
# Google Calendar
# ---------------------------------------------------------------------------
# Read-only scope is NOT enough here because we create events -> need write access.
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]

CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

# ---------------------------------------------------------------------------
# Scheduling defaults
# ---------------------------------------------------------------------------
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Karachi")
DEFAULT_MEETING_DURATION_MINUTES = 30
WORKING_HOURS_START = 9   # 9 AM
WORKING_HOURS_END = 20    # 8 PM

# Time-of-day windows used when the user says "morning" / "afternoon" / "evening"
TIME_WINDOWS = {
    "morning": (9, 12),
    "afternoon": (12, 17),
    "evening": (17, 20),
    "night": (20, 22),
}

# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------
MAX_SLOT_SUGGESTIONS = 3
REQUIRE_HUMAN_APPROVAL = True  # never flip this to False; see safety.py
