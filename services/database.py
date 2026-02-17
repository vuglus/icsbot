import logging
import urllib.parse
from services.database_provider import DatabaseProvider
from services.config_service import Config
from migrations.migration_manager import MigrationManager
from entity.base import BaseUserEntity, BaseCalendarEntity, BaseEventEntity


# Configure logging
logger = logging.getLogger(__name__)


class Database:
    """Database class for managing database connections and migrations"""
    
    def __init__(self, config: Config):
        self.provider_type = config.getDBProvider()
        self.path = config.getDBPath()
        self.config = config
        self.provider = DatabaseProvider(config)
        self._user_entity = None
        self._calendar_entity = None
        self._event_entity = None
        self.init_migrations()
    
    def _initialize_entities(self):
        """Initialize database entities if not already initialized"""
        if self._user_entity is None or self._calendar_entity is None or self._event_entity is None:
            self._user_entity, self._calendar_entity, self._event_entity = self.provider.get_entities()
    
    def getUser(self) -> BaseUserEntity :  
        """Get the user entity instance"""
        self._initialize_entities()
        return self._user_entity
    
    def getCalendar(self) -> BaseCalendarEntity : 
        """Get the calendar entity instance"""
        self._initialize_entities()
        return self._calendar_entity
    
    def getEvent(self) -> BaseEventEntity :
        """Get the event entity instance"""
        self._initialize_entities()
        return self._event_entity
    
    def init_migrations(self):
        """Initialize and run all database migrations"""
        logger.info("Initializing database migrations")

        if self.provider_type == "sqlite":
            import sqlite3
            conn = sqlite3.connect(self.path)
            conn.row_factory = sqlite3.Row
            migration_manager = MigrationManager(
                self.provider_type,
                db_connection=conn
            )
            migration_manager.run_all_migrations()
            conn.close()

        elif self.provider_type == "ydb":
            import ydb
            ydb_driver = ydb.Driver(
                endpoint=self.path.split('?')[0],
                database=self._extract_database_from_path(self.path)
            )
            ydb_driver.wait(timeout=5)
            session = ydb_driver.table_client.session().create()

            migration_manager = MigrationManager(
                self.provider_type,
                ydb_session=session
            )
            migration_manager.run_all_migrations()
            ydb_driver.stop()

    def _extract_database_from_path(self, db_path: str) -> str:
        """Extract database name from YDB connection string"""
        # Example: grpcs://ydb.serverless.yandexcloud.net:2135/?database=/ru-central1/b1gfvslmokutu1i2072q/etn631u5ho5500ae44jb
        parsed = urllib.parse.urlparse(db_path)
        query_params = urllib.parse.parse_qs(parsed.query)
        return query_params.get('database', [''])[0]