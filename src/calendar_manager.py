from datetime import datetime, timedelta
import pytz
import os
from typing import Optional
import streamlit as st


class CalendarManager:
    """Google Calendar integration with fallback to local storage"""

    def __init__(self):
        self.timezone = pytz.timezone(
            os.getenv("CALENDAR_TIMEZONE", "Asia/Kolkata")
        )
        self.service = None
        self.authenticated = False

    def authenticate(self):
        """Google OAuth flow - optional feature"""
        try:
            from googleapiclient.discovery import build
            from google_auth_oauthlib.flow import InstalledAppFlow
            import pickle

            SCOPES = ["https://www.googleapis.com/auth/calendar"]

            creds = None
            if os.path.exists("token.pickle"):
                with open("token.pickle", "rb") as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if os.path.exists("credentials.json"):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "credentials.json", SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    with open("token.pickle", "wb") as token:
                        pickle.dump(creds, token)
                else:
                    st.warning(
                        "credentials.json not found - using local storage"
                    )
                    return False

            self.service = build("calendar", "v3", credentials=creds)
            self.authenticated = True
            return True

        except Exception as e:
            st.info(f"Google Calendar not configured: {str(e)}")
            return False

    def create_event(self, event_data: dict) -> dict:
        """Create calendar event"""
        start_time = self.parse_time(event_data["time"])

        # Parse duration
        duration_str = event_data.get("duration", "1h")
        hours = 1

        if "m" in duration_str:
            hours = int(duration_str.replace("m", "")) / 60
        elif "h" in duration_str:
            hours = int(duration_str.replace("h", ""))

        end_time = start_time + timedelta(hours=hours)

        event = {
            "summary": event_data["title"],
            "description": (
                f"AI Assistant • Priority: "
                f"{event_data.get('priority', 'medium')} • "
                f"Category: {event_data.get('category', 'general')}"
            ),
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": self.timezone.zone,
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": self.timezone.zone,
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 10},
                    {"method": "email", "minutes": 60},
                ],
            },
        }

        if event_data.get("location"):
            event["location"] = event_data["location"]

        # Try Google Calendar, fallback to local storage
        if self.authenticated and self.service:
            try:
                created = (
                    self.service.events()
                    .insert(calendarId="primary", body=event)
                    .execute()
                )
                return {
                    **event,
                    "id": created["id"],
                    "htmlLink": created.get("htmlLink", ""),
                    "status": "created",
                    "source": "google_calendar",
                }
            except Exception as e:
                st.warning(f"Calendar sync error: {str(e)}")

        # Local fallback
        return {
            **event,
            "id": f"local_{datetime.now().timestamp()}",
            "status": "local",
            "source": "local_storage",
        }

    def parse_time(self, time_str: str) -> datetime:
        """Smart time parsing

        Examples:
        - "today 9PM" → today at 21:00
        - "tomorrow 7AM" → tomorrow at 07:00
        - "Friday 3PM" → next Friday at 15:00
        """

        now = datetime.now(self.timezone)
        time_str = time_str.lower().strip()

        # Default time: 6 PM
        hour = 18
        minute = 0

        # Parse time (AM / PM)
        if "pm" in time_str or "am" in time_str:
            time_part = time_str.split()[-1]
            hour_str = "".join(filter(str.isdigit, time_part))

            if hour_str:
                hour = int(hour_str)
                if "pm" in time_str and hour < 12:
                    hour += 12
                elif "am" in time_str and hour == 12:
                    hour = 0

        # Parse date
        target_date = now.date()

        if "tomorrow" in time_str:
            target_date = now.date() + timedelta(days=1)

        elif "monday" in time_str:
            days_ahead = (0 - now.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            target_date = now.date() + timedelta(days=days_ahead)

        elif "friday" in time_str:
            days_ahead = (4 - now.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            target_date = now.date() + timedelta(days=days_ahead)

        # Combine date and time
        result = self.timezone.localize(
            datetime(
                target_date.year,
                target_date.month,
                target_date.day,
                hour,
                minute,
            )
        )

        return result
