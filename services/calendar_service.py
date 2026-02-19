import logging
from entity.base import Calendar
from services.database import Database
from services.ics_parser import download_ics_content, calculate_content_hash, parse_ics_content
logger = logging.getLogger(__name__)
logger.info("Starting calendar synchronization")

class CalendarService:
    def __init__(self, database: Database, tzone: str = None):
        self.db = database
        self.users = self.db.getUser()
        self.events = self.db.getEvent()
        self.calendars = self.db.getCalendar()
        self.tzone = tzone

    def create_user(self, user_id: str) -> bool:
        """Create a new user"""
        return self.users.create_user(user_id)
    
    def create_calendar(self, user_id: str, url: str) -> bool:
        """Create a new calendar"""
        return self.calendars.create_calendar(user_id, url)
    
    def get_calendar_by_id(self, calendar_id: str):
        """Get a calendar by ID"""
        return self.calendars.get_calendar_by_id(calendar_id)

    def sync_all_calendars(self):
        """Sync all calendars"""
        logger.info("Starting calendar synchronization")
        
        calendars = self.calendars.get_calendars()
        success_count = 0
        
        for calendar in calendars:
            if self.sync_calendar(calendar):
                success_count += 1
        
        logger.info(f"Calendar synchronization complete: {success_count}/{len(calendars)} successful")

        return success_count == len(calendars)
    
    def sync_calendar(self, calendar: Calendar) -> bool:
        """Sync a single calendar using upsert logic"""
        try:
            logger.info(f"Syncing calendar {calendar.id} from {calendar.url}")
            
            # Download ICS content
            ics_content = download_ics_content(calendar.url)
            
            # Calculate hash to detect changes
            content_hash = calculate_content_hash(ics_content)
            
            # Skip if no changes
            if calendar.sync_hash == content_hash:
                logger.info(f"Calendar {calendar.id} unchanged, skipping")
                return True
            
            # Parse events
            events = parse_ics_content(ics_content, self.tzone)
            
            # Get existing event UIDs for this calendar
            existing_uids = self.calendars.get_existing_event_uids(calendar.id)
            
            # Track which events we're updating/inserting
            updated_uids = set()
            
            # Upsert events
            for event_data in events:
                uid = event_data['uid']
                updated_uids.add(uid)
                
                # Upsert event using EventEntity
                self.events.upsert_event(
                    calendar.id, uid, event_data['summary'], event_data['description'],
                    event_data['location'], event_data['start'], event_data['end'],
                    event_data['all_day']
                )
                logger.info(f"Upserted event {uid} for calendar {calendar.id}")
            
            # Delete events that no longer exist in the calendar
            deleted_uids = existing_uids - updated_uids
            self.events.delete_events_by_uids(calendar.id, deleted_uids)
            
            # Update sync metadata
            self.calendars.update_calendar_sync(calendar.id, content_hash)
            
            logger.info(f"Synced calendar {calendar.id}: {len(events)} events, {len(deleted_uids)} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing calendar {calendar.id}: {e}")
            return False
    
    def sync_calendar_by_id(self, calendar_id: str) -> bool:
        """Sync a specific calendar by ID"""
        try:
            calendar = self.calendars.get_calendar_by_id(calendar_id)
            if not calendar:
                logger.error(f"Calendar with ID {calendar_id} not found")
                return False
            
            return self.sync_calendar(calendar)
            
        except Exception as e:
            logger.error(f"Error syncing calendar {calendar_id}: {e}")
            return False
