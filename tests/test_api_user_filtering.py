import unittest
import json
import tempfile
import os
from flask import Flask
from flask_smorest import Api
from services.api_service import App
from services.api_utils import AuthService
from services.database import Database
from services.config_service import Config
from services.database_provider import DatabaseProvider


class TestAPIUserFiltering(unittest.TestCase):
    """Test API user filtering endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        # Set API key for testing
        os.environ['ICS_GATE_API_KEY'] = 'test-api-key'
        
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        config = Config({
            'api_key': 'test-api-key',
            'DB_PROVIDER': 'sqlite',
            'DB_PATH': self.temp_db.name,
        })
        
        # Initialize the database
        provider = DatabaseProvider(config)
        db = Database(provider, config)
        
        # Set up Flask app for testing
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["API_TITLE"] = "ICS Bot API"
        self.app.config["API_VERSION"] = "v1"
        self.app.config["OPENAPI_VERSION"] = "3.0.2"
        
        # Initialize API endpoints
        api = Api(self.app)
        # Create a mock auth service for testing
        class MockAuthService:
            def validate_api_key(self):
                return True
        auth_service = MockAuthService()
        
        app_instance = App()
        app_instance.initialize_api(api, auth_service, None, None)
        
        # Create test client after full initialization
        self.client = self.app.test_client()
        
    def tearDown(self):
        """Tear down test environment"""
        # Clean up temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
            
    def test_get_users_with_calendars(self):
        """Test getting users with calendars via API"""
        # First create some users and calendars through direct database access
        config = Config({
            'DB_PROVIDER': 'sqlite',
            'DB_PATH': self.temp_db.name,
        })
        provider = DatabaseProvider(config)
        user_entity, calendar_entity, event_entity, _ = provider.get_entities()
        
        # Create users
        user_id1 = user_entity.create_user('user1@example.com')
        user_id2 = user_entity.create_user('user2@example.com')
        user_id3 = user_entity.create_user('user3@example.com')
        
        # Create calendars for some users
        calendar_entity.create_calendar(user_id1.id, 'https://example.com/cal1.ics')
        calendar_entity.create_calendar(user_id2.id, 'https://example.com/cal2.ics')
        # user_id3 has no calendars
        
        # Get users with calendars via API
        response = self.client.get(
            '/users/with-calendars',
            headers={'X-Auth-Token': 'test-api-key'}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['users']), 2)
        
        # Check that correct users are returned
        user_ids_with_calendars = [user['id'] for user in data['users']]
        self.assertIn(user_id1.id, user_ids_with_calendars)
        self.assertIn(user_id2.id, user_ids_with_calendars)
        self.assertNotIn(user_id3.id, user_ids_with_calendars)
        
    def test_get_users_with_pending_events(self):
        """Test getting users with pending events via API"""
        # First create some users, calendars, and events through direct database access
        config = Config({
            'DB_PROVIDER': 'sqlite',
            'DB_PATH': self.temp_db.name,
        })
        provider = DatabaseProvider(config)
        user_entity, calendar_entity, event_entity, _ = provider.get_entities()
        
        # Create users
        user_id1 = user_entity.create_user('user1@example.com')
        user_id2 = user_entity.create_user('user2@example.com')
        user_id3 = user_entity.create_user('user3@example.com')
        
        # Create calendars
        calendar_id1 = calendar_entity.create_calendar(user_id1.id, 'https://example.com/cal1.ics')
        calendar_id2 = calendar_entity.create_calendar(user_id2.id, 'https://example.com/cal2.ics')
        calendar_id3 = calendar_entity.create_calendar(user_id3.id, 'https://example.com/cal3.ics')
        
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
        
        # Get users with pending events via API
        response = self.client.get(
            '/users/with-pending-events',
            headers={'X-Auth-Token': 'test-api-key'}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['users']), 2)
        
        # Check that correct users are returned
        user_ids_with_events = [user['id'] for user in data['users']]
        self.assertIn(user_id1.id, user_ids_with_events)
        self.assertIn(user_id2.id, user_ids_with_events)
        self.assertNotIn(user_id3.id, user_ids_with_events)

if __name__ == '__main__':
    unittest.main()