import unittest
import tempfile
import os
import sqlite3
from services.database import Database
from services.database_provider import DatabaseProvider
from services.config_service import Config
from entity.base import User, Calendar, Event


class TestCore(unittest.TestCase):
    """Test core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
    def tearDown(self):
        """Tear down test environment"""
        # Clean up temporary database
        if os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except PermissionError:
                # File is still in use, that's okay for tests
                pass
            
    def test_database_initialization(self):
        """Test database initialization"""
        config = Config({
            'DB_PROVIDER': 'sqlite',
            'DB_PATH': self.temp_db.name,
        })
        
        # Initialize the database
        provider = DatabaseProvider(config)
        db = Database(provider, config)
        
        # Initialize entities through the provider
        user_entity, calendar_entity, event_entity, _ = provider.get_entities()
        
        # Test that entities are properly initialized
        self.assertIsNotNone(user_entity)
        self.assertIsNotNone(calendar_entity)
        self.assertIsNotNone(event_entity)
        
        # Test that we can perform basic operations
        user = user_entity.create_user('test@example.com')
        self.assertIsInstance(user, User)
        self.assertIsInstance(user.id, int)
        self.assertGreater(user.id, 0)
        self.assertEqual(user.user_id, 'test@example.com')
        
        # Test calendar operations
        calendar = calendar_entity.create_calendar(user.id, 'https://example.com/test.ics')
        self.assertIsInstance(calendar, Calendar)
        self.assertIsInstance(calendar.id, int)
        self.assertGreater(calendar.id, 0)
        self.assertEqual(calendar.user_id, user.id)
        self.assertEqual(calendar.url, 'https://example.com/test.ics')
        
        # Test event operations
        event = event_entity.create_event(
            calendar_id=calendar.id,
            uid='test-event-1',
            title='Test Event',
            start_datetime='2023-01-01 10:00:00',
            end_datetime='2023-01-01 11:00:00',
            description='Test event description',
            location='Test Location',
            all_day=False
        )
        self.assertIsInstance(event, Event)
        self.assertIsInstance(event.id, int)
        self.assertGreater(event.id, 0)
        self.assertEqual(event.calendar_id, calendar.id)
        self.assertEqual(event.uid, 'test-event-1')
        self.assertEqual(event.title, 'Test Event')
        
        # Close provider to release database connection
        provider.close()

if __name__ == '__main__':
    unittest.main()