import logging
import ydb
import uuid
from datetime import datetime
from typing import Optional
from entity.base import BaseUserEntity, User

# Configure logging
logger = logging.getLogger(__name__)


class UserEntity(BaseUserEntity):
    """YDB implementation for user-related database operations"""
    
    def __init__(self, driver, session_pool, database):
        self.driver = driver
        self.session_pool = session_pool
        self.database = database
    
    def create_user(self, user_id: str) -> User:
        """Create a new user"""
        def callee(session):
            user = self.get_user_by_external_id(user_id)

            if user is not None:
                return user
                
            id = uuid.uuid4().hex
            # First try to insert the user
            query = """
            DECLARE $id AS Utf8;
            DECLARE $user_id AS Utf8;
            UPSERT INTO users (id, user_id, created_at) VALUES ($id, $user_id, CurrentUtcTimestamp());
            """
            prepared_query = session.prepare(query)
            session.transaction().execute(
                prepared_query,
                parameters={
                    "$id": id,
                    "$user_id": user_id
                },
                commit_tx=True,
            )

            user = self.get_user_by_id(id)

            if user is None:
                raise Exception("Failed to retrieve created user")                
            
            return user
        
        return self.session_pool.retry_operation_sync(callee)
    
    def get_user_by_id(self, id: str) -> User:
        """Get user by ID"""
        def callee(session):
            query = """
            DECLARE $user_id AS Utf8;
            SELECT id, user_id, created_at FROM users WHERE id = $user_id;
            """
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters={"$user_id": id},
                commit_tx=True,
            )
            
            if result[0].rows:
                row = result[0].rows[0]
                return User(
                    row.id, 
                    row.user_id, 
                    str(row.created_at)
                )

        return self.session_pool.retry_operation_sync(callee)


    def get_user_by_external_id(self, external_user_id: str) -> User:
        """Get user by external userID"""
        def callee(session):
            query = """
            DECLARE $user_id AS Utf8;
            SELECT id, user_id, created_at FROM users WHERE user_id = $user_id;
            """
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters={"$user_id": external_user_id},
                commit_tx=True,
            )
            
            if result[0].rows:
                row = result[0].rows[0]

                return User(
                    row.id, 
                    row.user_id, 
                    str(row.created_at)
                )             

        return self.session_pool.retry_operation_sync(callee)

    
    def get_user_id_by_external_id(self, external_user_id: str) -> int:
        """Get internal user ID by external user ID"""
        def callee(session):
            query = """
            DECLARE $user_id AS Utf8;
            SELECT id FROM users WHERE user_id = $user_id;
            """
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters={"$user_id": external_user_id},
                commit_tx=True,
            )
            
            if result[0].rows:
                return result[0].rows[0].id
            else:
                return None
        
        return self.session_pool.retry_operation_sync(callee)
    
    def get_users_with_calendars(self) -> list:
        """Get users who have calendars"""
        def callee(session):
            query = """
            DECLARE $dummy AS Int32;
            SELECT DISTINCT u.id, u.user_id, u.created_at
            FROM users u
            JOIN calendars c ON u.id = c.user_id;
            """
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters={"$dummy": 0},
                commit_tx=True,
            )
            
            return [{'id': row.id, 'user_id': row.user_id, 'created_at': str(row.created_at)} for row in result[0].rows]
        
        return self.session_pool.retry_operation_sync(callee)
    
    def get_users_with_pending_events(self) -> list:
        """Get users who have pending events"""
        def callee(session):
            query = """
            DECLARE $dummy AS Int32;
            SELECT DISTINCT u.id, u.user_id, u.created_at
            FROM users u
            JOIN calendars c ON u.id = c.user_id
            JOIN events e ON c.id = e.calendar_id
            WHERE e.notified = FALSE;
            """
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters={"$dummy": 0},
                commit_tx=True,
            )
            
            return [{'id': row.id, 'user_id': row.user_id, 'created_at': str(row.created_at)} for row in result[0].rows]
        
        return self.session_pool.retry_operation_sync(callee)