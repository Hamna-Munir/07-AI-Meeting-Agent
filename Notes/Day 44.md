# Day 44 — Structured Meeting Information

**Objective:** Learn how to turn messy natural language into reliable structured data.

---

## 📖 Theory

### Structured output, Pydantic, schema validation (recap)

As established in Week 6 (Day 37), structured output means the model returns validated, predictable data instead of free text, and Pydantic is what enforces that shape. The same discipline applies here — a scheduling agent that can't reliably extract a duration or date isn't safe to connect to a real calendar (Day 45 onward).

### Required vs optional fields

Not every meeting request includes every detail. A schema needs to distinguish what's genuinely required to proceed (e.g., some sense of date/duration) from what's optional (e.g., a description or location) — and the system needs a clear plan for what happens when a required field is missing (this becomes explicit on Day 49's "missing information" test case).

### Date/time normalization

Normalization means converting varied phrasings ("tomorrow," "next Wednesday," "in two days") into a consistent, computable representation — otherwise every downstream step (checking the calendar, finding slots) has to handle every possible phrasing itself.

### Time zones

A time without a timezone is ambiguous the moment more than one person or system is involved. Even for a single-user calendar agent, being explicit about which timezone a request is interpreted in avoids silent, hard-to-notice scheduling errors.

### Duration extraction

Duration might be stated explicitly ("45 minutes") or need a sensible default when omitted — but a default should be a deliberate, documented choice, not an accidental side effect of a missing field being ignored.

### Missing information

**The most important idea today:** "tomorrow afternoon" is not a final timestamp. The system needs to understand this as a **date + timezone + acceptable time window**, not force it into one exact, invented time. Treating a vague preference as if it were precise is exactly the kind of confident-but-wrong behavior this roadmap has been working against since Week 3's grounding lessons.

---

## 💻 Coding Exercise

Build the `MeetingRequest` Pydantic model:

```python
from pydantic import BaseModel
from typing import Optional

class MeetingRequest(BaseModel):
    intent: str
    title: Optional[str] = None
    participants: list[str] = []
    date: Optional[str] = None
    duration_minutes: Optional[int] = None
    preferred_start: Optional[str] = None
    preferred_end: Optional[str] = None
    timezone: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
```

---

## 🛠 Mini Project — Meeting Details Extractor

**Test input:**
> "Book a 45 minute meeting with Ahmed tomorrow after 2 PM."

**Expected extraction:** participant = Ahmed, duration_minutes = 45, date = tomorrow, preferred_start = 2:00 PM (as a window start, not a forced exact booking time).

---

## 🧠 Quiz

1. Why isn't "tomorrow afternoon" a final timestamp?
2. What's the difference between a required and an optional field in this schema?
3. Why does timezone matter even for a single-user calendar agent?
4. What should happen when a required field (like date) is missing from the request?

*(Try answering from memory first, then check the theory section above.)*

---

## 🐞 Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| Forcing a vague time into an exact timestamp | Extraction logic assumes every request gives a precise time | Represent vague preferences as a window (`preferred_start`/`preferred_end`), not a guessed exact value |
| Silently defaulting a missing duration | No explicit handling for an absent field | Make default duration a deliberate, visible choice (or flag it as missing, per Day 49) |
| Ignoring timezone entirely | Schema doesn't include a timezone field | Always capture timezone, even if defaulting to the user's local one |
| Treating "next Friday" and "this Friday" as the same | No real date normalization logic | Normalize relative dates carefully against the actual current date, not just a fixed offset |

---

## ✅ Checklist

- [ ] `MeetingRequest` Pydantic model built
- [ ] Vague time phrases represented as windows, not forced timestamps
- [ ] Timezone field included
- [ ] Tested against the "45 minute meeting with Ahmed tomorrow after 2 PM" example
- [ ] Git commit made

---

## 📂 GitHub Push

```bash
git add .
git commit -m "Day 44: Structured meeting information extraction"
git push
```

---

## 🧠 Skill Learned

Structured information extraction
