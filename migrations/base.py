import abc


class BaseMigration(abc.ABC):
    """Base interface for database migrations"""
    
    @abc.abstractmethod
    def run(self, connection):
        """Run the migration"""
        pass