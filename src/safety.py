"""
safety.py
Human-in-the-loop enforcement + basic prompt-injection resistance.

Continues the Week 6 "human-in-the-loop" principle: create_calendar_event()
must NEVER fire without an explicit, unambiguous human confirmation for
THIS specific slot.
"""

import re
from typing import Optional

from . import config

CONFIRM_PATTERNS = [
    r"^\s*(yes|yep|yeah|confirm|confirmed|go ahead|do it|sounds good|ok|okay)\s*[.!]?\s*$",
]

REJECT_PATTERNS = [
    r"^\s*(no|nope|cancel|don'?t|stop|wait)\b",
]

# Phrases that indicate the message is trying to make the LLM ignore its
# instructions / act as if it already has approval. We never execute a
# calendar write based on text that matches these — a human must click/type
# a real confirmation in response to the exact slot shown.
INJECTION_MARKERS = [
    "ignore previous instructions",
    "ignore the above",
    "you are now",
    "disregard the rules",
    "act as if approved",
    "auto-approve",
    "skip confirmation",
    "system prompt",
]


class SafetyViolation(Exception):
    pass


def contains_injection_attempt(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in INJECTION_MARKERS)


def is_explicit_confirmation(user_reply: str) -> bool:
    """True only for a clean, unambiguous 'yes' to the last proposed slot."""
    reply = user_reply.strip()
    return any(re.match(p, reply, flags=re.IGNORECASE) for p in CONFIRM_PATTERNS)


def is_explicit_rejection(user_reply: str) -> bool:
    reply = user_reply.strip()
    return any(re.match(p, reply, flags=re.IGNORECASE) for p in REJECT_PATTERNS)


def guard_before_create_event(pending_slot: Optional[dict], user_reply: str) -> None:
    """Raises SafetyViolation if it is not safe to create the event.

    Call this immediately before calendar_service.create_calendar_event().
    """
    if not config.REQUIRE_HUMAN_APPROVAL:
        # This branch should never actually be reached in this project —
        # REQUIRE_HUMAN_APPROVAL must stay True. Kept explicit on purpose.
        raise SafetyViolation("REQUIRE_HUMAN_APPROVAL must never be disabled.")

    if pending_slot is None:
        raise SafetyViolation("No slot was ever proposed — nothing to confirm.")

    if contains_injection_attempt(user_reply):
        raise SafetyViolation("Message looks like a prompt-injection attempt; refusing to act on it.")

    if not is_explicit_confirmation(user_reply):
        raise SafetyViolation("Did not receive an explicit, unambiguous confirmation.")


def guard_no_duplicate(created_event_ids: list, slot_key: str) -> None:
    """Prevents the same request from creating two events for the same slot."""
    if slot_key in created_event_ids:
        raise SafetyViolation("An event for this exact slot was already created — refusing duplicate.")
