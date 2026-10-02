"""
meeting_parser.py
Day 43-44: Turns a messy natural language meeting request into a validated
MeetingRequest object using an LLM + Pydantic schema validation.

The LLM only EXTRACTS phrases. Date math and "what is missing" are decided
in plain Python so they are deterministic and testable.
"""

import json
import re
from datetime import date, datetime, timedelta
from typing import List, Optional

import dateparser
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from . import config
from .prompts import extraction_system_prompt

_client = None


def _get_client() -> OpenAI:
    """Lazily builds the OpenAI-compatible client so importing this module
    (e.g. in tests, or before .env is loaded) never crashes on a missing key."""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=config.OPENAI_API_KEY or "not-set",
            base_url=config.OPENAI_BASE_URL,
        )
    return _client


WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}
VALID_QUALIFIERS = {"at", "after", "before"}


class MeetingRequest(BaseModel):
    """Structured, validated representation of a meeting request."""

    intent: str = Field(default="unclear")
    title: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    date_phrase: Optional[str] = None
    resolved_date: Optional[str] = None  # ISO date, filled in after normalization
    duration_minutes: Optional[int] = None
    time_preference: Optional[str] = None  # morning/afternoon/evening/night
    preferred_start_time: Optional[str] = None
    time_qualifier: Optional[str] = None  # at / after / before
    timezone: str = config.DEFAULT_TIMEZONE
    location: Optional[str] = None
    description: Optional[str] = None
    missing_fields: List[str] = Field(default_factory=list)


class ExtractionError(Exception):
    pass


def _call_llm(user_message: str) -> dict:
    response = _get_client().chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": extraction_system_prompt()},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        max_tokens=500,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ExtractionError(f"LLM did not return valid JSON: {raw!r}") from e


# ---------------------------------------------------------------------------
# Date normalization (deterministic, no LLM)
# ---------------------------------------------------------------------------
_MONTH_RE = re.compile(
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\b"
)


def _resolve_weekday_phrase(phrase: str, today: date) -> Optional[date]:
    """Handles 'Friday', 'this Friday', 'next Wednesday'.

    - 'Friday'        -> the upcoming Friday (never today)
    - 'next Friday'   -> Friday of NEXT calendar week (Mon-Sun)
    """
    lowered = phrase.lower()
    if re.search(r"\d", lowered) or _MONTH_RE.search(lowered):
        return None  # explicit calendar date; let dateparser handle it

    match = re.search(r"\b(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", lowered)
    if not match:
        return None

    target = WEEKDAYS[match.group(2)]
    if match.group(1):  # "next <weekday>"
        next_monday = today + timedelta(days=7 - today.weekday())
        return next_monday + timedelta(days=target)

    days_ahead = (target - today.weekday()) % 7 or 7
    return today + timedelta(days=days_ahead)


def _normalize_date(date_phrase: Optional[str], today: Optional[date] = None) -> Optional[str]:
    """Turn a relative phrase like 'tomorrow' or 'next Wednesday' into an ISO date."""
    if not date_phrase:
        return None
    today = today or date.today()

    weekday_date = _resolve_weekday_phrase(date_phrase, today)
    if weekday_date:
        return weekday_date.isoformat()

    parsed = dateparser.parse(
        date_phrase,
        settings={
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": datetime.combine(today, datetime.now().time()),
        },
    )
    if not parsed:
        return None
    return parsed.date().isoformat()


def compute_missing_fields(meeting: MeetingRequest) -> List[str]:
    """Required info the agent must have before it can look at the calendar.
    time_preference is optional (no preference = whole working day)."""
    missing = []
    if not meeting.resolved_date:
        missing.append("date")
    if not meeting.duration_minutes:
        missing.append("duration")
    return missing


def extract_meeting_request(user_message: str) -> MeetingRequest:
    """Main entry point: natural language -> validated MeetingRequest."""
    raw = _call_llm(user_message)

    qualifier = raw.get("time_qualifier")
    if qualifier not in VALID_QUALIFIERS:
        qualifier = None

    try:
        meeting = MeetingRequest(
            intent=raw.get("intent", "unclear"),
            title=raw.get("title"),
            participants=raw.get("participants") or [],
            date_phrase=raw.get("date_phrase"),
            resolved_date=_normalize_date(raw.get("date_phrase")),
            duration_minutes=raw.get("duration_minutes"),
            time_preference=raw.get("time_preference"),
            preferred_start_time=raw.get("preferred_start_time"),
            time_qualifier=qualifier,
            location=raw.get("location"),
            description=raw.get("description"),
        )
    except ValidationError as e:
        raise ExtractionError(str(e)) from e

    meeting.missing_fields = compute_missing_fields(meeting)
    return meeting


def merge_meeting_requests(old: MeetingRequest, new: MeetingRequest) -> MeetingRequest:
    """Combine an earlier partial request with the user's follow-up answer.

    New non-empty values win; participants are unioned; the date phrase and
    its resolved date always travel together.
    """
    data = old.model_dump()

    for key, value in new.model_dump().items():
        if key in ("missing_fields", "timezone", "intent", "date_phrase", "resolved_date", "participants"):
            continue
        if value not in (None, [], ""):
            data[key] = value

    data["participants"] = list(dict.fromkeys(old.participants + new.participants))

    if new.resolved_date:
        data["date_phrase"] = new.date_phrase
        data["resolved_date"] = new.resolved_date

    if new.intent == "schedule_meeting" or old.intent == "schedule_meeting":
        data["intent"] = "schedule_meeting"

    merged = MeetingRequest(**data)
    merged.missing_fields = compute_missing_fields(merged)
    return merged


if __name__ == "__main__":
    # Quick manual test — Day 43/44 style mini-project
    test_requests = [
        "Schedule a meeting tomorrow.",
        "Can we meet Friday at 3?",
        "Find me a 30-minute slot next week.",
        "I need a meeting with Ali sometime tomorrow afternoon.",
        "I want to meet Sarah for 45 minutes next Wednesday afternoon.",
        "Book a 45 minute meeting with Ahmed tomorrow after 2 PM.",
        "Schedule a meeting with Ahmed.",
        "Schedule it next Friday.",
        "Make it a 45-minute meeting with Zainab on Monday morning.",
        "30 minute call with the design team tomorrow evening.",
    ]
    for req in test_requests:
        try:
            result = extract_meeting_request(req)
            print(f"\nINPUT: {req}")
            print(result.model_dump_json(indent=2))
        except ExtractionError as e:
            print(f"\nINPUT: {req}\nERROR: {e}")
