"""
scheduler.py
Sits between meeting_parser.py (what the user wants) and calendar_tools.py
(what's actually free), and formats the result for the agent to present.
"""

from datetime import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo

from . import config
from .calendar_tools import find_available_slots
from .meeting_parser import MeetingRequest


def resolve_meeting_date(meeting: MeetingRequest) -> Optional[datetime]:
    """Converts MeetingRequest.resolved_date (ISO string) into a tz-aware datetime
    anchored at midnight, ready for slot scanning."""
    if not meeting.resolved_date:
        return None
    naive = datetime.fromisoformat(meeting.resolved_date)
    return naive.replace(tzinfo=ZoneInfo(config.DEFAULT_TIMEZONE))


def get_slot_options(service, meeting: MeetingRequest) -> List[dict]:
    """Given a validated + date-resolved MeetingRequest, return candidate slots."""
    if meeting.missing_fields:
        return []  # caller should ask for missing info first (see safety/agent flow)

    date_obj = resolve_meeting_date(meeting)
    if date_obj is None:
        return []

    duration = meeting.duration_minutes or config.DEFAULT_MEETING_DURATION_MINUTES

    return find_available_slots(
        service=service,
        date_obj=date_obj,
        duration_minutes=duration,
        time_preference=meeting.time_preference,
        preferred_start_time=meeting.preferred_start_time,
        time_qualifier=meeting.time_qualifier,
    )


def build_event_payload(meeting: MeetingRequest, chosen_slot: dict) -> dict:
    """Assembles the final event details for the confirmation prompt / creation call."""
    return {
        "title": meeting.title or "Meeting",
        "date_label": chosen_slot["start"].strftime("%A, %B %d"),
        "time_label": chosen_slot["label"],
        "start": chosen_slot["start"],
        "end": chosen_slot["end"],
        "participants": meeting.participants,
        "description": meeting.description or "",
    }
