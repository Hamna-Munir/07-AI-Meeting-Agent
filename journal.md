# Journal — Week 7: AI Meeting Agent

A running log across Days 43–49. Daily technical breakdowns live in
`notes/day-XX.md`; this file is the higher-level narrative.

- **Day 43**: Learned the core difference between a chatbot and an agent —
  tools + decisions + actions, not just a response. Built a first-pass
  request analyzer and tested it against 10 varied phrasings.
- **Day 44**: Locked down a proper `MeetingRequest` schema with Pydantic.
  Realized date resolution has to be a separate, deterministic step —
  never trust the LLM to do date arithmetic.
- **Day 45**: First real external-system integration of the roadmap so far —
  Google OAuth2 + Calendar API. Got genuinely excited seeing my real
  calendar events print out from Python.
- **Day 46**: Built the free/busy slot-finding logic. Kept it simple
  (fixed-increment scan within a time window) rather than over-engineering
  a constraint solver — good enough for this scope.
- **Day 47**: This is where it started to feel like a "real" agent — wiring
  the LLM's understanding to actual tool calls, with a hard human-approval
  gate before anything destructive happens.
- **Day 48**: Full loop closed — request in, real event created in Google
  Calendar out. Wrapped it in a Streamlit chat UI for the demo.
- **Day 49**: Wrote the test suite and the evaluation matrix. Focused
  extra attention on the safety cases (rejection, duplicate booking,
  prompt-injection attempts) since this project can take real-world
  action, unlike earlier weeks.

## Why this is a strong portfolio project
Unlike Weeks 1–2 (which were closed-loop LLM apps), this project
demonstrates an agent that reads and writes to a real external system
(Google Calendar) with a genuine human-in-the-loop safety gate — a
meaningfully different and more advanced skill set.
