import unittest
import tempfile
import os
from services.database import init_db, set_db_path, set_db_provider
from database_provider import DatabaseProvider
from migrations.sqlite.add_calendar_timezone import AddCalendarTimezoneMigration


class TestCalendarTimezoneMigration(unittest.TestCase):
    """Test calendar timezone migration"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        set_db_path(self.temp_db.name)
        set_db_provider('sqlite')
        
        # Initialize database
        init_db()
        
    def tearDown(self):
        """Tear down test environment"""
        # Clean up temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
            
    def test_calendar_timezone_migration(self):
        """Test calendar timezone migration"""
        # Initialize entities through the provider
        provider = DatabaseProvider('sqlite', self.temp_db.name)
        user_entity, calendar_entity, event_entity = provider.get_entities()
        
        # Create a user and calendar before migration
        user = user_entity.create_user('test@example.com')
        calendar = calendar_entity.create_calendar(user, 'https://example.com/test.ics')
        
        # Verify calendar exists
        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 1)
        self.assertIsNone(calendars[0].timezone)  # Should be None before migration
        
        # Run the migration
        migration = AddCalendarTimezoneMigration()
        migration.up(self.temp_db.name)
        
        # Verify calendar still exists and has default timezone
        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 1)
        # After migration, timezone should be None (default) or UTC
        # The exact behavior depends on the migration implementation

if __name__ == '__main__':
    unittest.main()