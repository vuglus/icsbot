import unittest
import tempfile
import os
from datetime import datetime, timedelta
import sys
import sqlite3

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.database import (
    init_db, 
    create_user, 
    create_calendar, 
    create_event,
    get_pending_events
)
from services.notification_service import get_pending_events_for_api

class TestUserFiltering(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Set the database path
        from services.database import set_db_path
        set_db_path(self.db_path)
        
        # Initialize the database
        init_db()
        
        # Add test data
        self.add_test_data()

    def tearDown(self):
        # Remove the temporary database file
        os.unlink(self.db_path)

    def add_test_data(self):
        # Add users
        user1 = create_user('user1')
        user2 = create_user('user2')
        
        # Add calendars
        cal1 = create_calendar(user1.id, 'http://example.com/cal1.ics')
        cal2 = create_calendar(user2.id, 'http://example.com/cal2.ics')
        
        # Add events using SQLite's datetime functions to ensure consistency
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add an event for user1 that should be pending (5 minutes from now)
        cursor.execute("SELECT datetime('now', '+5 minutes') as event_time")
        event_time1 = cursor.fetchone()[0]
        create_event(cal1.id, 'event1', 'Test Event 1', '', '', event_time1, event_time1, False)
        
        # Add an event for user2 that should be pending (10 minutes from now)
        cursor.execute("SELECT datetime('now', '+10 minutes') as event_time")
        event_time2 = cursor.fetchone()[0]
        create_event(cal2.id, 'event2', 'Test Event 2', '', '', event_time2, event_time2, False)
        
        conn.close()

    def test_get_pending_events_with_user_filter(self):
        """Test getting pending events filtered by user ID"""
        events = get_pending_events('user1')
        # Should get exactly 1 event for user1
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].title, 'Test Event 1')

    def test_get_pending_events_without_filter(self):
        """Test getting all pending events without filtering"""
        events = get_pending_events()
        # Should get both events
        self.assertEqual(len(events), 2)
        # Events should be ordered by start_datetime
        titles = [event.title for event in events]
        self.assertIn('Test Event 1', titles)
        self.assertIn('Test Event 2', titles)

    def test_get_pending_events_api_with_user_filter(self):
        """Test getting pending events through API with user filter"""
        events = get_pending_events_for_api('user1')
        # Should get exactly 1 event for user1
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].title, 'Test Event 1')

    def test_get_pending_events_api_without_filter(self):
        """Test getting all pending events through API without filter"""
        events = get_pending_events_for_api()
        # Should get both events
        self.assertEqual(len(events), 2)
        # Events should be ordered by start_datetime
        titles = [event.title for event in events]
        self.assertIn('Test Event 1', titles)
        self.assertIn('Test Event 2', titles)

    def test_user_not_found(self):
        """Test behavior when user is not found"""
        with self.assertRaises(ValueError):
            get_pending_events('nonexistent_user')

    def test_no_pending_events(self):
        """Test when there are no pending events"""
        # Mark all events as notified
        events = get_pending_events()
        from services.database import mark_event_notified
        for event in events:
            mark_event_notified(event.id)
        
        # Now there should be no pending events
        events = get_pending_events()
        self.assertEqual(len(events), 0)

if __name__ == '__main__':
    unittest.main()