from migrations.ydb.base import YdbMigration
import logging
from entity.base import BaseMigrationEntity

logger = logging.getLogger(__name__)


class AddNameColumnMigration(YdbMigration):
    def run(self, entity: BaseMigrationEntity):
        logger.info("Starting add_name_column migration")
        try:
            entity.execute(
                [
                    "ALTER TABLE calendars ADD COLUMN name Utf8;",
                ]
            )
            logger.info("Added name column to calendars table")
        except Exception as e:
            logger.warning(f"Could not add name column (may already exist): {e}")
        logger.info("Completed add_name_column migration")
