import sqlite3
import logging
from datetime import datetime
from typing import List, Optional
from entity.base import BaseCalendarEntity, Calendar, User
from entity.sqlite.user_entity import UserEntity

# Configure logging
logger = logging.getLogger(__name__)


class CalendarEntity(BaseCalendarEntity):
    """SQLite implementation for calendar-related database operations"""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.user_entity = UserEntity(db_connection)
    
    def create_calendar(self, user_id: str, url: str) -> Calendar:
        """Create a new calendar for a user"""
        cursor = self.db_connection.cursor()
        
        # Extract user ID if it's a User object
        if hasattr(user_id, 'id'):
            user_id = user_id.id

        try:
            cursor.execute(
                'INSERT INTO calendars (user_id, url) VALUES (?, ?)',
                (user_id, url)
            )
            self.db_connection.commit()
            calendar_id = cursor.lastrowid
            logger.info(f"Created calendar {calendar_id} for user {user_id}")
            calendar = Calendar(calendar_id, user_id, url, None, None, 'GMT+3')
        except sqlite3.IntegrityError as e:
            # Handle duplicate calendar entry
            self.db_connection.rollback()
            logger.warning(f"Calendar for user {user_id} with URL {url} already exists: {e}")
            cursor.execute(
                'SELECT * FROM calendars WHERE user_id = ? AND url = ?',
                (user_id, url)
            )
            row = cursor.fetchone()
            if row:
                calendar = Calendar(row['id'], row['user_id'], row['url'],
                                  row['last_sync_at'], row['sync_hash'],
                                  row['timezone'] if 'timezone' in row.keys() else 'GMT+3')
            else:
                raise Exception("Failed to retrieve existing calendar")
        
        return calendar
    
    def get_calendars(self, user_id: str = None) -> List[Calendar]:
        """Get all calendars, optionally filtered by user_id"""
        cursor = self.db_connection.cursor()
        
        if user_id:
            # First get the user's internal ID
            user_internal_id = self.user_entity.get_user_id_by_external_id(user_id)
            if not user_internal_id:
                raise ValueError(f"User {user_id} not found")
            
            cursor.execute('SELECT * FROM calendars WHERE user_id = ?', (user_internal_id,))
        else:
            cursor.execute('SELECT * FROM calendars')
        
        rows = cursor.fetchall()
        
        return [Calendar(row['id'], row['user_id'], row['url'],
                         row['last_sync_at'], row['sync_hash'],
                         row['timezone'] if 'timezone' in row.keys() else 'GMT+3') for row in rows]
    
    def delete_calendar(self, calendar_id: str, user_id: str = None) -> bool:
        """Delete a calendar by ID, optionally checking user ownership"""
        cursor = self.db_connection.cursor()
        
        if user_id:
            # First get the user's internal ID
            user_internal_id = self.user_entity.get_user_id_by_external_id(user_id)
            if not user_internal_id:
                raise ValueError(f"User {user_id} not found")
            
            # Delete only if the calendar belongs to this user
            cursor.execute('DELETE FROM calendars WHERE id = ? AND user_id = ?', (calendar_id, user_internal_id))
        else:
            # Delete any calendar (admin access)
            cursor.execute('DELETE FROM calendars WHERE id = ?', (calendar_id,))
        
        deleted = cursor.rowcount > 0
        self.db_connection.commit()
        
        return deleted
    
    def get_calendar_by_id(self, calendar_id: str) -> Calendar:
        """Get a specific calendar by ID"""
        cursor = self.db_connection.cursor()
        
        cursor.execute('SELECT * FROM calendars WHERE id = ?', (calendar_id,))
        row = cursor.fetchone()
        
        if row:
            return Calendar(row['id'], row['user_id'], row['url'],
                          row['last_sync_at'], row['sync_hash'],
                          row['timezone'] if 'timezone' in row.keys() else 'GMT+3')
        else:
            return None
    
    def update_calendar_sync(self, calendar_id: str, sync_hash: str):
        """Update calendar sync metadata"""
        cursor = self.db_connection.cursor()
        
        cursor.execute(
            'UPDATE calendars SET last_sync_at = ?, sync_hash = ? WHERE id = ?',
            (datetime.now().isoformat(), sync_hash, calendar_id)
        )
        self.db_connection.commit()
        
        logger.info(f"Updated sync metadata for calendar {calendar_id}")
    
    def get_existing_event_uids(self, calendar_id: str) -> set:
        """Get existing event UIDs for a calendar"""
        cursor = self.db_connection.cursor()
        
        cursor.execute('SELECT uid FROM events WHERE calendar_id = ?', (calendar_id,))
        existing_uids = {row[0] for row in cursor.fetchall()}
        
        return existing_uids