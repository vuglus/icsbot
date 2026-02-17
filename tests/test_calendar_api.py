import unittest
import json
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_smorest import Api
from services.config_service import Config
from services.database import Database
from services.api_utils import AuthService
from services.calendar_service import CalendarService
from services.notification_service import NotificationService
from services.api_endpoints import create_endpoints

class TestCalendarAPI(unittest.TestCase):
    """Test cases for calendar API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        # Set API key for testing
        os.environ['ICS_GATE_API_KEY'] = 'test-api-key'
        
        # Create a temporary database file
        self.temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_file.close()
        
        # Create config with temporary database
        config_data = {
            'api_key': 'test-api-key',
            'DB_PROVIDER': 'sqlite',
            'DB_PATH': self.temp_db_file.name,
            'notify_before_minutes': 10
        }
        self.config = Config(config_data)
        
        # Initialize database
        self.database = Database(self.config)
        
        # Set up Flask app for testing
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["API_TITLE"] = "ICS Bot API"
        self.app.config["API_VERSION"] = "v1"
        self.app.config["OPENAPI_VERSION"] = "3.0.2"
        
        # Initialize services
        self.auth_service = AuthService(self.app, self.config)
        self.calendar_service = CalendarService(self.database)
        self.notification_service = NotificationService(self.database)
        
        # Initialize API endpoints
        api = Api(self.app)
        
        # Create all endpoints with injected dependencies
        blueprints = create_endpoints(self.auth_service, self.calendar_service, self.notification_service)
        
        # Register blueprints with the API
        for name, blueprint in blueprints.items():
            if hasattr(blueprint, 'name') and blueprint.name:
                api.register_blueprint(blueprint)
        
        # Create test client after full initialization
        self.client = self.app.test_client()
        
    def tearDown(self):
        """Tear down test environment"""
        # Close any database connections
        if hasattr(self.database.provider, '_sqlite_connection') and self.database.provider._sqlite_connection:
            self.database.provider._sqlite_connection.close()
        
        # Clean up temporary database file
        if os.path.exists(self.temp_db_file.name):
            os.unlink(self.temp_db_file.name)
            
    def test_create_calendar_success(self):
        """Test successful calendar creation"""
        # Test data
        test_data = {
            'user_id': 'test_user',
            'url': 'https://example.com/calendar.ics'
        }
        
        # Make request
        response = self.client.post(
            '/calendars',
            json=test_data,
            headers={'X-API-Key': 'test-api-key'}
        )
        
        # Check response
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('calendar', data)
        self.assertEqual(data['calendar']['url'], 'https://example.com/calendar.ics')
        
    def test_create_calendar_duplicate(self):
        """Test creating duplicate calendar (should return existing)"""
        # Test data
        test_data = {
            'user_id': 'test_user',
            'url': 'https://example.com/calendar.ics'
        }
        
        # Create calendar first time
        response1 = self.client.post(
            '/calendars',
            json=test_data,
            headers={'X-API-Key': 'test-api-key'}
        )
        
        # Create same calendar again
        response2 = self.client.post(
            '/calendars',
            json=test_data,
            headers={'X-API-Key': 'test-api-key'}
        )
        
        # Both should succeed
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        
        # Both should return the same calendar ID
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        self.assertEqual(data1['calendar']['id'], data2['calendar']['id'])
        
        # Check that only one calendar exists in database
        calendars = self.calendar_service.calendars.get_calendars()
        self.assertEqual(len(calendars), 1)
        
    def test_create_calendar_invalid_url(self):
        """Test creating calendar with invalid URL"""
        # Test data with invalid URL
        test_data = {
            'user_id': 'test_user',
            'url': 'invalid-url'
        }
        
        # Make request
        response = self.client.post(
            '/calendars',
            json=test_data,
            headers={'X-API-Key': 'test-api-key'}
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 400)
        
    def test_create_calendar_missing_fields(self):
        """Test creating calendar with missing required fields"""
        # Test data with missing fields
        test_data = {
            'user_id': 'test_user'
            # Missing 'url'
        }
        
        # Make request
        response = self.client.post(
            '/calendars',
            json=test_data,
            headers={'X-API-Key': 'test-api-key'}
        )
        
        # Check response
        self.assertEqual(response.status_code, 422)
        data = json.loads(response.data)
        self.assertIn('errors', data)
        
    def test_create_calendar_unauthorized(self):
        """Test creating calendar without valid API key"""
        # Test data
        test_data = {
            'user_id': 'test_user',
            'url': 'https://example.com/calendar.ics'
        }
        
        # Make request without API key
        response = self.client.post('/calendars', json=test_data)
        
        # Check response
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 401)
    
    def test_sync_calendar_success(self):
        """Test successful calendar synchronization"""
        # First create a calendar
        test_data = {
            'user_id': 'test_user',
            'url': 'https://example.com/calendar.ics'
        }
        
        # Create calendar
        response = self.client.post(
            '/calendars',
            json=test_data,
            headers={'X-API-Key': 'test-api-key'}
        )
        
        # Check that calendar was created
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        calendar_id = data['calendar']['id']
        
        # Mock the sync_calendar_by_id method to return True
        with patch.object(self.calendar_service, 'sync_calendar_by_id', return_value=True):
            # Test sync endpoint
            sync_response = self.client.put(
                f'/calendars/{calendar_id}/sync',
                headers={'X-API-Key': 'test-api-key'}
            )
            
            # Check response
            self.assertEqual(sync_response.status_code, 200)
            sync_data = json.loads(sync_response.data)
            self.assertEqual(sync_data['status'], 'success')
    
    def test_sync_calendar_not_found(self):
        """Test syncing a non-existent calendar"""
        # Test sync endpoint with non-existent calendar ID
        sync_response = self.client.put(
            '/calendars/nonexistent/sync',
            headers={'X-API-Key': 'test-api-key'}
        )
        
        # Check response
        self.assertEqual(sync_response.status_code, 404)
        sync_data = json.loads(sync_response.data)
        self.assertIn('error', sync_data)
        self.assertEqual(sync_data['error']['code'], 404)

if __name__ == '__main__':
    unittest.main()