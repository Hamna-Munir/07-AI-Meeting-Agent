"""
test_scheduler.py
Tests scheduler.py's date resolution and event payload building.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

from src.meeting_parser import MeetingRequest
from src.scheduler import resolve_meeting_date, get_slot_options, build_event_payload


def test_resolve_meeting_date_returns_none_when_missing():
    meeting = MeetingRequest(resolved_date=None)
    assert resolve_meeting_date(meeting) is None


def test_resolve_meeting_date_parses_iso_string():
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    meeting = MeetingRequest(resolved_date=tomorrow)
    resolved = resolve_meeting_date(meeting)
    assert resolved.date().isoformat() == tomorrow


def test_get_slot_options_returns_empty_when_fields_missing():
    meeting = MeetingRequest(missing_fields=["date"])
    slots = get_slot_options(service=object(), meeting=meeting)
    assert slots == []


@patch("src.scheduler.find_available_slots")
def test_get_slot_options_calls_finder_when_ready(mock_find):
    mock_find.return_value = [{"label": "3:00 PM – 3:30 PM"}]
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    meeting = MeetingRequest(resolved_date=tomorrow, duration_minutes=30)

    slots = get_slot_options(service=object(), meeting=meeting)
    assert len(slots) == 1
    mock_find.assert_called_once()


def test_build_event_payload_formats_fields():
    meeting = MeetingRequest(title="AI Project Discussion", participants=["Ali"])
    slot = {
        "start": datetime(2026, 10, 1, 15, 30),
        "end": datetime(2026, 10, 1, 16, 0),
        "label": "3:30 PM – 4:00 PM",
    }
    payload = build_event_payload(meeting, slot)

    assert payload["title"] == "AI Project Discussion"
    assert payload["participants"] == ["Ali"]
    assert payload["time_label"] == "3:30 PM – 4:00 PM"
