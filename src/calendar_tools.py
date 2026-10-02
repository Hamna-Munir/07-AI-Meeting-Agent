"""
calendar_tools.py
Day 46: Availability + smart slot finding, built on top of calendar_service.py.

These are the "tools" the agent (agent.py) can call. Each function is a thin,
well-defined wrapper so the agent's tool-calling stays predictable.
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo

from . import config


def _tz():
    return ZoneInfo(config.DEFAULT_TIMEZONE)


def _window_for_preference(date_obj: datetime, time_preference: Optional[str]):
    """Returns (window_start, window_end) datetimes for a given day + preference."""
    tz = _tz()
    if time_preference and time_preference in config.TIME_WINDOWS:
        start_hour, end_hour = config.TIME_WINDOWS[time_preference]
    else:
        start_hour, end_hour = config.WORKING_HOURS_START, config.WORKING_HOURS_END

    window_start = date_obj.replace(hour=start_hour, minute=0, second=0, microsecond=0, tzinfo=tz)
    window_end = date_obj.replace(hour=end_hour, minute=0, second=0, microsecond=0, tzinfo=tz)
    return window_start, window_end


_CLOCK_RE = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", re.IGNORECASE)


def parse_clock_time(date_obj: datetime, text: Optional[str]) -> Optional[datetime]:
    """Parses '3 PM', '3:30 PM', '2pm' etc into a tz-aware datetime on date_obj.
    Bare hours 1-7 are assumed PM, 8-11 assumed AM, matching prompts.py's rule."""
    if not text:
        return None
    match = _CLOCK_RE.search(text)
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    meridiem = (match.group(3) or "").lower()

    if not meridiem:
        meridiem = "pm" if 1 <= hour <= 7 else "am"

    if meridiem == "pm" and hour != 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0

    return date_obj.replace(hour=hour, minute=minute, second=0, microsecond=0, tzinfo=_tz())


def _apply_qualifier(window_start, window_end, preferred_dt, qualifier):
    """Narrows [window_start, window_end) based on an explicit clock time."""
    if preferred_dt is None:
        return window_start, window_end

    if qualifier == "after":
        window_start = max(window_start, preferred_dt)
    elif qualifier == "before":
        window_end = min(window_end, preferred_dt)
    else:  # "at" or unspecified -> center the window tightly on that time
        window_start = preferred_dt
        window_end = max(preferred_dt + timedelta(hours=3), window_end)

    return window_start, window_end


def check_availability(service, start: datetime, end: datetime) -> bool:
    """Returns True if the [start, end) window is free of existing events."""
    from .calendar_service import get_calendar_events

    events = get_calendar_events(service, start, end)
    for event in events:
        ev_start_raw = event["start"].get("dateTime")
        ev_end_raw = event["end"].get("dateTime")
        if not ev_start_raw or not ev_end_raw:
            continue  # all-day event without a specific time; ignore for slot math
        ev_start = datetime.fromisoformat(ev_start_raw)
        ev_end = datetime.fromisoformat(ev_end_raw)
        if start < ev_end and end > ev_start:
            return False  # overlap
    return True


def find_available_slots(
    service,
    date_obj: datetime,
    duration_minutes: int,
    time_preference: Optional[str] = None,
    preferred_start_time: Optional[str] = None,
    time_qualifier: Optional[str] = None,
    max_slots: int = config.MAX_SLOT_SUGGESTIONS,
    step_minutes: int = 30,
) -> List[dict]:
    """Scans the relevant window in `step_minutes` increments and returns
    up to `max_slots` free windows of `duration_minutes` length.

    If the user gave an explicit clock time ("at 3", "after 2 PM"), the
    scan window is narrowed/anchored around it instead of the whole
    morning/afternoon/evening block.
    """
    from .calendar_service import get_calendar_events

    window_start, window_end = _window_for_preference(date_obj, time_preference)

    preferred_dt = parse_clock_time(date_obj, preferred_start_time)
    if preferred_dt:
        window_start, window_end = _apply_qualifier(window_start, window_end, preferred_dt, time_qualifier)

    # Never offer a slot that has already passed today.
    now = datetime.now(_tz())
    if window_start < now:
        window_start = now
        # round up to the next step boundary so slots look clean
        minutes_past = window_start.minute % step_minutes
        if minutes_past:
            window_start += timedelta(minutes=step_minutes - minutes_past)
        window_start = window_start.replace(second=0, microsecond=0)

    if window_start >= window_end:
        return []

    # Pull all events for the whole window once instead of hitting the API per-slot.
    busy_events = get_calendar_events(service, window_start, window_end)
    busy_blocks = []
    for event in busy_events:
        ev_start_raw = event["start"].get("dateTime")
        ev_end_raw = event["end"].get("dateTime")
        if not ev_start_raw or not ev_end_raw:
            continue
        busy_blocks.append(
            (datetime.fromisoformat(ev_start_raw), datetime.fromisoformat(ev_end_raw))
        )

    slots = []
    cursor = window_start
    duration = timedelta(minutes=duration_minutes)
    step = timedelta(minutes=step_minutes)

    while cursor + duration <= window_end and len(slots) < max_slots:
        candidate_end = cursor + duration
        overlaps = any(cursor < b_end and candidate_end > b_start for b_start, b_end in busy_blocks)
        if not overlaps:
            slots.append(
                {
                    "start": cursor,
                    "end": candidate_end,
                    "label": f"{cursor.strftime('%I:%M %p').lstrip('0')} \u2013 "
                             f"{candidate_end.strftime('%I:%M %p').lstrip('0')}",
                }
            )
            cursor = candidate_end  # avoid overlapping suggestions
        else:
            cursor += step

    return slots
