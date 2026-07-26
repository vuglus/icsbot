import logging
import ydb
import uuid
from datetime import datetime
from typing import List, Optional
from entity.base import BaseCalendarEntity, Calendar, User
from entity.ydb.user_entity import UserEntity

# Configure logging
logger = logging.getLogger(__name__)


class CalendarEntity(BaseCalendarEntity):
    """YDB implementation for calendar-related database operations"""
    
    def __init__(self, session_pool, user_entity):
        self.session_pool = session_pool
        self.user_entity = user_entity
    
    def create_calendar(self, user_id: str, url: str) -> Calendar:
        """Create a new calendar for a user"""
        def callee(session):

            calendar = self.get_calendar_by_user_id_and_url(user_id, url)
            if calendar is not None:
                return calendar
            
            id = uuid.uuid4().hex

            # First try to insert the calendar
            query = """
            DECLARE $id AS Utf8;
            DECLARE $user_id AS Utf8;
            DECLARE $url AS Utf8;
            UPSERT INTO calendars (id, user_id, url, timezone) VALUES ($id, $user_id, $url, 'GMT+3');
            """
            prepared_query = session.prepare(query)
            session.transaction().execute(
                prepared_query,
                parameters={"$id": id, "$user_id": user_id, "$url": url},
                commit_tx=True,
            )

            return self.get_calendar_by_user_id_and_url(user_id, url)
        
        return self.session_pool.retry_operation_sync(callee)
    
    def get_calendar_by_user_id_and_url(self, user_id: str, url: str) -> Optional[Calendar]:
        """Get a calendar by user_id and url"""
        def callee(session):
                        # Then retrieve the calendar to get the ID
            query = """
            DECLARE $user_id AS Utf8;
            DECLARE $url AS Utf8;
            SELECT id, user_id, url, last_sync_at, sync_hash, timezone FROM calendars 
            WHERE user_id = $user_id AND url = $url;
            """
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters={"$user_id": user_id, "$url": url},
                commit_tx=True,
            )
            
            if result[0].rows:
                row = result[0].rows[0]
                return Calendar(
                    row.id, 
                    row.user_id, 
                    row.url,
                    str(row.last_sync_at) if row.last_sync_at else None,
                    row.sync_hash,
                    row.timezone
                )

        return self.session_pool.retry_operation_sync(callee)

    
    def get_calendars(self, user_id: str = None) -> List[Calendar]:
        """Get all calendars, optionally filtered by user_id"""
        def callee(session):
            if user_id:
                # First get the user's internal ID
                user_internal_id = self.user_entity.get_user_id_by_external_id(user_id)
                if not user_internal_id:
                    raise ValueError(f"User {user_id} not found")
                
                query = """
                DECLARE $user_id AS Utf8;
                SELECT id, user_id, url, last_sync_at, sync_hash, timezone FROM calendars 
                WHERE user_id = $user_id;
                """
                prepared_query = session.prepare(query)
                result = session.transaction().execute(
                    prepared_query,
                    parameters={"$user_id": user_internal_id},
                    commit_tx=True,
                )
            else:
                query = """
                SELECT id, user_id, url, last_sync_at, sync_hash, timezone FROM calendars;
                """
                prepared_query = session.prepare(query)
                result = session.transaction().execute(
                    prepared_query,
                    commit_tx=True,
                )
            
            calendars = []
            for row in result[0].rows:
                calendar = Calendar(
                    row.id,
                    row.user_id,
                    row.url,
                    str(row.last_sync_at) if row.last_sync_at else None,
                    row.sync_hash,
                    row.timezone
                )
                calendars.append(calendar)
            
            return calendars
        
        return self.session_pool.retry_operation_sync(callee)
    
    def delete_calendar(self, calendar_id: str, user_id: str = None) -> bool:
        """Delete a calendar by ID, optionally checking user ownership"""
        def callee(session):
            if user_id:
                # First get the user's internal ID
                user_internal_id = self.user_entity.get_user_id_by_external_id(user_id)
                if not user_internal_id:
                    raise ValueError(f"User {user_id} not found")
                
                # Delete only if the calendar belongs to this user
                query = """
                DECLARE $id AS Utf8;
                DECLARE $user_id AS Utf8;
                DELETE FROM calendars WHERE id = $id AND user_id = $user_id;
                """
                prepared_query = session.prepare(query)
                result = session.transaction().execute(
                    prepared_query,
                    parameters={"$id": calendar_id, "$user_id": user_internal_id},
                    commit_tx=True,
                )
            else:
                # Delete any calendar (admin access)
                query = """
                DECLARE $id AS Utf8;
                DELETE FROM calendars WHERE id = $id;
                """
                prepared_query = session.prepare(query)
                result = session.transaction().execute(
                    prepared_query,
                    parameters={"$id": calendar_id},
                    commit_tx=True,
                )
            
            # YDB doesn't return row count, so we'll check if the calendar exists after deletion
            check_query = """
            DECLARE $id AS Utf8;
            SELECT id FROM calendars WHERE id = $id;
            """
            check_prepared = session.prepare(check_query)
            check_result = session.transaction().execute(
                check_prepared,
                parameters={"$id": calendar_id},
                commit_tx=True,
            )
            
            return len(check_result[0].rows) == 0
        
        return self.session_pool.retry_operation_sync(callee)
    
    def get_calendar_by_id(self, calendar_id: str) -> Calendar:
        """Get a specific calendar by ID"""
        def callee(session):
            query = """
            DECLARE $id AS Utf8;
            SELECT id, user_id, url, last_sync_at, sync_hash, timezone FROM calendars 
            WHERE id = $id;
            """
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters={"$id": calendar_id},
                commit_tx=True,
            )
            
            if result[0].rows:
                row = result[0].rows[0]
                return Calendar(
                    row.id,
                    row.user_id,
                    row.url,
                    str(row.last_sync_at) if row.last_sync_at else None,
                    row.sync_hash,
                    row.timezone
                )
            else:
                return None
        
        return self.session_pool.retry_operation_sync(callee)
    
    def update_calendar_sync(self, calendar_id: str, sync_hash: str):
        """Update calendar sync metadata"""
        def callee(session):
            query = """
            DECLARE $id AS Utf8;
            DECLARE $sync_hash AS Utf8;
            UPDATE calendars SET last_sync_at = CurrentUtcTimestamp(), sync_hash = $sync_hash 
            WHERE id = $id;
            """
            prepared_query = session.prepare(query)
            session.transaction().execute(
                prepared_query,
                parameters={"$id": calendar_id, "$sync_hash": sync_hash},
                commit_tx=True,
            )
            
            logger.info(f"Updated sync metadata for calendar {calendar_id}")
        
        return self.session_pool.retry_operation_sync(callee)
    
    def get_existing_event_uids(self, calendar_id: str) -> set:
        """Get existing event UIDs for a calendar"""
        def callee(session):
            query = """
            DECLARE $calendar_id AS Utf8;
            SELECT uid FROM events WHERE calendar_id = $calendar_id;
            """
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters={"$calendar_id": calendar_id},
                commit_tx=True,
            )
            
            return {row.uid for row in result[0].rows}
        
        return self.session_pool.retry_operation_sync(callee)