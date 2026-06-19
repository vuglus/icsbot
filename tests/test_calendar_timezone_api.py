import unittest
import json
import tempfile
import os
from flask import Flask
from flask_smorest import Api
from services.api_service import initialize_api
from services.api_utils import AuthService
from services.database import init_db, set_db_path, set_db_provider
from services.config_service import Config
from database_provider import DatabaseProvider


class TestCalendarTimezoneAPI(unittest.TestCase):
    """Test cases for calendar timezone API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        # Set API key for testing
        os.environ['ICS_GATE_API_KEY'] = 'test-api-key'
        
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        set_db_path(self.temp_db.name)
        set_db_provider('sqlite')
        
        # Initialize database
        init_db()
        config = Config({
            'api_key': 'test-api-key'
        })
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
        initialize_api(api, auth_service, config)
        
        # Create test client after full initialization
        self.client = self.app.test_client()
        
    def tearDown(self):
        """Tear down test environment"""
        # Clean up temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
            
    def test_update_calendar_timezone_success(self):
        """Test successful calendar timezone update"""
        # First create a calendar
        calendar_data = {
            'user_id': 'test_user',
            'url': 'https://example.com/calendar.ics'
        }
        
        response = self.client.post(
            '/calendars',
            json=calendar_data,
            headers={'X-Auth-Token': 'test-api-key'}
        )
        
        self.assertEqual(response.status_code, 201)
        calendar = json.loads(response.data)['calendar']
        calendar_id = calendar['id']
        
        # Update timezone
        timezone_data = {
            'timezone': 'Europe/Moscow'
        }
        
        response = self.client.patch(
            f'/calendars/{calendar_id}/timezone',
            json=timezone_data,
            headers={'X-Auth-Token': 'test-api-key'}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['calendar']['timezone'], 'Europe/Moscow')
        
    def test_update_calendar_timezone_not_found(self):
        """Test updating timezone for non-existent calendar"""
        timezone_data = {
            'timezone': 'Europe/Moscow'
        }
        
        response = self.client.patch(
            '/calendars/999999/timezone',
            json=timezone_data,
            headers={'X-Auth-Token': 'test-api-key'}
        )
        
        # Check response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 404)
        
    def test_update_calendar_timezone_invalid_timezone(self):
        """Test updating calendar with invalid timezone"""
        # First create a calendar
        calendar_data = {
            'user_id': 'test_user',
            'url': 'https://example.com/calendar.ics'
        }
        
        response = self.client.post(
            '/calendars',
            json=calendar_data,
            headers={'X-Auth-Token': 'test-api-key'}
        )
        
        self.assertEqual(response.status_code, 201)
        calendar = json.loads(response.data)['calendar']
        calendar_id = calendar['id']
        
        # Update with invalid timezone
        timezone_data = {
            'timezone': 'Invalid/Timezone'
        }
        
        response = self.client.patch(
            f'/calendars/{calendar_id}/timezone',
            json=timezone_data,
            headers={'X-Auth-Token': 'test-api-key'}
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 400)

if __name__ == '__main__':
    unittest.main()