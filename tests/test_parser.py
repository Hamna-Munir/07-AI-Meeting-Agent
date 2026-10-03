"""
test_parser.py
Tests meeting_parser.py's date normalization and Pydantic validation logic
without hitting the real LLM (mocked _call_llm).
"""

from datetime import datetime, timedelta
from unittest.mock import patch

from src.meeting_parser import extract_meeting_request, MeetingRequest


def _mock_response(**overrides):
    base = {
        "intent": "schedule_meeting",
        "title": None,
        "participants": [],
        "date_phrase": "tomorrow",
        "duration_minutes": 30,
        "time_preference": None,
        "preferred_start_time": None,
        "location": None,
        "description": None,
        "missing_fields": [],
    }
    base.update(overrides)
    return base


@patch("src.meeting_parser._call_llm")
def test_basic_extraction(mock_llm):
    mock_llm.return_value = _mock_response()
    result = extract_meeting_request("Schedule a meeting tomorrow.")

    assert isinstance(result, MeetingRequest)
    assert result.intent == "schedule_meeting"
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    assert result.resolved_date == tomorrow


@patch("src.meeting_parser._call_llm")
def test_missing_duration_is_flagged(mock_llm):
    mock_llm.return_value = _mock_response(duration_minutes=None)
    result = extract_meeting_request("Schedule a meeting with Ahmed.")

    assert "duration" in result.missing_fields


@patch("src.meeting_parser._call_llm")
def test_unresolvable_date_is_flagged(mock_llm):
    mock_llm.return_value = _mock_response(date_phrase="whenever works I guess")
    result = extract_meeting_request("Meet whenever works I guess.")

    assert result.resolved_date is None
    assert "date" in result.missing_fields


@patch("src.meeting_parser._call_llm")
def test_participants_extracted(mock_llm):
    mock_llm.return_value = _mock_response(participants=["Sarah"], time_preference="afternoon")
    result = extract_meeting_request("I want to meet Sarah for 45 minutes next Wednesday afternoon.")

    assert result.participants == ["Sarah"]
    assert result.time_preference == "afternoon"
