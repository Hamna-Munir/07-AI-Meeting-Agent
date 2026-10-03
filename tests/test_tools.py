"""
test_tools.py
Tests find_available_slots() and check_availability() against a fake
calendar (no real Google API calls).
"""

from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from src import config
from src.calendar_tools import find_available_slots, check_availability

TZ = ZoneInfo(config.DEFAULT_TIMEZONE)


def _event(start_hm, end_hm, day):
    def iso(hm):
        h, m = hm
        return day.replace(hour=h, minute=m, second=0, microsecond=0, tzinfo=TZ).isoformat()

    return {"start": {"dateTime": iso(start_hm)}, "end": {"dateTime": iso(end_hm)}}


def _sample_day():
    return datetime(2026, 10, 1)  # arbitrary fixed day for deterministic tests


@patch("src.calendar_service.get_calendar_events")
def test_find_available_slots_skips_busy_blocks(mock_events):
    day = _sample_day()
    # Busy 1:00-2:00 PM and 2:30-3:30 PM (matches the roadmap's worked example)
    mock_events.return_value = [
        _event((13, 0), (14, 0), day),
        _event((14, 30), (15, 30), day),
    ]

    slots = find_available_slots(
        service=object(),
        date_obj=day,
        duration_minutes=30,
        time_preference="afternoon",
    )

    labels = [s["label"] for s in slots]
    assert any("2:00" in l for l in labels)
    assert not any("1:00" in l and "1:30" in l for l in labels)


@patch("src.calendar_service.get_calendar_events")
def test_check_availability_true_when_free(mock_events):
    mock_events.return_value = []
    day = _sample_day()
    start = day.replace(hour=15, tzinfo=TZ)
    end = day.replace(hour=15, minute=30, tzinfo=TZ)

    assert check_availability(object(), start, end) is True


@patch("src.calendar_service.get_calendar_events")
def test_check_availability_false_when_overlapping(mock_events):
    day = _sample_day()
    mock_events.return_value = [_event((15, 0), (16, 0), day)]
    start = day.replace(hour=15, minute=15, tzinfo=TZ)
    end = day.replace(hour=15, minute=45, tzinfo=TZ)

    assert check_availability(object(), start, end) is False
