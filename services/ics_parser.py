import logging
import hashlib
from datetime import datetime
from typing import List, Dict
from icalendar import Calendar as ICalendar
from dateutil import tz
import requests

# Configure logging
logger = logging.getLogger(__name__)

# Global variables
TIMEZONE_DEFAULT = None  # This will be set from the main app

def parse_ics_content(ics_content: str) -> List[Dict]:
    """Parse ICS content and extract events"""
    try:
        cal = ICalendar.from_ical(ics_content)
        events = []
        
        for component in cal.walk():
            if component.name == "VEVENT":
                event = {
                    'uid': str(component.get('uid', '')),
                    'summary': str(component.get('summary', '')),
                    'description': str(component.get('description', '')),
                    'location': str(component.get('location', '')),
                    'start': component.get('dtstart').dt if component.get('dtstart') else None,
                    'end': component.get('dtend').dt if component.get('dtend') else None,
                    'duration': component.get('duration') if component.get('duration') else None,
                    'all_day': False
                }
                
                # Handle all-day events
                if event['start'] and hasattr(event['start'], 'date'):
                    event['all_day'] = True
                
                # Convert datetime to string
                if event['start']:
                    if isinstance(event['start'], datetime):
                        # Make timezone aware if not already
                        if event['start'].tzinfo is None:
                            event['start'] = event['start'].replace(tzinfo=tz.gettz(TIMEZONE_DEFAULT))
                        event['start'] = event['start'].isoformat()
                    else:
                        event['start'] = event['start'].isoformat()
                
                if event['end']:
                    if isinstance(event['end'], datetime):
                        # Make timezone aware if not already
                        if event['end'].tzinfo is None:
                            event['end'] = event['end'].replace(tzinfo=tz.gettz(TIMEZONE_DEFAULT))
                        event['end'] = event['end'].isoformat()
                    else:
                        event['end'] = event['end'].isoformat()
                elif event['duration'] and event['start']:
                    # Calculate end datetime based on duration
                    from datetime import timedelta
                    if isinstance(event['start'], str):
                        # Parse the start datetime string
                        from dateutil import parser
                        start_dt = parser.parse(event['start'])
                    else:
                        start_dt = event['start']
                    
                    # Calculate end datetime
                    end_dt = start_dt + event['duration'].dt
                    event['end'] = end_dt.isoformat()
                elif not event['end'] and event['start']:
                    # If end datetime is still missing, set it to start datetime
                    event['end'] = event['start']
                
                events.append(event)
        
        logger.info(f"Parsed {len(events)} events from ICS content")
        return events
    except Exception as e:
        logger.error(f"Error parsing ICS content: {e}")
        return []

def download_ics_content(url: str) -> str:
    """Download ICS content from a URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Error downloading ICS content from {url}: {e}")
        raise

def calculate_content_hash(content: str) -> str:
    """Calculate MD5 hash of content"""
    return hashlib.md5(content.encode()).hexdigest()