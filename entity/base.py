import abc
from typing import List, Optional
from datetime import datetime


class User:
    def __init__(self, id: str, user_id: str, created_at: str):
        self.id = id
        self.user_id = user_id
        self.created_at = created_at


class Calendar:
    def __init__(self, id: str, user_id: str, url: str, last_sync_at: str, sync_hash: str, timezone: str = 'GMT+3'):
        self.id = id
        self.user_id = user_id
        self.url = url
        self.last_sync_at = last_sync_at
        self.sync_hash = sync_hash
        self.timezone = timezone


class Event:
    def __init__(self, id: int, calendar_id: str, uid: str, title: str, description: str,
                 location: str, start_datetime: str, end_datetime: str, all_day: bool, notified: bool, 
                 user_id: str = None, calendar_timezone: str = None):
        self.id = id
        self.calendar_id = calendar_id
        self.uid = uid
        self.title = title
        self.description = description
        self.location = location
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.all_day = all_day
        self.notified = notified
        self.user_id = user_id
        self.calendar_timezone = calendar_timezone


class Migration:
    def __init__(self, id: str, name: str, executed_at: str):
        self.id = id
        self.name = name
        self.executed_at = executed_at


class BaseMigrationEntity(abc.ABC):
    """Base interface for migration-related database operations"""
    
    @abc.abstractmethod
    def create_migration_table(self):
        """Create the migrations table"""
        pass
    
    @abc.abstractmethod
    def get_executed_migrations(self) -> list:
        """Get list of executed migrations"""
        pass
    
    @abc.abstractmethod
    def record_migration(self, name: str):
        """Record a migration as executed"""
        pass
    
    @abc.abstractmethod
    def is_migration_executed(self, name: str) -> bool:
        """Check if a migration has been executed"""
        pass


class BaseUserEntity(abc.ABC):
    """Base interface for user-related database operations"""
    
    @abc.abstractmethod
    def create_user(self, user_id: str) -> User:
        """Create a new user"""
        pass
    
    @abc.abstractmethod
    def get_user_id_by_external_id(self, external_user_id: str) -> int:
        """Get internal user ID by external user ID"""
        pass
    
    @abc.abstractmethod
    def get_users_with_calendars(self) -> list:
        """Get users who have calendars"""
        pass
    
    @abc.abstractmethod
    def get_users_with_pending_events(self) -> list:
        """Get users who have pending events"""
        pass


class BaseCalendarEntity(abc.ABC):
    """Base interface for calendar-related database operations"""
    
    @abc.abstractmethod
    def create_calendar(self, user_id: str, url: str) -> Calendar:
        """Create a new calendar for a user"""
        pass
    
    @abc.abstractmethod
    def get_calendars(self, user_id: str = None) -> List[Calendar]:
        """Get all calendars, optionally filtered by user_id"""
        pass
    
    @abc.abstractmethod
    def delete_calendar(self, calendar_id: str, user_id: str = None) -> bool:
        """Delete a calendar by ID, optionally checking user ownership"""
        pass
    
    @abc.abstractmethod
    def get_calendar_by_id(self, calendar_id: str) -> Calendar:
        """Get a specific calendar by ID"""
        pass
    
    @abc.abstractmethod
    def update_calendar_sync(self, calendar_id: str, sync_hash: str):
        """Update calendar sync metadata"""
        pass
    
    @abc.abstractmethod
    def get_existing_event_uids(self, calendar_id: str) -> set:
        """Get existing event UIDs for a calendar"""
        pass


class BaseEventEntity(abc.ABC):
    """Base interface for event-related database operations"""
    
    @abc.abstractmethod
    def get_pending_events(self, user_id: str = None) -> List[Event]:
        """Get events that need to be notified"""
        pass
    
    @abc.abstractmethod
    def mark_event_notified(self, event_id: str) -> bool:
        """Mark an event as notified"""
        pass
    
    @abc.abstractmethod
    def upsert_event(self, calendar_id: str, uid: str, title: str, description: str,
                     location: str, start_datetime: str, end_datetime: str, all_day: bool):
        """Upsert an event (update if exists, insert if not)"""
        pass
    
    @abc.abstractmethod
    def delete_events_by_uids(self, calendar_id: str, deleted_uids: set):
        """Delete events by UIDs"""
        pass
