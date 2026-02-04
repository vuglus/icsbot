import unittest
import tempfile
import os
import json
from datetime import datetime, timezone, timedelta
from flask import Flask
from flask_smorest import Api
from services.api_service import get_app, initialize_api
from services.database import init_db, create_user, create_calendar, create_event
from services.database import set_db_path
from services.api_service import get_app

class TestCalendarTimezoneAPI(unittest.TestCase):
    def setUp(self):
        # Set API key for testing
        os.environ['ICS_GATE_API_KEY'] = 'test-api-key'
        
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        set_db_path(self.temp_db.name)
        
        # Initialize the database
        init_db()

                
        # Create a test user
        self.user = create_user("test_user")
        
        # Create a calendar with timezone
        self.calendar = create_calendar(self.user.id, "https://example.com/calendar.ics")
        # Create an event for 1 hour from now

        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        start_time = future_time.replace(second=0, microsecond=0)
        end_time = (future_time + timedelta(hours=1)).replace(second=0, microsecond=0)
        
        self.event = create_event(
            calendar_id=self.calendar.id,
            uid="test-event-123",
            title="Test Event",
            description="Test event description",
            location="Test Location",
            start_datetime=start_time.isoformat(),
            end_datetime=end_time.isoformat(),
            all_day=False
        )
        
        # Set up Flask app for testing
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["API_TITLE"] = "ICS Bot API"
        self.app.config["API_VERSION"] = "v1"
        self.app.config["OPENAPI_VERSION"] = "3.0.2"        
        # Initialize API endpoints
        api = Api(self.app)
        initialize_api(api)

        # Create Flask test client
        self.client = self.app.test_client()
        
    def tearDown(self):
        # Clean up the temporary database
        os.unlink(self.temp_db.name)
        
    def test_get_events_pending_includes_timezone(self):
        """Test that the /events/pending endpoint includes timezone information"""
        # Make a request to the API with API key
        response = self.client.get(f"/events/pending?user_id={self.user.user_id}", headers={'X-API-Key': 'test-api-key'})
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.data)
        
        # Check that we have events in the response
        self.assertIn('events', data)
        
        # Check that the event has timezone information
        events = data['events']
        self.assertGreater(len(events), 0)
        
        # Check the first event
        event = events[0]
        self.assertIn('calendar_timezone', event)
        self.assertEqual(event['calendar_timezone'], 'GMT+3')
        
        # Check that datetime values are in the correct format
        self.assertIn('start_datetime', event)
        self.assertIn('end_datetime', event)
        
        # The datetime values should include timezone information
        self.assertIn('+03:00', event['start_datetime'])
        self.assertIn('+03:00', event['end_datetime'])

if __name__ == '__main__':
    unittest.main()