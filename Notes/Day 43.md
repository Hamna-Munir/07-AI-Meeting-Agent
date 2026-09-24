# Day 43 — Meeting Agent Fundamentals

**Objective:** Understand how a meeting agent differs from a normal chatbot.

---

## 📖 Theory

### What is a Meeting Agent?

An agent that can understand a scheduling request, gather the required information, use calendar tools, reason about availability, and take an approved scheduling action. This is a direct continuation of the agent pattern from Weeks 5-6: goal → tools → decision → (confirmed) action — now applied to calendar scheduling specifically.

### Agent workflow

```
User Request → Understand → Extract Details → Check Calendar → Find Slots → Propose → Human Approves → Create Event
```

Each stage builds on the previous one — a wrong extraction (Day 44) leads to checking the wrong date; a wrong calendar check (Day 45-46) leads to proposing a slot that's actually busy.

### The scheduling problem

Scheduling isn't just "understand the request" — it's understanding a request that's often incomplete or ambiguous ("tomorrow afternoon" isn't a timestamp), then reconciling it against real external constraints (what's actually free) rather than just generating a plausible-sounding answer.

### Intent detection (recap)

As in Week 6, the first step is recognizing what the message is actually asking for — here specifically, whether it's a scheduling request at all, and if so, what kind (new meeting, reschedule, cancellation).

### Constraints

A scheduling request carries constraints that must all be satisfied simultaneously: a specific duration, a preferred time window, sometimes a specific participant's availability too. Finding a valid slot means finding a time that satisfies every constraint at once, not just one of them.

### Tools vs normal LLM responses

A normal LLM response to "can we meet tomorrow?" would just generate plausible-sounding text. A tool-using agent instead calls a real calendar tool to check actual availability — the difference between *describing* a schedule and *knowing* one.

### Agent decision-making

The agent must decide: is there enough information to search for a slot yet, or is something missing (Day 49 covers this failure case explicitly)? Once slots are found, which ones are worth proposing? This decision-making layer is what turns "read the calendar" into "be useful about scheduling."

---

## 💻 Coding Exercise

Build a **Meeting Request Analyzer**.

**Input:**
> "I want to meet Sarah for 45 minutes next Wednesday afternoon."

**Output:**
```json
{
  "intent": "schedule_meeting",
  "participant": "Sarah",
  "duration_minutes": 45,
  "date": "next Wednesday",
  "time_preference": "afternoon"
}
```

---

## 🛠 Mini Project

Create 10 meeting requests and test extraction against them, for example:

- "Schedule a meeting tomorrow."
- "Can we meet Friday at 3?"
- "Find me a 30-minute slot next week."
- "I need a meeting with Ali sometime tomorrow afternoon."

---

## 🧠 Quiz

1. What makes a meeting agent different from a chatbot that just talks about scheduling?
2. Why is "tomorrow afternoon" a constraint, not a final answer?
3. Why does an agent need a real calendar tool instead of just generating a plausible response?
4. What decision does the agent need to make before it can even search for a slot?

*(Try answering from memory first, then check the theory section above.)*

---

## 🐞 Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| Treating every message as a scheduling request | No intent check before extraction | Confirm intent first, exactly as Week 6's email classification did |
| Extracting a fake, specific timestamp from a vague phrase | Forcing "tomorrow afternoon" into a single time immediately | Represent it as a time window/preference (formalized fully on Day 44), not a guessed exact time |
| Assuming one participant when multiple are mentioned | Not handling multi-participant requests | Extract participants as a list, even if usually just one for now |
| Ignoring missing duration | Assuming a default without checking the message | Extract duration explicitly; handle "no duration given" as its own case (Day 49) |

---

## ✅ Checklist

- [ ] Meeting agent concept understood
- [ ] Meeting Request Analyzer built
- [ ] Tested against 10 sample requests
- [ ] Git commit made

---

## 📂 GitHub Push

```bash
git add .
git commit -m "Day 43: Meeting agent fundamentals + request analyzer"
git push
```

---

## 🧠 Skill Learned

Meeting intent + constraint extraction
