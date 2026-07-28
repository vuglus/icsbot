from migrations.sqlite.base import SqliteMigration
import logging
from entity.base import BaseMigrationEntity

logger = logging.getLogger(__name__)


class AddNameColumnMigration(SqliteMigration):
    def run(self, entity: BaseMigrationEntity):
        logger.info("Starting add_name_column migration")
        try:
            entity.execute("SELECT name FROM calendars LIMIT 1")
            logger.info("name column already exists, skipping")
        except Exception:
            entity.execute("ALTER TABLE calendars ADD COLUMN name TEXT")
            logger.info("Added name column")
        logger.info("Completed add_name_column migration")
