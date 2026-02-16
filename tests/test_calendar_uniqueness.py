import unittest
import tempfile
import os
from services.database import init_db, set_db_path, set_db_provider
from database_provider import DatabaseProvider
from entity.base import Calendar


class TestCalendarUniqueness(unittest.TestCase):
    """Test calendar uniqueness constraints"""
    
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
            
    def test_calendar_uniqueness_constraint(self):
        """Test that calendar uniqueness constraint works"""
        # Initialize entities through the provider
        provider = DatabaseProvider('sqlite', self.temp_db.name)
        user_entity, calendar_entity, event_entity = provider.get_entities()
        
        # Create a user
        user = user_entity.create_user('test@example.com')
        
        # Create first calendar
        calendar1 = calendar_entity.create_calendar(user.id, 'https://example.com/test.ics')
        self.assertIsInstance(calendar1, Calendar)
        self.assertGreater(calendar1.id, 0)
        
        # Try to create duplicate calendar - should return existing calendar
        calendar2 = calendar_entity.create_calendar(user.id, 'https://example.com/test.ics')
        self.assertEqual(calendar1.id, calendar2.id)
        
        # Verify only one calendar exists
        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 1)
        
    def test_calendars_for_different_users_can_have_same_url(self):
        """Test that calendars for different users can have the same URL"""
        # Initialize entities through the provider
        provider = DatabaseProvider('sqlite', self.temp_db.name)
        user_entity, calendar_entity, event_entity = provider.get_entities()
        
        # Create two users
        user1 = user_entity.create_user('test1@example.com')
        user2 = user_entity.create_user('test2@example.com')
        
        # Create calendars with same URL for different users
        calendar1 = calendar_entity.create_calendar(user1.id, 'https://example.com/test.ics')
        calendar2 = calendar_entity.create_calendar(user2.id, 'https://example.com/test.ics')
        
        # Both should succeed and have different IDs
        self.assertIsInstance(calendar1, Calendar)
        self.assertIsInstance(calendar2, Calendar)
        self.assertGreater(calendar1.id, 0)
        self.assertGreater(calendar2.id, 0)
        self.assertNotEqual(calendar1.id, calendar2.id)
        
        # Verify both calendars exist
        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 2)

if __name__ == '__main__':
    unittest.main()