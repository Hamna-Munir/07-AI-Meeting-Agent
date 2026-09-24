# Day 45 — Real Google Calendar Integration 🔥

**Objective:** Connect the agent to your real Google Calendar — this is where mock data ends.

---

## 📖 Theory

### Google Calendar API

Google's Calendar API lets an application read and write calendar data (events, availability) on behalf of an authenticated user. This is the real external system the agent will act on for the rest of the week.

### OAuth 2.0

OAuth 2.0 is the authorization protocol that lets this application access a user's Google Calendar **without ever seeing their Google password** — the user explicitly grants a defined, limited set of permissions (scopes), and the application receives tokens it can use within those limits.

### Access tokens vs refresh tokens

- **Access token** — a short-lived credential used for actual API requests. It expires relatively quickly.
- **Refresh token** — a longer-lived credential used to obtain a new access token without requiring the user to log in again every time.

### API scopes

A scope defines exactly what an application is allowed to do — e.g., read-only calendar access is a different, narrower scope than event-editing access. Google explicitly recommends requesting only the scope actually needed (this directly echoes Week 5-6's least-privilege principle) — a read-only agent should not request write access it doesn't yet use.

### Authentication vs authorization

- **Authentication** — confirming *who* the user is.
- **Authorization** — confirming *what* that authenticated user (and by extension, this app) is allowed to do.

OAuth handles both: Google authenticates the user via their login, then the user authorizes this specific application for specific scopes.

### Calendar resources and the Events API

The Calendar API organizes data around calendars (a user may have several) and events within them. The Events API is what's used to list, query, and (later, Day 48) create events.

---

## 🛠️ Setup

1. Create a project in **Google Cloud Console**.
2. Enable the **Google Calendar API** for that project.
3. Configure OAuth 2.0 credentials (Desktop app type) and download `credentials.json`.

Keep secrets **out of GitHub** from the very first commit:

```
credentials.json
token.json
```

both already listed in `.gitignore`.

---

## 💻 Build

Create `calendar_service.py` with:

```python
def authenticate_google_calendar():
    """Handles the OAuth flow, returns an authenticated service object."""
    ...

def get_upcoming_events():
    """Returns upcoming events from the primary calendar."""
    ...

def get_calendar_events(time_min, time_max):
    """Returns events within a specific time range."""
    ...
```

**First real test:** can this Python application actually read your Google Calendar?

```
Upcoming Events

10:00 AM — Software Engineering
2:00 PM — Project Meeting
4:30 PM — Study Session
```

If this prints real events from your actual calendar, the integration is genuinely working — not simulated.

---

## 🧠 Quiz

1. What's the difference between an access token and a refresh token?
2. Why does OAuth let an app access a calendar without ever seeing the user's password?
3. Why should an app request the narrowest scope it actually needs?
4. What's the difference between authentication and authorization, in this context?

*(Try answering from memory first, then check the theory section above.)*

---

## 🐞 Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| `credentials.json` committed to GitHub | Forgot to add it to `.gitignore` before the first commit | Rotate the credentials immediately in Google Cloud Console if this happens, then fix `.gitignore` |
| Requesting write scope for a read-only feature | Copy-pasting a broader scope "just in case" | Request the minimum scope needed for the current feature; expand only when write access (Day 48) is actually built |
| Token expires and the app breaks silently | No handling for expired/invalid tokens | Check for and handle token refresh failures explicitly, rather than assuming the token always works |
| Testing against the wrong calendar | Multiple calendars exist on the account and the wrong one is queried | Explicitly confirm which calendar ID is being used (usually `'primary'` to start) |

---

## ✅ Checklist

- [ ] Google Cloud project created
- [ ] Calendar API enabled
- [ ] OAuth credentials configured, `credentials.json` downloaded
- [ ] `credentials.json` and `token.json` confirmed in `.gitignore` BEFORE first commit
- [ ] `authenticate_google_calendar()` working
- [ ] `get_upcoming_events()` successfully prints real events from the actual calendar
- [ ] Git commit made

---

## 📂 GitHub Push

```bash
git add .
git commit -m "Day 45: Real Google Calendar OAuth integration"
git push
```

---

## 🧠 Skill Learned

OAuth + real API integration
