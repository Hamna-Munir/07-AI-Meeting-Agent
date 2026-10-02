"""
calendar_service.py
Day 45: Real Google Calendar integration — OAuth2 + Calendar API wrapper.

Setup required before this works:
1. Create a Google Cloud project.
2. Enable the "Google Calendar API".
3. Configure an OAuth consent screen + create OAuth client credentials
   (Desktop app type is simplest for local development).
4. Download the client secret JSON and save it as `credentials.json`
   in the project root (see config.CREDENTIALS_FILE).
5. `credentials.json` and `token.json` must NEVER be committed — they're
   already listed in .gitignore.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from . import config


def authenticate_google_calendar():
    """Handles the OAuth dance and returns an authenticated Calendar service.

    - On first run, opens a browser window for consent and writes token.json.
    - On later runs, reuses / refreshes the saved token.
    """
    creds = None

    if _token_file_exists():
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.GOOGLE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.CREDENTIALS_FILE, config.GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(config.TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service


def _token_file_exists() -> bool:
    import os
    return os.path.exists(config.TOKEN_FILE)


def get_upcoming_events(service, max_results: int = 10) -> List[dict]:
    """Returns the next `max_results` upcoming events on the primary calendar."""
    now = datetime.utcnow().isoformat() + "Z"
    try:
        events_result = (
            service.events()
            .list(
                calendarId=config.CALENDAR_ID,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
    except HttpError as e:
        raise RuntimeError(f"Failed to fetch upcoming events: {e}") from e

    return events_result.get("items", [])


def get_calendar_events(service, time_min: datetime, time_max: datetime) -> List[dict]:
    """Returns events between time_min and time_max (both timezone-aware datetimes)."""
    try:
        events_result = (
            service.events()
            .list(
                calendarId=config.CALENDAR_ID,
                timeMin=time_min.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
    except HttpError as e:
        raise RuntimeError(f"Failed to fetch calendar events: {e}") from e

    return events_result.get("items", [])


def create_calendar_event(
    service,
    title: str,
    start: datetime,
    end: datetime,
    description: Optional[str] = None,
    attendees_emails: Optional[List[str]] = None,
) -> dict:
    """Creates a real event on the calendar. Only call this AFTER human approval."""
    event_body = {
        "summary": title,
        "description": description or "",
        "start": {"dateTime": start.isoformat(), "timeZone": config.DEFAULT_TIMEZONE},
        "end": {"dateTime": end.isoformat(), "timeZone": config.DEFAULT_TIMEZONE},
    }
    if attendees_emails:
        event_body["attendees"] = [{"email": email} for email in attendees_emails]

    try:
        created_event = (
            service.events()
            .insert(calendarId=config.CALENDAR_ID, body=event_body, sendUpdates="all")
            .execute()
        )
    except HttpError as e:
        raise RuntimeError(f"Failed to create event: {e}") from e

    return created_event


if __name__ == "__main__":
    # Day 45 test: "Can my Python application actually read my Google Calendar?"
    svc = authenticate_google_calendar()
    events = get_upcoming_events(svc)
    if not events:
        print("No upcoming events found.")
    else:
        print("Upcoming Events\n")
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(f"{start} — {event.get('summary', '(no title)')}")
