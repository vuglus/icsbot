import logging
import ydb
import uuid
from typing import List
from entity.base import BaseEventEntity, Event, User, Calendar
from entity.ydb.user_entity import UserEntity
from entity.ydb.calendar_entity import CalendarEntity
import pytz

# Configure logging
logger = logging.getLogger(__name__)


class EventEntity(BaseEventEntity):
    """YDB implementation for event-related database operations"""
    
    def __init__(self, driver, session_pool, notify_before_minutes: int, user_entity: UserEntity, calendar_entity: CalendarEntity):
        self.driver = driver
        self.session_pool = session_pool
        self.user_entity = user_entity
        self.calendar_entity = calendar_entity
        self.notify_before_minutes = notify_before_minutes
    
    def get_calendar_event_by_uid(self, calendar_id: str, uid: str) -> Event: 
        """Create a new event"""
        def callee(session):
            # Retrieve the created event to get the ID
            query = """
            DECLARE $calendar_id AS Utf8;
            DECLARE $uid AS Utf8;
            SELECT id, calendar_id, uid, title, description, location, 
                    start_datetime, end_datetime, all_day, notified
            FROM events WHERE calendar_id = $calendar_id AND uid = $uid;
            """
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters={"$calendar_id": calendar_id, "$uid": uid},
                commit_tx=True,
            )
            
            if result[0].rows:
                row = result[0].rows[0]
                return Event(
                    row.id, row.calendar_id, row.uid, row.title,
                    row.description, row.location, row.start_datetime,
                    row.end_datetime, row.all_day, row.notified
                )
            
            return None
        
        return self.session_pool.retry_operation_sync(callee)

    
    def get_pending_events(self, user_id: str) -> List[Event]:
        """Get events that need to be notified"""
        def callee(session):
            # First check if user exists
            user_internal_id = self.user_entity.get_user_id_by_external_id(user_id)
            if not user_internal_id:
                raise ValueError(f"User {user_id} not found")
            
            # Calculate date range in code
            from datetime import datetime, timedelta
            import pytz
            
            # Get current time in UTC
            now_utc = datetime.utcnow()
            # Calculate the time window (from now to now + notify_before_minutes)
            future_time = now_utc + timedelta(minutes=self.notify_before_minutes)
            
            # Format dates for logging and query parameters
            now_utc_str = now_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            future_time_str = future_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            logger.info(f"Checking pending events from {now_utc_str} to {future_time_str}")
            
            query = """
            DECLARE $user_id AS Utf8;
            DECLARE $now AS Utf8;
            DECLARE $future_time AS Utf8;
            SELECT e.*, u.user_id as user_id, c.timezone as calendar_timezone
            FROM events e
            JOIN calendars c ON e.calendar_id = c.id
            JOIN users u ON c.user_id = u.id
            WHERE e.notified = false
            AND start_datetime <= $future_time
            AND start_datetime > $now
            AND u.user_id = $user_id
            ORDER BY start_datetime ASC;
            """
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters={
                    "$user_id": user_id,
                    "$now": now_utc_str,
                    "$future_time": future_time_str
                },
                commit_tx=True,
            )
            
            events = []
            for row in result[0].rows:
                event = Event(
                    row.id, row.calendar_id, row.uid, row.title,
                    row.description, row.location, row.start_datetime,
                    row.end_datetime, row.all_day, row.notified,
                    row.user_id if hasattr(row, 'user_id') else None,
                    row.calendar_timezone if hasattr(row, 'calendar_timezone') else None
                )
                events.append(event)
            
            return events
        
        return self.session_pool.retry_operation_sync(callee)
    
    def mark_event_notified(self, event_id: int) -> bool:
        """Mark an event as notified"""
        def callee(session):
            # Update the event
            query = """
            DECLARE $id AS Utf8;
            UPDATE events SET notified = true WHERE id = $id AND notified = false;
            """
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters={"$id": event_id},
                commit_tx=True,
            )
            
            # Check if the event was updated
            check_query = """
            DECLARE $id AS Utf8;
            SELECT id FROM events WHERE id = $id AND notified = true;
            """
            check_prepared = session.prepare(check_query)
            check_result = session.transaction().execute(
                check_prepared,
                parameters={"$id": event_id},
                commit_tx=True,
            )
            
            updated = len(check_result[0].rows) > 0
            
            if updated:
                logger.info(f"Marked event {event_id} as notified")
            else:
                logger.warning(f"Event {event_id} not found or already notified")
            
            return updated
        
        return self.session_pool.retry_operation_sync(callee)
    
    def upsert_event(self, calendar_id: str, uid: str, title: str, description: str,
                     location: str, start_datetime: str, end_datetime: str, all_day: bool):
        """Upsert an event (update if exists, insert if not)"""
        def callee(session):
            event = self.get_calendar_event_by_uid(calendar_id, uid)
            id = event.id if event else uuid.uuid4().hex
            # For YDB, we can use UPSERT which will insert or update
            query = """
            DECLARE $id AS Utf8;
            DECLARE $calendar_id AS Utf8;
            DECLARE $uid AS Utf8;
            DECLARE $title AS Utf8;
            DECLARE $description AS Utf8;
            DECLARE $location AS Utf8;
            DECLARE $start_datetime AS Utf8;
            DECLARE $end_datetime AS Utf8;
            DECLARE $all_day AS Bool;
            UPSERT INTO events (id, calendar_id, uid, title, description, location, 
                               start_datetime, end_datetime, all_day, notified)
            VALUES ($id, $calendar_id, $uid, $title, $description, $location, 
                    $start_datetime, $end_datetime, $all_day, false);
            """
            prepared_query = session.prepare(query)
            session.transaction().execute(
                prepared_query,
                parameters={
                    "$id": id,
                    "$calendar_id": calendar_id,
                    "$uid": uid,
                    "$title": title,
                    "$description": description,
                    "$location": location,
                    "$start_datetime": start_datetime,
                    "$end_datetime": end_datetime,
                    "$all_day": all_day
                },
                commit_tx=True,
            )
        
        return self.session_pool.retry_operation_sync(callee)
    
    def delete_events_by_uids(self, calendar_id: str, deleted_uids: set):
        """Delete events by UIDs"""
        if not deleted_uids:
            return
        
        def callee(session):
            # Delete events with specified UIDs for the calendar
            placeholders = ','.join(['?' for _ in deleted_uids])
            query = f"""
            DECLARE $calendar_id AS Utf8;
            DECLARE $uids AS List<Utf8>;
            DELETE FROM events WHERE calendar_id = $calendar_id AND uid IN $uids;
            """
            prepared_query = session.prepare(query)
            session.transaction().execute(
                prepared_query,
                parameters={
                    "$calendar_id": calendar_id,
                    "$uids": list(deleted_uids)
                },
                commit_tx=True,
            )
        
        return self.session_pool.retry_operation_sync(callee)