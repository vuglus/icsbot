import os
import sqlite3
import ydb
import logging
from typing import Tuple
from services.config_service import Config

logger = logging.getLogger(__name__)

from entity.sqlite.calendar_entity import CalendarEntity as SqliteCalendarEntity
from entity.sqlite.sent_notification_entity import (
    SentNotificationEntity as SqliteSentNotificationEntity,
)
from entity.sqlite.migration_entity import MigrationEntity as SqliteMigrationEntity

from entity.ydb.calendar_entity import CalendarEntity as YdbCalendarEntity
from entity.ydb.sent_notification_entity import (
    SentNotificationEntity as YdbSentNotificationEntity,
)
from entity.ydb.migration_entity import MigrationEntity as YdbMigrationEntity


class DatabaseProvider:
    def __init__(self, config: Config):
        self.config = config
        self.db_provider = config.getDBProvider()
        self.db_endpoint = config.getDBEndpoint()
        self.db_path = config.getDBPath()
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
                self._ydb_driver = ydb.Driver(
                    endpoint=self.db_endpoint,
                    database=self.db_path,
                    credentials=ydb.credentials_from_env_variables(),
                )
                self._ydb_driver.wait(timeout=30)
                self._ydb_session_pool = ydb.SessionPool(self._ydb_driver)
                return self._ydb_session_pool
        raise NotImplementedError(f"{self.db_provider} is not supported yet")

    def get_entities(self) -> Tuple[object, object, object]:
        if self.db_provider == "sqlite":
            return self._get_sqlite_entities()
        elif self.db_provider == "ydb":
            return self._get_ydb_entities()
        else:
            raise ValueError(f"Unsupported database provider: {self.db_provider}")

    def _get_sqlite_entities(self):
        conn = self.getConnection()
        calendar_entity = SqliteCalendarEntity(conn)
        sent_notification_entity = SqliteSentNotificationEntity(conn)
        migration_entity = SqliteMigrationEntity(conn)
        return calendar_entity, sent_notification_entity, migration_entity

    def _get_ydb_entities(self):
        conn = self.getConnection()
        calendar_entity = YdbCalendarEntity(conn)
        sent_notification_entity = YdbSentNotificationEntity(conn)
        migration_entity = YdbMigrationEntity(conn)
        return calendar_entity, sent_notification_entity, migration_entity

    def close(self):
        if self._sqlite_connection:
            self._sqlite_connection.close()
            self._sqlite_connection = None
        if self._ydb_session_pool:
            self._ydb_session_pool.stop()
            self._ydb_session_pool = None
        if self._ydb_driver:
            self._ydb_driver.stop()
            self._ydb_driver = None
