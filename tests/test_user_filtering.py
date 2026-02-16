import unittest
import tempfile
import os
from services.database import init_db, set_db_path, set_db_provider
from database_provider import DatabaseProvider


class TestUserFiltering(unittest.TestCase):
    """Test user filtering functionality"""
    
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
            
    def test_get_users_with_calendars(self):
        """Test getting users with calendars"""
        # Initialize entities through the provider
        provider = DatabaseProvider('sqlite', self.temp_db.name)
        user_entity, calendar_entity, event_entity = provider.get_entities()
        
        # Create users
        user1 = user_entity.create_user('user1@example.com')
        user2 = user_entity.create_user('user2@example.com')
        user3 = user_entity.create_user('user3@example.com')
        
        # Create calendars for some users
        calendar_entity.create_calendar(user1.id, 'https://example.com/cal1.ics')
        calendar_entity.create_calendar(user2.id, 'https://example.com/cal2.ics')
        # user3 has no calendars
        
        # Get users with calendars
        users_with_calendars = user_entity.get_users_with_calendars()
        
        # Should only return users with calendars
        self.assertEqual(len(users_with_calendars), 2)
        user_ids_with_calendars = [user['id'] for user in users_with_calendars]
        self.assertIn(user1.id, user_ids_with_calendars)
        self.assertIn(user2.id, user_ids_with_calendars)
        self.assertNotIn(user3.id, user_ids_with_calendars)
        
    def test_get_users_with_pending_events(self):
        """Test getting users with pending events"""
        # Initialize entities through the provider
        provider = DatabaseProvider('sqlite', self.temp_db.name)
        user_entity, calendar_entity, event_entity = provider.get_entities()
        
        # Create users
        user1 = user_entity.create_user('user1@example.com')
        user2 = user_entity.create_user('user2@example.com')
        user3 = user_entity.create_user('user3@example.com')
        
        # Create calendars
        calendar_id1 = calendar_entity.create_calendar(user1.id, 'https://example.com/cal1.ics')
        calendar_id2 = calendar_entity.create_calendar(user2.id, 'https://example.com/cal2.ics')
        calendar_id3 = calendar_entity.create_calendar(user3.id, 'https://example.com/cal3.ics')
        
        # Create events for some users
        event_entity.create_event(
            calendar_id=calendar_id1,
            uid='event1',
            title='Event 1',
            start_datetime='2023-01-01 10:00:00',
            end_datetime='2023-01-01 11:00:00',
            description='Test event',
            location='',
            all_day=False
        )
        
        event_entity.create_event(
            calendar_id=calendar_id2,
            uid='event2',
            title='Event 2',
            start_datetime='2023-01-01 10:00:00',
            end_datetime='2023-01-01 11:00:00',
            description='Test event',
            location='',
            all_day=False
        )
        
        # user_id3 has no events
        
        # Get users with pending events
        users_with_events = user_entity.get_users_with_pending_events()
        
        # Should only return users with events
        self.assertEqual(len(users_with_events), 2)
        user_ids_with_events = [user['id'] for user in users_with_events]
        self.assertIn(user1.id, user_ids_with_events)
        self.assertIn(user2.id, user_ids_with_events)
        self.assertNotIn(user3.id, user_ids_with_events)

if __name__ == '__main__':
    unittest.main()