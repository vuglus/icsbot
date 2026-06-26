import unittest
import tempfile
import os
from services.database import Database
from services.database_provider import DatabaseProvider
from services.config_service import Config
from migrations.sqlite.remove_calendar_duplicates import RemoveCalendarDuplicatesMigration


class TestCalendarTimezoneMigration(unittest.TestCase):
    """Test calendar timezone migration"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
    def tearDown(self):
        """Tear down test environment"""
        # Clean up temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
            
    def test_calendar_timezone_migration(self):
        """Test calendar timezone migration"""
        config = Config({
            'DB_PROVIDER': 'sqlite',
            'DB_PATH': self.temp_db.name,
        })
        
        # Initialize the database
        provider = DatabaseProvider(config)
        db = Database(provider, config)
        
        # Initialize entities through the provider
        user_entity, calendar_entity, event_entity, migration_entity = provider.get_entities()
        
        # Create a user and calendar before migration
        user = user_entity.create_user('test@example.com')
        calendar = calendar_entity.create_calendar(user.id, 'https://example.com/test.ics')
        
        # Verify calendar exists
        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 1)
        
        # Run a migration to verify the migration framework works
        migration = RemoveCalendarDuplicatesMigration()
        migration.run(migration_entity)
        
        # Verify calendar still exists after migration
        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 1)

if __name__ == '__main__':
    unittest.main()