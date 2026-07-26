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
    
    def __init__(self, provider: DatabaseProvider, config: Config):
        self.provider_type = config.getDBProvider()
        self.endpoint = config.getDBEndpoint()
        self.path = config.getDBPath()
        self.config = config
        self.provider = provider
        self._user_entity = None
        self._calendar_entity = None
        self._event_entity = None
        self._migration_entity = None
        self._initialize_entities()
        self.init_migrations()

    
    def _initialize_entities(self):
        """Initialize database entities if not already initialized"""
        self._user_entity, self._calendar_entity, self._event_entity, self._migration_entity = self.provider.get_entities()
        
    def getUser(self) -> BaseUserEntity :  
        """Get the user entity instance"""
        if self._user_entity == None:
            raise Exception("User entity not initialized")
            
        return self._user_entity
    
    def getCalendar(self) -> BaseCalendarEntity : 
        """Get the calendar entity instance"""
        return self._calendar_entity
    
    def getEvent(self) -> BaseEventEntity :
        """Get the event entity instance"""
        return self._event_entity
    
    def init_migrations(self):
        """Initialize and run all database migrations"""
        logger.info(f"Initializing database migrations: {self._migration_entity}")
        migration_manager = MigrationManager(
            self.provider_type,
            self._migration_entity
        )
        migration_manager.run_all_migrations()
