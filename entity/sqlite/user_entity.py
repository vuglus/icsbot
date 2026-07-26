import sqlite3
import logging
from datetime import datetime
from typing import Optional
from entity.base import BaseUserEntity, User

# Configure logging
logger = logging.getLogger(__name__)


class UserEntity(BaseUserEntity):
    """SQLite implementation for user-related database operations"""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_user(self, user_id: str) -> User:
        """Create a new user"""
        cursor = self.db_connection.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (user_id) VALUES (?)',
                (user_id,)
            )
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables in database: {[table[0] for table in tables]}")
            
            self.db_connection.commit()
            user_row_id = cursor.lastrowid
            logger.info(f"Created user with ID {user_row_id}")
            return User(user_row_id, user_id, datetime.now().isoformat())
        except sqlite3.IntegrityError:
            logger.warning(f"User {user_id} already exists")
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            return User(row['id'], row['user_id'], row['created_at'])
    
    def get_user_id_by_external_id(self, external_user_id: str) -> int:
        """Get internal user ID by external user ID"""
        cursor = self.db_connection.cursor()
        
        cursor.execute('SELECT id FROM users WHERE user_id = ?', (external_user_id,))
        user_row = cursor.fetchone()
        
        if not user_row:
            return None
        
        return user_row['id']
    
    def get_users_with_calendars(self) -> list:
        """Get users who have calendars"""
        cursor = self.db_connection.cursor()
        
        cursor.execute('''
            SELECT DISTINCT u.id, u.user_id
            FROM users u
            JOIN calendars c ON u.id = c.user_id
        ''')
        
        rows = cursor.fetchall()
        return [{'id': row['id'], 'email': row['user_id']} for row in rows]
    
    def get_users_with_pending_events(self) -> list:
        """Get users who have pending events"""
        cursor = self.db_connection.cursor()
        
        cursor.execute('''
            SELECT DISTINCT u.id, u.user_id
            FROM users u
            JOIN calendars c ON u.id = c.user_id
            JOIN events e ON c.id = e.calendar_id
            WHERE e.notified = FALSE
        ''')
        
        rows = cursor.fetchall()
        return [{'id': row['id'], 'email': row['user_id']} for row in rows]