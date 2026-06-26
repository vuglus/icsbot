import unittest
import json
import os
from flask import Flask
from flask_smorest import Api
from services.api_service import App
from services.database import Database
from services.config_service import Config
from services.database_provider import DatabaseProvider

class TestAPIIntegration(unittest.TestCase):
    """Test API integration endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        # Set API key for testing
        os.environ['ICS_GATE_API_KEY'] = 'test-api-key'
        # Create a temporary database for testing
        config = Config({
            'api_key': 'test-api-key',
            'DB_PROVIDER': 'sqlite',
            'DB_PATH': ':memory:',
        })
        provider = DatabaseProvider(config=config)
        db = Database(provider, config=config)
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
                # Get the API key from the request
                from flask import request
                api_key = request.headers.get('X-Auth-Token')
                return api_key == 'test-api-key'
        auth_service = MockAuthService()
        
        # Use the App class to initialize API
        app_instance = App()
        app_instance.initialize_api(api, auth_service, None, None)
        
        # Create test client after full initialization
        self.client = self.app.test_client()
        
    def tearDown(self):
        """Tear down test environment"""
        # Clean up temporary database
             
    def test_full_api_flow(self):
        """Test full API flow: create user, create calendar, create events"""
        # Create a calendar (user will be created automatically)
        calendar_data = {
            'user_id': 'test@example.com',
            'url': 'https://example.com/calendar.ics'
        }
        
        response = self.client.post(
            '/calendars',
            json=calendar_data,
            headers={'X-Auth-Token': 'test-api-key'}
        )
        
        # Check calendar creation
        self.assertEqual(response.status_code, 201)
        calendar_response = json.loads(response.data)
        self.assertEqual(calendar_response['status'], 'success')
        calendar_id = calendar_response['calendar']['id']
        
        # Verify data through direct database access
        config = Config({
            'DB_PROVIDER': 'sqlite',
            'DB_PATH': ':memory:',
        })
        provider = DatabaseProvider(config)
        user_entity, calendar_entity, event_entity, _ = provider.get_entities()
        
        # Check user exists
        users = user_entity.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['user_id'], 'test@example.com')
        
        # Check calendar exists
        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 1)
        self.assertEqual(calendars[0].id, calendar_id)
        self.assertEqual(calendars[0].user_id, users[0]['id'])
        self.assertEqual(calendars[0].url, 'https://example.com/calendar.ics')

if __name__ == '__main__':
    unittest.main()