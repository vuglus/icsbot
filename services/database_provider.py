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
from entity.sqlite.migration_entity import MigrationEntity as SqliteMigrationEntity

from entity.ydb.user_entity import UserEntity as YdbUserEntity
from entity.ydb.calendar_entity import CalendarEntity as YdbCalendarEntity
from entity.ydb.event_entity import EventEntity as YdbEventEntity
from entity.ydb.migration_entity import MigrationEntity as YdbMigrationEntity


class DatabaseProvider:
    """Factory for creating database entity instances based on the configured provider"""
    
    def __init__(self, config: Config):
        self.db_provider = config.getDBProvider()
        self.db_endpoint = config.getDBEndpoint()
        self.db_path = config.getDBPath()
        self.config = config
        self._sqlite_connection = None
        self._ydb_driver = None
        self._ydb_session_pool = None

    def getConnection(self):
        if self.db_provider == "sqlite":
            if self._sqlite_connection is None:
                self._sqlite_connection = sqlite3.connect(self.db_path)
                self._sqlite_connection.row_factory = sqlite3.Row
            return self._sqlite_connection
        if self.db_provider == "ydb":
            if self._ydb_driver is None:
                logger.info(f"Connecting to YDB database: {self.db_path}")
                
                # Create YDB driver
                self._ydb_driver = ydb.Driver(
                    endpoint=self.db_endpoint,
                    database=self.db_path,
                    credentials=ydb.credentials_from_env_variables()
                )
                
                # Wait for driver to become ready
                self._ydb_driver.wait(timeout=5)
                
                # Create session pool
                self._ydb_session_pool = ydb.SessionPool(self._ydb_driver)
                return self._ydb_session_pool

        raise NotImplementedError(f"{self.db_provider} is not supported yet")
    
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
        conn = self.getConnection()
        user_entity = SqliteUserEntity(conn)
        calendar_entity = SqliteCalendarEntity(conn)
        event_entity = SqliteEventEntity(conn, self.config.get_notify_before_minutes())
        migration_entity = SqliteMigrationEntity(conn)
        
        return user_entity, calendar_entity, event_entity, migration_entity
    
    def _get_ydb_entities(self):
        conn = self.getConnection()
        user_entity = YdbUserEntity(conn)
        calendar_entity = YdbCalendarEntity(conn, user_entity)
        event_entity = YdbEventEntity(conn, self.config.get_notify_before_minutes(), user_entity, calendar_entity)
        migration_entity = YdbMigrationEntity(conn)
        
        return user_entity, calendar_entity, event_entity, migration_entity
    
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