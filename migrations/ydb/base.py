from migrations.base import BaseMigration
import logging
from entity.base import BaseMigrationEntity

# Configure logging
logger = logging.getLogger(__name__)


class YdbMigration(BaseMigration):
    """Base class for YDB migrations"""
    
    def run(self, entity: BaseMigrationEntity):
        """Run the migration using the provided YDB session"""
        raise NotImplementedError("Subclasses must implement run method")