from migrations.ydb.base import YdbMigration
import logging
from entity.base import BaseMigrationEntity

# Configure logging
logger = logging.getLogger(__name__)


class InitialSchemaMigration(YdbMigration):
    """Initialize the database with required tables"""
    
    def run(self, entity: BaseMigrationEntity):
        """Run the migration using the provided YDB session"""
        logger.info("Starting initial_schema migration")
        
        try:
            # Create users table
            entity.execute([
                '''
                    CREATE TABLE users (
                        id Utf8,
                        user_id Utf8,
                        created_at Timestamp,
                        PRIMARY KEY (id)
                    );
                ''',
                '''
                CREATE TABLE calendars (
                    id Utf8,
                    user_id Utf8,
                    url Utf8,
                    last_sync_at Timestamp,
                    sync_hash Utf8,
                    timezone Utf8,
                    created_at Timestamp,
                    PRIMARY KEY (id)
                );
                ''',
                '''CREATE TABLE events (
                    id Utf8,
                    calendar_id Utf8,
                    uid Utf8,
                    title Utf8,
                    description Utf8,
                    location Utf8,
                    start_datetime Utf8,
                    end_datetime Utf8,
                    all_day Bool,
                    notified Bool,
                    created_at Timestamp,
                    PRIMARY KEY (id)
                );
                ''',
            ])
            
            logger.info("Completed initial_schema migration")
            
        except Exception as e:
            logger.error(f"Error during initial_schema migration: {e}")
            raise
        
        logger.info("Completed initial_schema migration")