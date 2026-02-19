from migrations.ydb.base import YdbMigration
import logging
from entity.base import BaseMigrationEntity

# Configure logging
logger = logging.getLogger(__name__)

class m20260219_events_index(YdbMigration):
    """Initialize the database with required tables"""
    
    def run(self, entity: BaseMigrationEntity):
        """Run the migration using the provided YDB session"""
        # Create migrations table
        entity.execute([
            "ALTER TABLE `events` ADD INDEX idx_event_uid GLOBAL ON (`uid`, `calendar_id`);", 
            "ALTER TABLE `events` ADD INDEX idx_calendar_uid GLOBAL ON (`calendar_id`);", 
        ])
