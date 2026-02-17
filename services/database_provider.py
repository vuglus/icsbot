import os
import sqlite3
import ydb
import logging
from typing import Tuple
from services.config_service import Config

# Configure logging
logger = logging.getLogger(__name__)

# Import entity implementations
from entity.sqlite.user_entity import UserEntity as SqliteUserEntity
from entity.sqlite.calendar_entity import CalendarEntity as SqliteCalendarEntity
from entity.sqlite.event_entity import EventEntity as SqliteEventEntity

from entity.ydb.user_entity import UserEntity as YdbUserEntity
from entity.ydb.calendar_entity import CalendarEntity as YdbCalendarEntity
from entity.ydb.event_entity import EventEntity as YdbEventEntity

class DatabaseProvider:
    """Factory for creating database entity instances based on the configured provider"""
    
    def __init__(self, config: Config):
        self.db_provider = config.getDBProvider()
        self.db_path = config.getDBPath()
        self.config = config
        self._sqlite_connection = None
        self._ydb_driver = None
        self._ydb_session_pool = None
        self._ydb_database = None
    
    def get_entities(self) -> Tuple[object, object, object]:
        """Get entity instances based on the configured provider"""
        if self.db_provider == "sqlite":
            return self._get_sqlite_entities()
        elif self.db_provider == "ydb":
            return self._get_ydb_entities()
        else:
            raise ValueError(f"Unsupported database provider: {self.db_provider}")
    
    def _get_sqlite_entities(self):
        """Get SQLite entity instances"""
        if self._sqlite_connection is None:
            logger.info(f"Connecting to SQLite database: {self.db_path}")
            self._sqlite_connection = sqlite3.connect(self.db_path)
            self._sqlite_connection.row_factory = sqlite3.Row
        
        user_entity = SqliteUserEntity(self._sqlite_connection)
        calendar_entity = SqliteCalendarEntity(self._sqlite_connection)
        event_entity = SqliteEventEntity(self._sqlite_connection, self.config.get_notify_before_minutes())
        
        return user_entity, calendar_entity, event_entity
    
    def _get_ydb_entities(self):
        """Get YDB entity instances"""
        if self._ydb_driver is None:
            logger.info(f"Connecting to YDB database: {self.db_path}")
            
            # Create YDB driver
            self._ydb_driver = ydb.Driver(
                endpoint=self.db_path.split('?')[0],  # Extract endpoint from connection string
                database=self._extract_database_from_path(self.db_path)
            )
            
            # Wait for driver to become ready
            self._ydb_driver.wait(timeout=5)
            
            # Create session pool
            self._ydb_session_pool = ydb.SessionPool(self._ydb_driver)
            self._ydb_database = self._extract_database_from_path(self.db_path)
        
        user_entity = YdbUserEntity(self._ydb_driver, self._ydb_session_pool)
        calendar_entity = YdbCalendarEntity(self._ydb_driver, self._ydb_session_pool, user_entity)
        event_entity = YdbEventEntity(self._ydb_driver, self._ydb_session_pool, self.config.get_notify_before_minutes(), user_entity, calendar_entity)
        
        return user_entity, calendar_entity, event_entity
    
    def _extract_database_from_path(self, db_path: str) -> str:
        """Extract database name from YDB connection string"""
        # Example: grpcs://ydb.serverless.yandexcloud.net:2135/?database=/ru-central1/b1gfvslmokutu1i2072q/etn631u5ho5500ae44jb
        import urllib.parse
        parsed = urllib.parse.urlparse(db_path)
        query_params = urllib.parse.parse_qs(parsed.query)
        return query_params.get('database', [''])[0]
    
    def close(self):
        """Close database connections"""
        if self._sqlite_connection:
            self._sqlite_connection.close()
            self._sqlite_connection = None
        
        if self._ydb_session_pool:
            self._ydb_session_pool.stop()
            self._ydb_session_pool = None
        
        if self._ydb_driver:
            self._ydb_driver.stop()
            self._ydb_driver = None