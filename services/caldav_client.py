import logging
from datetime import date, datetime, timedelta
from typing import List, Optional

import caldav
from icalendar import Calendar as ICalendar, Event as IEvent
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class CaldavEvent:
    def __init__(
        self,
        uid: str,
        summary: str,
        description: str,
        location: str,
        start: Optional[datetime],
        end: Optional[datetime],
        all_day: bool = False,
    ):
        self.uid = uid
        self.summary = summary
        self.description = description
        self.location = location
        self.start = start
        self.end = end
        self.all_day = all_day


class CaldavClient:
    def __init__(self, calendar_url: str):
        self.calendar_url = calendar_url
        self.calendar_id = calendar_url.rstrip("/").split("/")[-1]
        base_url = self._extract_base_url(calendar_url)
        self.client = caldav.DAVClient(url=base_url)

    @staticmethod
    def _extract_base_url(full_url: str) -> str:
        scheme_end = full_url.find("://")
        if scheme_end == -1:
            return full_url
        scheme = full_url[: scheme_end + 3]
        rest = full_url[scheme_end + 3 :]
        last_at = rest.rfind("@")
        if last_at == -1:
            host = rest.split("/")[0] if "/" in rest else rest
            return scheme + host
        auth = rest[: last_at + 1]
        host = (
            rest[last_at + 1 :].split("/")[0]
            if "/" in rest[last_at + 1 :]
            else rest[last_at + 1 :]
        )
        return scheme + auth + host

    def get_events(self, start: date = None, end: date = None) -> List[CaldavEvent]:
        try:
            principal = self.client.principal()
            calendars = principal.calendars()
            target = None
            for cal in calendars:
                cal_id = str(cal.url).rstrip("/").split("/")[-1]
                cal_name = str(cal.name) if cal.name else ""
                if self.calendar_id == cal_id or self.calendar_id == cal_name:
                    target = cal
                    break
            if not target:
                logger.error(f"Calendar {self.calendar_id} not found on CalDAV server")
                return []

            search_start = start or date.today()
            search_end = end or (date.today() + timedelta(days=1))

            result = []
            for caldav_event in target.search(
                start=search_start, end=search_end, event=True, expand=True
            ):
                ical = caldav_event.icalendar_instance
                for component in ical.subcomponents:
                    if component.name != "VEVENT":
                        continue
                    uid = str(component.get("UID", ""))
                    summary = str(component.get("SUMMARY", ""))
                    description = str(component.get("DESCRIPTION", ""))
                    location = str(component.get("LOCATION", ""))
                    dtstart = (
                        component.get("DTSTART").dt
                        if component.get("DTSTART")
                        else None
                    )
                    dtend = (
                        component.get("DTEND").dt if component.get("DTEND") else None
                    )
                    all_day = False
                    if dtstart and hasattr(dtstart, "date"):
                        all_day = True
                    if isinstance(dtstart, datetime):
                        dtstart = dtstart.isoformat()
                    else:
                        dtstart = str(dtstart) if dtstart else None
                    if isinstance(dtend, datetime):
                        dtend = dtend.isoformat()
                    else:
                        dtend = str(dtend) if dtend else None
                    result.append(
                        CaldavEvent(
                            uid=uid,
                            summary=summary,
                            description=description,
                            location=location,
                            start=dtstart,
                            end=dtend,
                            all_day=all_day,
                        )
                    )
            logger.info(
                f"Fetched {len(result)} events from CalDAV calendar {self.calendar_url}"
            )
            return result
        except Exception as e:
            logger.error(
                f"Error fetching events from CalDAV calendar {self.calendar_url}: {e}"
            )
            return []

    def create_event(
        self,
        summary: str,
        start: datetime,
        end: datetime,
        description: str = "",
        location: str = "",
        all_day: bool = False,
    ) -> Optional[str]:
        try:
            principal = self.client.principal()
            calendars = principal.calendars()
            target = None
            for cal in calendars:
                cal_id = str(cal.url).rstrip("/").split("/")[-1]
                cal_name = str(cal.name) if cal.name else ""
                if self.calendar_id == cal_id or self.calendar_id == cal_name:
                    target = cal
                    break
            if not target:
                logger.error(f"Calendar {self.calendar_id} not found on CalDAV server")
                return None

            event_uid = str(uuid.uuid4())
            ical = ICalendar()
            ical.add("prodid", "-//ICS-Gate//")
            ical.add("version", "2.0")

            vevent = IEvent()
            vevent.add("uid", event_uid)
            vevent.add("summary", summary)
            if description:
                vevent.add("description", description)
            if location:
                vevent.add("location", location)

            if all_day:
                vevent.add("dtstart", start.date())
                vevent.add("dtend", end.date() if end else start.date())
            else:
                vevent.add("dtstart", start)
                vevent.add("dtend", end)

            ical.add_component(vevent)
            target.save_event(ical.to_ical())

            logger.info(
                f"Created event {event_uid} in CalDAV calendar {self.calendar_url}"
            )
            return event_uid
        except caldav.error.AuthorizationError as e:
            logger.error(
                f"Authorization denied for CalDAV calendar {self.calendar_url}: {e}"
            )
            raise PermissionError(
                "Editing is not allowed for this calendar — the calendar is likely imported (read-only)"
            )
        except Exception as e:
            logger.error(
                f"Error creating event in CalDAV calendar {self.calendar_url}: {e}"
            )
            return None
