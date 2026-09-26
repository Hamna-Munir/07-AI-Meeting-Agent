# Day 49 — Testing + Evaluation + Deployment

**Objective:** Make sure the Meeting Agent actually works reliably — with a real calendar, the cost of an untested failure is higher than ever this roadmap.

---

## 📖 Theory

### Why this evaluation matters more than previous weeks'

Every prior evaluation (Weeks 2-6) tested text output or draft actions. This week's agent can create a **real, external, hard-to-reverse effect** — a duplicate or wrongly-timed calendar event is a genuine inconvenience, not just a quality issue. That raises the bar for what "tested" actually means here.

### The 10 required test categories

1. **Basic scheduling** — "Schedule a 30-minute meeting tomorrow."
2. **Specific time** — "Book Friday at 3 PM."
3. **Flexible time** — "Any time tomorrow afternoon works."
4. **Conflict** — request a time when the calendar is already busy; the agent must not create a conflicting event.
5. **Missing information** — "Schedule a meeting with Ahmed." (no time/duration given) — the agent should ask for the missing details instead of guessing everything (this is exactly Day 44's "missing information" concern, now tested concretely).
6. **Ambiguous date** — "Schedule it next Friday." — the agent must handle date interpretation carefully (which Friday, relative to which reference date?).
7. **Duration** — "Make it a 45-minute meeting."
8. **Time zone** — test explicit timezone handling.
9. **Human rejection** — the agent suggests 3:30 PM, the user says "No, choose 4 PM" — the agent must not create the rejected 3:30 PM option.
10. **Duplicate scheduling** — test whether the same request accidentally creates multiple events (directly related to Day 48's duplicate-prevention concern).

---

## 📊 Evaluation Metrics

| Metric | What we're checking |
|---|---|
| Intent accuracy | Did it understand the request? |
| Extraction accuracy | Date/time/duration/participants correctly extracted? |
| Calendar accuracy | Did it read the real calendar correctly? |
| Conflict detection | Did it avoid busy slots? |
| Slot quality | Were suggestions actually available? |
| Tool selection | Did it call the right tool? |
| Event creation | Was the correct event actually created? |
| Human approval | Did it wait for confirmation before creating anything? |
| Error handling | What happens when the API call fails? |
| Safety | Can malicious instructions manipulate it? (continuing Week 6's prompt-injection testing discipline) |

---

## 💻 Testing

Run all 10 test categories against the real (or a dedicated test) Google Calendar, and record actual outcomes — not predicted ones — for each metric above.

---

## 🧠 Quiz

1. Why does test category 9 (human rejection) matter specifically for a real-write agent?
2. Why is duplicate-scheduling its own explicit test case rather than being assumed to "just work"?
3. What should happen in test category 5 (missing information) — should the agent guess, or ask?
4. Why does "safety" appear as its own evaluation metric here, continuing from Week 6?

*(Try answering from memory first, then check the theory section above.)*

---

## 🐞 Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| Only testing the happy path | Confirmation bias — running only the cases most likely to succeed | Deliberately run all 10 categories, including conflict, rejection, and duplicate-scheduling cases |
| Treating "no crash" as passing | Conflating reliability with actual correctness | Judge each test against the specific expected behavior for that category, not just absence of errors |
| Skipping the rejection test because it "should obviously work" | Assuming prompt-based safety is sufficient without verifying | Actually run the rejection scenario and confirm the rejected time was never created |
| Deploying before real-calendar testing is complete | Wanting to ship quickly | Complete all 10 test categories against the real calendar first — this is the one week where an untested bug has a real-world side effect |

---

## ✅ Checklist

- [ ] All 10 test categories run against real calendar data
- [ ] Evaluation table filled in with real results for every metric
- [ ] Conflict detection verified (no double-booking)
- [ ] Human rejection case verified (rejected slot never created)
- [ ] Duplicate scheduling case verified (no accidental double-creation)
- [ ] Malicious instruction case tested (safety, continuing Week 6)
- [ ] Deployed
- [ ] Git commit made

---

## 📂 GitHub Push

```bash
git add .
git commit -m "Day 49: Full evaluation and deployment of Meeting Agent"
git push
```

---

## 🧠 Skill Learned

Real-world agent evaluation + deploymentDay 49.md
