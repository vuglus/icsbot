from migrations.base import BaseMigration
from entity.base import BaseMigrationEntity
import logging

# Configure logging
logger = logging.getLogger(__name__)


class SqliteMigration(BaseMigration):
    """Base class for SQLite migrations"""
    
    def run(self, entity: BaseMigrationEntity):
        """Run the migration using the provided SQLite connection"""
        raise NotImplementedError("Subclasses must implement run method")