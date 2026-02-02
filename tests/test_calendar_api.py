import unittest
import json
import tempfile
import os
from unittest.mock import patch
from flask import Flask
from services.api_service import get_app
from services.database import init_db, set_db_path, create_user, create_calendar, get_calendars
import sys

class TestCalendarAPI(unittest.TestCase):
    """Test cases for calendar API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        # Set API key for testing
        os.environ['ICS_GATE_API_KEY'] = 'test-api-key'
        
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        set_db_path(self.temp_db.name)
        
        # Initialize database
        init_db()
        
        # Set up Flask app for testing
        self.app = get_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
    def tearDown(self):
        """Tear down test environment"""
        # Clean up temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
            
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
        self.assertEqual(data['calendar']['user_id'], 1)  # First user gets ID 1
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
        calendars = get_calendars()
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
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 400)
        
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

if __name__ == '__main__':
    unittest.main()