import logging
from services.database_provider import DatabaseProvider
from services.config_service import Config
from migrations.migration_manager import MigrationManager
from entity.base import BaseCalendarEntity, BaseSentNotificationEntity

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, provider: DatabaseProvider, config: Config):
        self.provider_type = config.getDBProvider()
        self.endpoint = config.getDBEndpoint()
        self.path = config.getDBPath()
        self.config = config
        self.provider = provider
        self._calendar_entity = None
        self._sent_notification_entity = None
        self._migration_entity = None
        self._initialize_entities()
        self.init_migrations()

    def _initialize_entities(self):
        (
            self._calendar_entity,
            self._sent_notification_entity,
            self._migration_entity,
        ) = self.provider.get_entities()

    def getCalendar(self) -> BaseCalendarEntity:
        return self._calendar_entity

    def getSentNotification(self) -> BaseSentNotificationEntity:
        return self._sent_notification_entity

    def init_migrations(self):
        logger.info(f"Initializing database migrations: {self._migration_entity}")
        migration_manager = MigrationManager(self.provider_type, self._migration_entity)
        migration_manager.run_all_migrations()
