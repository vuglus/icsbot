from migrations.ydb.base import YdbMigration
import logging
from entity.base import BaseMigrationEntity

logger = logging.getLogger(__name__)


class InitialSchemaMigration(YdbMigration):
    def run(self, entity: BaseMigrationEntity):
        logger.info("Starting initial_schema migration")
        try:
            entity.execute(
                [
                    """
                CREATE TABLE calendars (
                    id Utf8,
                    user_id Utf8,
                    chat_id Utf8,
                    chat_type Utf8,
                    url Utf8,
                    client_type Utf8,
                    name Utf8,
                    last_sync_at Timestamp,
                    sync_hash Utf8,
                    timezone Utf8,
                    created_at Timestamp,
                    PRIMARY KEY (id)
                );
                """,
                    """
                CREATE TABLE sent_notifications (
                    id Utf8,
                    calendar_id Utf8,
                    event_uid Utf8,
                    chat_id Utf8,
                    event_data Utf8,
                    sent_at Timestamp,
                    PRIMARY KEY (id)
                );
                """,
                ]
            )
            logger.info("Completed initial_schema migration")
        except Exception as e:
            logger.error(f"Error during initial_schema migration: {e}")
            raise
