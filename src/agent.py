"""
agent.py
Day 47-48: The orchestration layer.

Workflow implemented here:
Meeting Request -> AI Understanding -> Extract Details -> Google Calendar ->
Check Availability -> Find Suitable Slots -> Human Approval -> Create Real
Calendar Event

This class is intentionally stateful (one instance per conversation/session)
because slot approval requires remembering what was just proposed.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from . import config
from .calendar_service import authenticate_google_calendar, create_calendar_event
from .meeting_parser import (
    extract_meeting_request,
    merge_meeting_requests,
    ExtractionError,
    MeetingRequest,
)
from .prompts import missing_info_prompt, slot_offer_message, confirmation_prompt
from .safety import guard_before_create_event, guard_no_duplicate, SafetyViolation
from .scheduler import get_slot_options, build_event_payload


@dataclass
class AgentState:
    stage: str = "idle"  # idle -> collecting -> offering_slots -> confirming -> done
    meeting: Optional[MeetingRequest] = None
    slots: List[dict] = field(default_factory=list)
    pending_event: Optional[dict] = None
    created_event_slots: List[str] = field(default_factory=list)


class MeetingAgent:
    def __init__(self, calendar_service=None):
        # Allow dependency injection for tests (mock calendar service).
        self.service = calendar_service or authenticate_google_calendar()
        self.state = AgentState()

    # ------------------------------------------------------------------
    # Step 1-2: Understand the request + extract structured details
    # ------------------------------------------------------------------
    def handle_message(self, user_message: str) -> str:
        if self.state.stage in ("idle", "collecting"):
            return self._handle_new_or_followup_request(user_message)
        if self.state.stage == "offering_slots":
            return self._handle_slot_choice(user_message)
        if self.state.stage == "confirming":
            return self._handle_confirmation(user_message)
        # done -> start fresh
        self.state = AgentState()
        return self._handle_new_or_followup_request(user_message)

    def _handle_new_or_followup_request(self, user_message: str) -> str:
        try:
            new_info = extract_meeting_request(user_message)
        except ExtractionError as e:
            return f"Sorry, I couldn't understand that request ({e}). Could you rephrase it?"

        # If we already had a partial request pending (missing date/duration),
        # merge the new answer into it instead of starting over.
        if self.state.meeting is not None and self.state.stage == "collecting":
            meeting = merge_meeting_requests(self.state.meeting, new_info)
        else:
            meeting = new_info

        self.state.meeting = meeting
        self.state.stage = "collecting"

        if meeting.missing_fields:
            return missing_info_prompt(meeting.missing_fields)

        return self._find_and_offer_slots()

    # ------------------------------------------------------------------
    # Step 3-4: Check availability + find suitable slots
    # ------------------------------------------------------------------
    def _find_and_offer_slots(self) -> str:
        slots = get_slot_options(self.service, self.state.meeting)
        self.state.slots = slots

        if not slots:
            self.state.stage = "idle"
            return slot_offer_message([])

        self.state.stage = "offering_slots"
        return slot_offer_message(slots)

    # ------------------------------------------------------------------
    # Step 5: Human picks a slot
    # ------------------------------------------------------------------
    def _handle_slot_choice(self, user_message: str) -> str:
        chosen = self._match_slot(user_message)
        if chosen is None:
            return (
                "I didn't catch which slot you meant. "
                + slot_offer_message(self.state.slots)
            )

        event_payload = build_event_payload(self.state.meeting, chosen)
        self.state.pending_event = event_payload
        self.state.stage = "confirming"
        return confirmation_prompt(event_payload)

    def _match_slot(self, user_message: str) -> Optional[dict]:
        text = user_message.strip().lower()

        # Match by number, e.g. "1", "2."
        for i, slot in enumerate(self.state.slots, start=1):
            if text.startswith(str(i)):
                return slot

        # Match by time mentioned in the slot label, e.g. "3:30"
        for slot in self.state.slots:
            time_part = slot["label"].split("–")[0].strip().lower()
            if time_part.replace(" ", "") in text.replace(" ", ""):
                return slot

        return None

    # ------------------------------------------------------------------
    # Step 6: Human approval -> real event creation
    # ------------------------------------------------------------------
    def _handle_confirmation(self, user_message: str) -> str:
        try:
            guard_before_create_event(self.state.pending_event, user_message)
        except SafetyViolation as e:
            if "explicit" not in str(e):
                # Real safety problem (injection attempt, etc.) — hard stop.
                self.state = AgentState()
                return f"I won't proceed: {e}"
            # Just an unclear / negative reply — treat as rejection, ask again.
            self.state.stage = "offering_slots"
            return "No problem — " + slot_offer_message(self.state.slots)

        event = self.state.pending_event
        slot_key = f"{event['start'].isoformat()}|{event['title']}"

        try:
            guard_no_duplicate(self.state.created_event_slots, slot_key)
        except SafetyViolation as e:
            self.state = AgentState()
            return f"I won't proceed: {e}"

        created = create_calendar_event(
            self.service,
            title=event["title"],
            start=event["start"],
            end=event["end"],
            description=event["description"],
        )

        self.state.created_event_slots.append(slot_key)
        self.state.stage = "done"
        link = created.get("htmlLink", "(no link returned)")
        return f"✅ Event created: {event['title']} on {event['date_label']}, {event['time_label']}.\n{link}"
