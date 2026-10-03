# Week 7 Summary — AI Meeting Agent

## Goal
Build an agent that turns a natural-language scheduling request into a real
Google Calendar event, with human approval before anything is written.

## What was built
| Day | Focus | Output |
|-----|-------|--------|
| 43 | Meeting agent fundamentals | `meeting_parser.py` (rule-of-thumb version) + 10 test requests |
| 44 | Structured extraction | `MeetingRequest` Pydantic model, LLM JSON extraction, date normalization |
| 45 | Real Google Calendar (OAuth) | `calendar_service.py`: auth, upcoming events |
| 46 | Availability + slot finding | `calendar_tools.py`: `check_availability`, `find_available_slots` |
| 47 | Agent decision + human approval | `agent.py` state machine, `prompts.py` confirmation flow |
| 48 | Real event creation | `create_calendar_event()` wired to human-approved slot |
| 49 | Testing + evaluation | `tests/`, `evaluation/evaluation.csv`, `safety.py` |

## Architecture

```
User message
   │
   ▼
MeetingAgent.handle_message()
   │
   ├─ extract_meeting_request()  (meeting_parser.py + LLM)
   │       └─ missing fields? → ask follow-up question
   │
   ├─ get_slot_options()         (scheduler.py → calendar_tools.py)
   │       └─ no slots? → say so, ask to try another day/time
   │
   ├─ present slots → wait for human choice
   │
   ├─ build_event_payload() → confirmation_prompt()
   │       └─ wait for explicit human "yes"
   │
   ├─ safety.guard_before_create_event()   ← hard gate
   ├─ safety.guard_no_duplicate()          ← hard gate
   │
   └─ create_calendar_event()   (calendar_service.py) → real event
```

## Key decisions
- **Human-in-the-loop is enforced in code, not just prompted.** `safety.py`
  requires a regex-matched, unambiguous confirmation string before
  `create_calendar_event()` is ever called — an LLM "deciding" the user
  approved is not enough.
- **Date math is done in Python, not by the LLM.** The LLM only extracts the
  raw phrase (e.g. "next Wednesday"); `dateparser` resolves it to an ISO
  date. This avoids the LLM silently getting arithmetic wrong.
- **One API call per day-window**, not per candidate slot, to keep
  `find_available_slots` fast and within API quotas.

## Known limitations / next steps
- Multi-participant calendar overlap (checking attendees' calendars, not
  just the owner's) is not implemented yet.
- Timezone handling assumes a single `DEFAULT_TIMEZONE`; per-user timezone
  detection would be a good Phase 2 extension.
- `evaluation.csv` results are still marked PENDING — run the test plan
  against a real calendar before treating this as portfolio-final.
