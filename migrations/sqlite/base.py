from migrations.base import BaseMigration
import logging

# Configure logging
logger = logging.getLogger(__name__)


class SqliteMigration(BaseMigration):
    """Base class for SQLite migrations"""
    
    def run(self, connection):
        """Run the migration using the provided SQLite connection"""
        raise NotImplementedError("Subclasses must implement run method")