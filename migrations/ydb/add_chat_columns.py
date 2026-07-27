from migrations.ydb.base import YdbMigration
import logging
from entity.base import BaseMigrationEntity

logger = logging.getLogger(__name__)


class AddChatColumnsMigration(YdbMigration):
    def run(self, entity: BaseMigrationEntity):
        logger.info("Starting add_chat_columns migration")
        try:
            entity.execute(
                [
                    "ALTER TABLE calendars ADD COLUMN chat_id Utf8;",
                    "ALTER TABLE calendars ADD COLUMN chat_type Utf8;",
                    "ALTER TABLE calendars ADD COLUMN client_type Utf8;",
                ]
            )
            logger.info("Added chat columns to calendars table")
        except Exception as e:
            logger.warning(f"Could not add columns (may already exist): {e}")

        try:
            entity.execute(
                [
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
            """
                ]
            )
            logger.info("Created sent_notifications table")
        except Exception as e:
            logger.warning(
                f"Could not create sent_notifications table (may already exist): {e}"
            )

        logger.info("Completed add_chat_columns migration")
