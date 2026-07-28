import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import requests

from entity.base import Calendar
from services.database import Database
from services.config_service import Config
from services.calendar_service import CalendarService

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(
        self, database: Database, config: Config, calendar_service: CalendarService
    ):
        self.db = database
        self.sent_notifications = self.db.getSentNotification()
        self.calendar_service = calendar_service
        self.config = config
        self.tg_bot_url = config.get_tg_bot_url()
        self.tg_bot_token = config.get_tg_bot_token()
        self.notify_before_minutes = config.get_notify_before_minutes()

    def check_pending_notifications(self):
        logger.info("Checking for pending notifications")
        calendars = self.calendar_service.calendars.get_calendars_with_chat()
        now = datetime.now()
        window_end = now + timedelta(minutes=self.notify_before_minutes)
        logger.info(
            f"Notification window: now={now.isoformat()}, end={window_end.isoformat()}, "
            f"calendars={len(calendars)}, notify_before_minutes={self.notify_before_minutes}"
        )

        for calendar in calendars:
            try:
                events = self.calendar_service.fetch_events(calendar)
                logger.info(
                    f"Calendar {calendar.id}: fetched {len(events)} events, "
                    f"chat_id={calendar.chat_id}, tg_bot_url={self.tg_bot_url}"
                )
                for event in events:
                    if self._is_event_in_window(event, now, window_end):
                        if self.sent_notifications.is_event_sent(
                            calendar.id, event.uid
                        ):
                            logger.info(f"Event {event.uid} already sent, skipping")
                            continue
                        self._send_notification(calendar, event)
            except Exception as e:
                logger.error(f"Error processing calendar {calendar.id}: {e}")

    def _is_event_in_window(self, event, now: datetime, window_end: datetime) -> bool:
        try:
            from dateutil import parser

            event_start = (
                parser.isoparse(event.start)
                if isinstance(event.start, str)
                else event.start
            )
            if isinstance(event_start, datetime):
                if event_start.tzinfo is not None:
                    event_start = event_start.astimezone(timezone.utc).replace(
                        tzinfo=None
                    )
                in_window = now <= event_start <= window_end
                if not in_window:
                    logger.info(
                        f"Event {event.uid} start={event.start} parsed={event_start.isoformat()} "
                        f"not in window [{now.isoformat()}, {window_end.isoformat()}]"
                    )
                return in_window
            logger.info(
                f"Event {event.uid} start is not datetime: type={type(event_start).__name__} value={event.start}"
            )
            return False
        except Exception as e:
            logger.warning(f"Error checking event window for {event.uid}: {e}")
            return False

    def _send_notification(self, calendar: Calendar, event):
        if not self.tg_bot_url:
            logger.warning("TG_BOT_URL not configured, cannot send notification")
            return

        try:
            event_data = {
                "chat_id": int(calendar.chat_id)
                if calendar.chat_id and calendar.chat_id.lstrip("-").isdigit()
                else calendar.chat_id,
                "summary": event.summary or "",
                "description": event.description
                if hasattr(event, "description")
                else "",
                "location": event.location if hasattr(event, "location") else "",
                "start": event.start or "",
                "end": event.end or "",
                "all_day": event.all_day if hasattr(event, "all_day") else False,
                "uid": event.uid or "",
                "calendar_id": calendar.id,
                "calendar_url": calendar.url,
                "calendar_name": calendar.name or "",
            }

            headers = {"Content-Type": "application/json"}
            if self.tg_bot_token:
                headers["x-api-key"] = self.tg_bot_token

            url = f"{self.tg_bot_url.rstrip('/')}/calendar/event"
            response = requests.post(url, json=event_data, headers=headers, timeout=30)

            if response.status_code == 200:
                self.sent_notifications.record_sent(
                    calendar.id,
                    event.uid,
                    calendar.chat_id,
                    json.dumps(event_data, ensure_ascii=False),
                )
                logger.info(
                    f"Sent notification for event {event.uid} to chat {calendar.chat_id}"
                )
            else:
                logger.error(
                    f"Failed to send notification for event {event.uid}: HTTP {response.status_code} {response.text}"
                )

        except Exception as e:
            logger.error(f"Error sending notification for event {event.uid}: {e}")

    def get_pending_events_for_api(self, user_id: str = None) -> List:
        if not user_id:
            return []
        calendars = self.calendar_service.get_calendars(user_id)
        now = datetime.now()
        window_end = now + timedelta(minutes=self.notify_before_minutes)
        pending = []
        for calendar in calendars:
            events = self.calendar_service.fetch_events(calendar)
            for event in events:
                if self._is_event_in_window(event, now, window_end):
                    if not self.sent_notifications.is_event_sent(
                        calendar.id, event.uid
                    ):
                        pending.append(
                            {
                                "id": event.uid,
                                "uid": event.uid,
                                "user_id": user_id,
                                "title": event.summary,
                                "description": event.description
                                if hasattr(event, "description")
                                else "",
                                "location": event.location
                                if hasattr(event, "location")
                                else "",
                                "start_datetime": event.start,
                                "end_datetime": event.end,
                                "all_day": event.all_day
                                if hasattr(event, "all_day")
                                else False,
                                "calendar_timezone": calendar.timezone,
                            }
                        )
        return pending
