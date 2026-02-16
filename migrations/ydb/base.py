from migrations.base import BaseMigration
import logging

# Configure logging
logger = logging.getLogger(__name__)


class YdbMigration(BaseMigration):
    """Base class for YDB migrations"""
    
    def run(self, session):
        """Run the migration using the provided YDB session"""
        raise NotImplementedError("Subclasses must implement run method")