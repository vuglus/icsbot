import sqlite3
import logging
from typing import List
from entity.base import BaseEventEntity, Event, User, Calendar
from entity.sqlite.user_entity import UserEntity
from entity.sqlite.calendar_entity import CalendarEntity

# Configure logging
logger = logging.getLogger(__name__)


class EventEntity(BaseEventEntity):
    """SQLite implementation for event-related database operations"""
    
    def __init__(self, db_connection, notify_before_minutes: int):
        self.db_connection = db_connection
        self.user_entity = UserEntity(db_connection)
        self.calendar_entity = CalendarEntity(db_connection)
        self.notify_before_minutes = notify_before_minutes
    
    def create_event(self, calendar_id: int, uid: str, title: str, description: str,
                     location: str, start_datetime: str = None, end_datetime: str = None,
                     all_day: bool = False, **kwargs) -> Event:
        """Create a new event"""
        # Handle both parameter names
        if 'start_time' in kwargs:
            start_datetime = kwargs['start_time']
        if 'end_time' in kwargs:
            end_datetime = kwargs['end_time']
            
        cursor = self.db_connection.cursor()
        
        # Extract calendar ID if it's a Calendar object
        if hasattr(calendar_id, 'id'):
            calendar_id = calendar_id.id

        cursor.execute('''
            INSERT INTO events (calendar_id, uid, title, description, location,
                               start_datetime, end_datetime, all_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (calendar_id, uid, title, description, location,
              start_datetime, end_datetime, all_day))
        
        self.db_connection.commit()
        event_id = cursor.lastrowid
        print(f"Created event {event_id} for calendar {calendar_id}")  # Debug output
        
        logger.info(f"Created event {event_id} for calendar {calendar_id}")
        return Event(event_id, calendar_id, uid, title, description, location,
                     start_datetime, end_datetime, all_day, False)
    
    def get_pending_events(self, user_id: str = None) -> List[Event]:
        """Get events that need to be notified"""
        cursor = self.db_connection.cursor()
        
        cursor.execute('''
            SELECT e.*, u.user_id as user_id, c.timezone as calendar_timezone FROM events e
            JOIN calendars c ON e.calendar_id = c.id
            JOIN users u ON c.user_id = u.id
            WHERE e.notified = FALSE
            AND julianday(e.start_datetime) <= julianday(datetime('now')) + (? / 1440.0)
            AND julianday(e.start_datetime) > julianday(datetime('now'))
            AND u.user_id = ?
            ORDER BY e.start_datetime ASC
        ''', (self.notify_before_minutes, user_id))        
        
        rows = cursor.fetchall()
        
        # Debug output
        print(f"Found {len(rows)} pending events")
        for row in rows:
            print(f"  - Event: {row['title']} at {row['start_datetime']}")
        
        events = []
        for row in rows:
            event = Event(row['id'], row['calendar_id'], row['uid'], row['title'],
                          row['description'], row['location'], row['start_datetime'],
                          row['end_datetime'], row['all_day'], row['notified'],
                          row['user_id'] if 'user_id' in row.keys() else None,
                          row['calendar_timezone'] if 'calendar_timezone' in row.keys() else None)
            events.append(event)
        
        return events
    
    def mark_event_notified(self, event_id: int) -> bool:
        """Mark an event as notified"""
        cursor = self.db_connection.cursor()
        
        cursor.execute(
            'UPDATE events SET notified = TRUE WHERE id = ? AND notified = FALSE',
            (event_id,)
        )
        
        updated = cursor.rowcount > 0
        self.db_connection.commit()
        
        if updated:
            logger.info(f"Marked event {event_id} as notified")
        else:
            logger.warning(f"Event {event_id} not found or already notified")
        
        return updated
    
    def upsert_event(self, calendar_id: int, uid: str, title: str, description: str,
                     location: str, start_datetime: str, end_datetime: str, all_day: bool):
        """Upsert an event (update if exists, insert if not)"""
        cursor = self.db_connection.cursor()
        
        # Try to update existing event
        cursor.execute('''
            UPDATE events
            SET title = ?, description = ?, location = ?,
                start_datetime = ?, end_datetime = ?, all_day = ?
            WHERE calendar_id = ? AND uid = ?
        ''', (title, description, location, start_datetime, end_datetime, all_day,
              calendar_id, uid))
        
        # If no rows were affected, insert new event
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO events (calendar_id, uid, title, description, location,
                                   start_datetime, end_datetime, all_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (calendar_id, uid, title, description, location,
                  start_datetime, end_datetime, all_day))
        
        self.db_connection.commit()
    
    def delete_events_by_uids(self, calendar_id: int, deleted_uids: set):
        """Delete events by UIDs"""
        if not deleted_uids:
            return
        
        cursor = self.db_connection.cursor()
        
        placeholders = ','.join('?' * len(deleted_uids))
        cursor.execute(f'''
            DELETE FROM events
            WHERE calendar_id = ? AND uid IN ({placeholders})
        ''', (calendar_id, *deleted_uids))
        
        self.db_connection.commit()