from migrations.ydb.base import YdbMigration
import logging
from entity.base import BaseMigrationEntity

# Configure logging
logger = logging.getLogger(__name__)

class m20260218_migration_table(YdbMigration):
    """Initialize the database with required tables"""
    
    def run(self, entity: BaseMigrationEntity):
        """Run the migration using the provided YDB session"""
        # Create migrations table
        entity.execute(['''
            CREATE TABLE migrations (
                id Utf8,
                name Utf8,
                executed_at Timestamp,
                PRIMARY KEY (id)
            );
        '''])
