import json
import logging
from datetime import datetime, timedelta, date, time
from typing import List, Optional

from entity.base import Calendar
from services.database import Database
from services.config_service import Config
from services.ics_parser import download_ics_content, parse_ics_content, IcsEvent
from services.caldav_client import CaldavClient, CaldavEvent

logger = logging.getLogger(__name__)


class CalendarService:
    def __init__(self, database: Database, config: Config):
        self.db = database
        self.calendars = self.db.getCalendar()
        self.config = config

    def create_calendar(
        self, chat_id: str, chat_type: str, url: str, client_type: str = "ics"
    ) -> Calendar:
        return self.calendars.create_calendar(chat_id, chat_type, url, client_type)

    def get_calendar_by_id(self, calendar_id: str) -> Optional[Calendar]:
        return self.calendars.get_calendar_by_id(calendar_id)

    def get_calendars(self, chat_id: str = None) -> List[Calendar]:
        return self.calendars.get_calendars(chat_id)

    def delete_calendar(self, calendar_id: str, chat_id: str = None) -> bool:
        return self.calendars.delete_calendar(calendar_id, chat_id)

    def fetch_events(self, calendar: Calendar) -> List:
        if calendar.client_type == "caldav":
            return self._fetch_caldav_events(calendar)
        else:
            return self._fetch_ics_events(calendar)

    def _fetch_caldav_events(self, calendar: Calendar) -> List[CaldavEvent]:
        try:
            client = CaldavClient(calendar.url)
            now = datetime.now()
            window_start = now - timedelta(hours=6)
            window_end = now + timedelta(days=1)
            return client.get_events(start=window_start, end=window_end)
        except Exception as e:
            logger.error(
                f"Error fetching CalDAV events for calendar {calendar.id}: {e}"
            )
            return []

    def _fetch_ics_events(self, calendar: Calendar) -> List[IcsEvent]:
        try:
            ics_content = download_ics_content(calendar.url)
            events = parse_ics_content(
                ics_content, calendar.timezone or self.config.getTZone()
            )
            return events
        except Exception as e:
            logger.error(f"Error fetching ICS events for calendar {calendar.id}: {e}")
            return []

    def get_upcoming_events(
        self, calendar: Calendar, notify_before_minutes: int
    ) -> List:
        all_events = self.fetch_events(calendar)
        now = datetime.now()
        window_end = now + timedelta(minutes=notify_before_minutes)
        upcoming = []
        for event in all_events:
            try:
                from dateutil import parser

                event_start = (
                    parser.isoparse(event.start)
                    if isinstance(event.start, str)
                    else event.start
                )
                if event_start and now <= event_start <= window_end:
                    upcoming.append(event)
            except Exception as e:
                logger.warning(f"Error checking event time for {event.uid}: {e}")
        return upcoming

    def sync_all_calendars(self):
        logger.info("Starting calendar synchronization")
        calendars = self.calendars.get_calendars_with_chat()
        success_count = 0
        for calendar in calendars:
            try:
                logger.info(
                    f"Syncing calendar {calendar.id} for chat {calendar.chat_id}"
                )
                events = self.fetch_events(calendar)
                logger.info(f"Fetched {len(events)} events for calendar {calendar.id}")
                self.calendars.update_calendar_sync(calendar.id, "")
                success_count += 1
            except Exception as e:
                logger.error(f"Error syncing calendar {calendar.id}: {e}")
        logger.info(
            f"Calendar sync complete: {success_count}/{len(calendars)} successful"
        )
