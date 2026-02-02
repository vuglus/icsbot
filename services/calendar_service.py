import logging
from typing import List
from .database import get_calendars, create_calendar as db_create_calendar, update_calendar_sync
from .ics_parser import download_ics_content, parse_ics_content, calculate_content_hash
from .database import create_event, Calendar

# Configure logging
logger = logging.getLogger(__name__)

def sync_calendar(calendar: Calendar) -> bool:
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
        events = parse_ics_content(ics_content)
        
        # Update database
        from .database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get existing event UIDs for this calendar
        cursor.execute('SELECT uid FROM events WHERE calendar_id = ?', (calendar.id,))
        existing_uids = {row[0] for row in cursor.fetchall()}
        
        # Track which events we're updating/inserting
        updated_uids = set()
        
        # Upsert events
        for event_data in events:
            uid = event_data['uid']
            updated_uids.add(uid)
            
            # Try to update existing event
            cursor.execute('''
                UPDATE events
                SET title = ?, description = ?, location = ?,
                    start_datetime = ?, end_datetime = ?, all_day = ?
                WHERE calendar_id = ? AND uid = ?
            ''', (event_data['summary'], event_data['description'],
                  event_data['location'], event_data['start'],
                  event_data['end'], event_data['all_day'],
                  calendar.id, uid))
            
            # If no rows were affected, insert new event
            if cursor.rowcount == 0:
                cursor.execute('''
                    INSERT INTO events (calendar_id, uid, title, description, location,
                                       start_datetime, end_datetime, all_day)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (calendar.id, uid, event_data['summary'],
                      event_data['description'], event_data['location'],
                      event_data['start'], event_data['end'], event_data['all_day']))
        
        # Delete events that no longer exist in the calendar
        deleted_uids = existing_uids - updated_uids
        if deleted_uids:
            placeholders = ','.join('?' * len(deleted_uids))
            cursor.execute(f'''
                DELETE FROM events
                WHERE calendar_id = ? AND uid IN ({placeholders})
            ''', (calendar.id, *deleted_uids))
        
        conn.commit()
        conn.close()
        
        # Update sync metadata
        update_calendar_sync(calendar.id, content_hash)
        
        logger.info(f"Synced calendar {calendar.id}: {len(events)} events, {len(deleted_uids)} deleted")
        return True
        
    except Exception as e:
        logger.error(f"Error syncing calendar {calendar.id}: {e}")
        return False

def sync_all_calendars():
    """Sync all calendars"""
    logger.info("Starting calendar synchronization")
    
    calendars = get_calendars()
    success_count = 0
    
    for calendar in calendars:
        if sync_calendar(calendar):
            success_count += 1
    
    logger.info(f"Calendar synchronization complete: {success_count}/{len(calendars)} successful")

def create_calendar(user_id: int, url: str) -> Calendar:
    """Create a new calendar for a user"""
    return db_create_calendar(user_id, url)