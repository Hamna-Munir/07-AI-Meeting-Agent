"""
prompts.py
All system / instruction prompts for the Meeting Agent live here so they're
easy to tune without touching logic code.
"""

from datetime import datetime


def extraction_system_prompt() -> str:
    """System prompt used by meeting_parser.py to pull structured fields
    out of a messy natural-language meeting request."""
    today = datetime.now().strftime("%A, %Y-%m-%d")

    return f"""You are a meeting-request extraction engine.

Today's date is: {today}

Your ONLY job is to read a user's natural language meeting request and
return a single JSON object with these fields:

{{
  "intent": "schedule_meeting" | "unclear",
  "title": string | null,
  "participants": array of strings (empty array if none mentioned),
  "date_phrase": string | null,
  "duration_minutes": integer | null,
  "time_preference": "morning" | "afternoon" | "evening" | "night" | null,
  "preferred_start_time": string | null,
  "time_qualifier": "at" | "after" | "before" | null,
  "description": string | null
}}

Rules:
- Do NOT invent a date, time, or duration the user did not imply. Use null
  for anything not stated.
- "date_phrase" must stay exactly as the user said it (relative), e.g.
  "tomorrow", "next Wednesday", "Friday". Date resolution happens in code.
- "title": a short title from the meeting purpose, e.g. "AI Project
  Discussion". null if no purpose is mentioned.
- "preferred_start_time": an explicit clock time, written in 12-hour form
  with AM/PM (e.g. "3 PM", "3:30 PM"). If the user gives a bare hour like
  "at 3", assume working hours (1-7 means PM, 8-11 means AM).
- "time_qualifier": "at" for an exact time ("at 3"), "after" for
  "after 2 PM", "before" for "before noon". null if no clock time is given.
- If the message only answers a previous question (e.g. "30 minutes"),
  fill in just that field and leave everything else null / empty.
- Return ONLY the JSON object. No preamble, no markdown fences, no commentary.
"""


def missing_info_prompt(missing_fields: list) -> str:
    """A friendly follow-up question when required info is missing."""
    field_questions = {
        "date": "Which date did you have in mind?",
        "duration": "How long should the meeting be?",
        "time_preference": "Do you prefer morning, afternoon, or evening?",
    }
    questions = [field_questions.get(f, f"Can you clarify: {f}?") for f in missing_fields]
    return " ".join(questions)


def slot_offer_message(slots: list) -> str:
    """Message shown to the user presenting available slots for approval."""
    if not slots:
        return "I couldn't find any free slots that match your request. Want to try a different day or time window?"

    lines = ["I found the following available slot(s):"]
    for i, slot in enumerate(slots, start=1):
        lines.append(f"{i}. {slot['label']}")
    lines.append("\nWhich one would you like? (reply with the number or the time)")
    return "\n".join(lines)


def confirmation_prompt(event: dict) -> str:
    """Final confirmation message before creating the real calendar event."""
    return (
        "Ready to create:\n\n"
        f"Title: {event['title']}\n"
        f"Date: {event['date_label']}\n"
        f"Time: {event['time_label']}\n"
        f"Participants: {', '.join(event['participants']) if event['participants'] else 'None'}\n\n"
        "Confirm & Create Event? (yes/no)"
    )
