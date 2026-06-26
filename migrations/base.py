import abc
from entity.base import BaseMigrationEntity

class BaseMigration(abc.ABC):
    """Base interface for database migrations"""
    
    @abc.abstractmethod
    def run(self, entity: BaseMigrationEntity):
        """Run the migration"""
        pass