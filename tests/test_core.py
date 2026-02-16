import unittest
import tempfile
import os
import sqlite3
from services.database import init_db, set_db_path, set_db_provider
from database_provider import DatabaseProvider
from entity.base import User, Calendar, Event


class TestCore(unittest.TestCase):
    """Test core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        set_db_path(self.temp_db.name)
        set_db_provider('sqlite')
        
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
        # Initialize database
        init_db()
        
        # Initialize entities through the provider
        provider = DatabaseProvider('sqlite', self.temp_db.name)
        user_entity, calendar_entity, event_entity = provider.get_entities()
        
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
        
    def test_entity_initialization_through_init_service(self):
        """Test entity initialization through init_service"""
        # Initialize database
        init_db()
        
        # Initialize entities through init_service
        # Note: We're not starting background processes in tests
        from services.init_service import _provider, _user_entity, _calendar_entity, _event_entity
        from services.database import get_db_provider, get_db_path
        
        # Create database provider directly (without starting background processes)
        db_provider = get_db_provider()
        db_path = get_db_path()
        
        provider = DatabaseProvider(db_provider, db_path)
        user_entity, calendar_entity, event_entity = provider.get_entities()
        
        # Set global variables manually
        import services.init_service
        services.init_service._provider = provider
        services.init_service._user_entity = user_entity
        services.init_service._calendar_entity = calendar_entity
        services.init_service._event_entity = event_entity
        
        # Set entities in services
        import services.calendar_service as calendar_service
        calendar_service.set_entities(calendar_entity, event_entity)
        
        import services.notification_service as notification_service
        notification_service.set_event_entity(event_entity)
        
        # Test that we can access entities through init_service
        user_entity = get_user_entity()
        calendar_entity = get_calendar_entity()
        event_entity = get_event_entity()
        
        # Test that entities are properly initialized
        self.assertIsNotNone(user_entity)
        self.assertIsNotNone(calendar_entity)
        self.assertIsNotNone(event_entity)
        
        # Test basic operations
        user = user_entity.create_user('test2@example.com')
        self.assertIsInstance(user, User)
        self.assertIsInstance(user.id, int)
        self.assertGreater(user.id, 0)
        self.assertEqual(user.user_id, 'test2@example.com')
        
        # Close provider to release database connection
        provider.close()

if __name__ == '__main__':
    unittest.main()