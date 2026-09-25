# Day 46 — Availability + Smart Slot Finding

**Objective:** Use real calendar data to find genuinely available meeting slots.

---

## 📖 Theory

### Free/busy

Free/busy is the specific piece of calendar information that matters for scheduling: not the full details of what's on someone's calendar, just whether a given time is occupied or open. Google Calendar's API supports scopes and endpoints specifically for this — an agent scheduling meetings often needs only free/busy data, not full event details (another least-privilege consideration, per Day 45).

### Calendar conflicts

A conflict is any existing event that overlaps with a candidate meeting time. The agent must check the real calendar for these before proposing (or, on Day 48, before creating) any slot.

### Time windows and duration

A time window (e.g., "afternoon" → 12:00–5:00 PM) combined with a required duration defines the actual search space for available slots — the agent needs to find a continuous free period at least as long as the duration, within the window.

### Date/time reasoning

This is where Day 44's normalized structured data actually gets used: turning "tomorrow afternoon, 30 minutes" into a concrete search against real calendar data for that specific date and window.

### Slot generation

Slot generation means computing the actual list of open time ranges within a window, given the calendar's busy periods — this is a real algorithmic step, not something an LLM should be asked to eyeball from a text description of the calendar.

**Worked example:**

Calendar for the day:
```
1:00–2:00 PM → Busy
2:00–2:30 PM → Free
2:30–3:30 PM → Busy
3:30–4:00 PM → Free
4:00–5:00 PM → Free
```

For a 30-minute meeting request, `find_available_slots()` should return:
```
Available slots:
1. 2:00 PM – 2:30 PM
2. 3:30 PM – 4:00 PM
3. 4:00 PM – 4:30 PM
```

Note the third slot: it's a 30-minute sub-window of the larger 4:00–5:00 PM free block, not just the full 1-hour block reported as a single option — this level of precision is what makes the agent's suggestions actually useful.

---

## 💻 Build

```python
def find_available_slots(date, duration_minutes, preferred_time_window):
    """
    Checks real calendar events for the given date, computes free
    periods within the preferred window, and returns valid slots of
    at least `duration_minutes` each.
    """
    ...
```

---

## 🧠 Quiz

1. What's the difference between free/busy data and full event details?
2. Why should slot generation be computed algorithmically rather than left to the LLM to eyeball?
3. In the worked example above, why are there three suggested slots instead of just reporting the three free blocks as-is?
4. What two inputs does `find_available_slots()` need at minimum?

*(Try answering from memory first, then check the theory section above.)*

---

## 🐞 Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| Suggesting a slot that's actually busy | Free/busy data not actually checked, or checked against the wrong date | Verify the exact date and calendar being queried matches the request |
| Reporting only whole free blocks, not sub-windows | Slot generation doesn't slice a large free block into duration-sized options | Generate every valid duration-length slot within each free block, as in the worked example |
| Off-by-one boundary errors | Treating a slot that starts exactly when a busy period ends as still busy (or vice versa) | Handle boundary times carefully and test them explicitly |
| Ignoring the preferred time window entirely | Slot search covers the whole day instead of respecting "afternoon" | Constrain the search to the requested window before generating slots |

---

## ✅ Checklist

- [ ] `find_available_slots()` implemented
- [ ] Tested against a real calendar with actual busy periods
- [ ] Verified slots correctly avoid conflicts
- [ ] Verified sub-window slot generation (like the worked example) works correctly
- [ ] Git commit made

---

## 📂 GitHub Push

```bash
git add .
git commit -m "Day 46: Availability checking and smart slot finding"
git push
```

---

## 🧠 Skill Learned

Tool result → reasoning → scheduling decision
