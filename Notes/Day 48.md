# Day 47 — Agent Decision + Human Approval

**Objective:** Connect the LLM decision-making layer with the real calendar tools built on Days 45-46.

---

## 📖 Theory

### The full workflow

```
User Request
     ↓
Meeting Agent
     ↓
Understand Request
     ↓
Extract Constraints
     ↓
Google Calendar Tool
     ↓
Check Availability
     ↓
Find Slots
     ↓
Present Options
     ↓
Human Chooses
     ↓
Create Event
```

Today's job is wiring together everything built individually across Days 43-46 into this single, coherent decision flow — the same integration principle as Week 6's Day 41, now applied to real calendar tools instead of mock ones.

### Available tools

```
get_calendar_events()
check_availability()
find_available_slots()
create_calendar_event()
```

### The critical rule: create_calendar_event() never executes automatically

This is Week 6's human-in-the-loop principle, continued and made even more important now that the action has a **real, external effect** on an actual calendar — not a mock draft.

The correct flow:

```
Agent: "I found 3 available times. Which one would you like?"
User:  "3:30 PM."
Agent: [only now creates the event]
```

The agent proposes; it does not decide unilaterally. This mirrors exactly the send/delete gating from Week 6 (Day 40) — read and search actions can run freely, but the one action with a real, hard-to-reverse external effect requires an explicit human choice first.

### Why this matters more than Week 6's version

An email draft that's never sent has essentially no consequence. A calendar event that's mistakenly created has a real effect — it might notify participants, occupy a real time slot, and require an explicit cancellation to undo. The stakes of getting the confirmation gate right are higher here than they were for drafting an email.

---

## 💻 Build

Wire the agent's tool-calling loop (same pattern as Weeks 5-6) so that:

- `get_calendar_events()`, `check_availability()`, and `find_available_slots()` are available for the agent to call freely
- `create_calendar_event()` is either excluded from the agent's own tool set entirely (the safest option, matching Week 6's approach to `send_email`) or explicitly requires a separate confirmation step before execution

---

## 🧠 Quiz

1. Why does `create_calendar_event()` specifically need to be gated, when the read/search tools don't?
2. How does this connect to Week 6's Day 40 safety principle?
3. Why are the stakes of an accidental calendar booking higher than an accidental email draft?
4. What should the agent say to the user once it has found available slots, before any event is created?

*(Try answering from memory first, then check the theory section above.)*

---

## 🐞 Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| Agent creates an event immediately after finding a slot | `create_calendar_event()` included in the same auto-executing tool loop as the read/search tools | Exclude it from the agent's automatic tool set, exactly as Week 6 excluded `send_email` |
| Agent doesn't clearly present options before acting | Jumping straight to a decision instead of stating the choices | Always have the agent explicitly list the available slots and wait for a response |
| Assuming a single proposed slot is "obviously fine" | Skipping confirmation for cases that "seem simple" | Confirmation applies to every event creation, not just ambiguous cases |
| No clear mapping from user's chosen time back to the specific slot | User says "3:30" but the system doesn't reliably match it to the right slot object | Track proposed slots explicitly so the user's choice maps unambiguously to one of them |

---

## ✅ Checklist

- [ ] Full decision workflow wired together (Days 43-46 combined)
- [ ] `create_calendar_event()` confirmed to never execute without human approval
- [ ] Agent correctly presents multiple slot options before any action
- [ ] User's slot choice correctly maps to the intended time
- [ ] Git commit made

---

## 📂 GitHub Push

```bash
git add .
git commit -m "Day 47: Agent decision-making with human approval gate"
git push
```

---

## 🧠 Skill Learned

Human-in-the-loop scheduling decisions
