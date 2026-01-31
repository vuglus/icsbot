import unittest
import tempfile
import os
from services.database import init_db, get_calendars, create_user, create_calendar, get_calendar_by_id
from services.database import set_db_path

class TestCalendarTimezoneMigration(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        set_db_path(self.temp_db.name)
        
        # Initialize the database
        init_db()
        
        # Create a test user
        self.user = create_user("test_user")
        
    def tearDown(self):
        # Clean up the temporary database
        os.unlink(self.temp_db.name)
        
    def test_calendar_timezone_field_exists(self):
        """Test that calendars have timezone field after migration"""
        # Create a calendar
        calendar = create_calendar(self.user.id, "https://example.com/calendar.ics")
        
        # Check that the calendar has a timezone field
        self.assertTrue(hasattr(calendar, 'timezone'))
        self.assertEqual(calendar.timezone, 'GMT+3')
        
    def test_get_calendars_includes_timezone(self):
        """Test that get_calendars returns timezone information"""
        # Create a calendar
        created_calendar = create_calendar(self.user.id, "https://example.com/calendar.ics")
        
        # Get all calendars
        calendars = get_calendars()
        
        # Check that we got the calendar back
        self.assertEqual(len(calendars), 1)
        
        # Check that the calendar has timezone information
        calendar = calendars[0]
        self.assertTrue(hasattr(calendar, 'timezone'))
        self.assertEqual(calendar.timezone, 'GMT+3')
        
    def test_get_calendar_by_id_includes_timezone(self):
        """Test that get_calendar_by_id returns timezone information"""
        # Create a calendar
        created_calendar = create_calendar(self.user.id, "https://example.com/calendar.ics")
        
        # Get the calendar by ID
        calendar = get_calendar_by_id(created_calendar.id)
        
        # Check that the calendar has timezone information
        self.assertTrue(hasattr(calendar, 'timezone'))
        self.assertEqual(calendar.timezone, 'GMT+3')

if __name__ == '__main__':
    unittest.main()