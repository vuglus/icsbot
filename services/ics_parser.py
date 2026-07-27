import logging
import hashlib
from datetime import datetime
from typing import List, Dict
from icalendar import Calendar as ICalendar
from dateutil import tz
import requests

logger = logging.getLogger(__name__)

TIMEZONE_DEFAULT = "UTC"


class IcsEvent:
    def __init__(
        self,
        uid: str,
        summary: str,
        description: str,
        location: str,
        start: str,
        end: str,
        all_day: bool = False,
    ):
        self.uid = uid
        self.summary = summary
        self.description = description
        self.location = location
        self.start = start
        self.end = end
        self.all_day = all_day


def parse_ics_content(
    ics_content: str, tzone: str = TIMEZONE_DEFAULT
) -> List[IcsEvent]:
    try:
        cal = ICalendar.from_ical(ics_content)
        events = []

        for component in cal.walk():
            if component.name == "VEVENT":
                uid = str(component.get("uid", ""))
                summary = str(component.get("summary", ""))
                description = str(component.get("description", ""))
                location = str(component.get("location", ""))
                start = (
                    component.get("dtstart").dt if component.get("dtstart") else None
                )
                end = component.get("dtend").dt if component.get("dtend") else None
                duration = (
                    component.get("duration") if component.get("duration") else None
                )
                all_day = False

                if start and hasattr(start, "date"):
                    all_day = True

                if start:
                    if isinstance(start, datetime):
                        if start.tzinfo is None:
                            start = start.replace(tzinfo=tz.gettz(tzone))
                        start = start.isoformat()
                    else:
                        start = start.isoformat()

                if end:
                    if isinstance(end, datetime):
                        if end.tzinfo is None:
                            end = end.replace(tzinfo=tz.gettz(tzone))
                        end = end.isoformat()
                    else:
                        end = end.isoformat()
                elif duration and start:
                    from datetime import timedelta

                    if isinstance(start, str):
                        from dateutil import parser

                        start_dt = parser.parse(start)
                    else:
                        start_dt = start
                    end_dt = start_dt + duration.dt
                    end = end_dt.isoformat()
                elif not end and start:
                    end = start

                events.append(
                    IcsEvent(
                        uid=uid,
                        summary=summary,
                        description=description,
                        location=location,
                        start=start,
                        end=end,
                        all_day=all_day,
                    )
                )

        logger.info(f"Parsed {len(events)} events from ICS content")
        return events
    except Exception as e:
        logger.error(f"Error parsing ICS content: {e}")
        return []


def download_ics_content(url: str) -> str:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Error downloading ICS content from {url}: {e}")
        raise
