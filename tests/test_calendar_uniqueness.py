import unittest
import tempfile
import os
from services.database import init_db, get_db_connection, create_user, create_calendar

class TestCalendarUniqueness(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Set the database path
        from services.database import set_db_path
        set_db_path(self.temp_db.name)
        
        # Initialize the database
        init_db()
    
    def tearDown(self):
        # Clean up the temporary database
        os.unlink(self.temp_db.name)
    
    def test_calendar_unique_constraint(self):
        """Test that calendar uniqueness constraint works correctly"""
        # Create a user
        user = create_user("test_user")
        
        # Create a calendar
        calendar1 = create_calendar(user.id, "https://example.com/calendar.ics")
        
        # Try to create another calendar with the same user_id and URL
        # This should either return the existing calendar or raise an exception
        try:
            calendar2 = create_calendar(user.id, "https://example.com/calendar.ics")
            # If we get here, it should be the same calendar
            self.assertEqual(calendar1.id, calendar2.id)
        except Exception as e:
            # If an exception is raised, it should be related to the unique constraint
            # This is also acceptable behavior
            pass
        
        # Verify only one calendar exists with this user_id and URL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT COUNT(*) as count FROM calendars WHERE user_id = ? AND url = ?',
            (user.id, "https://example.com/calendar.ics")
        )
        count = cursor.fetchone()['count']
        conn.close()
        
        # Should have exactly one calendar
        self.assertEqual(count, 1)
    
    def test_calendars_with_different_urls_allowed(self):
        """Test that calendars with different URLs for the same user are allowed"""
        # Create a user
        user = create_user("test_user")
        
        # Create two calendars with different URLs
        calendar1 = create_calendar(user.id, "https://example.com/calendar1.ics")
        calendar2 = create_calendar(user.id, "https://example.com/calendar2.ics")
        
        # Should be different calendars
        self.assertNotEqual(calendar1.id, calendar2.id)
        
        # Verify both calendars exist
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM calendars WHERE user_id = ?', (user.id,))
        count = cursor.fetchone()['count']
        conn.close()
        
        # Should have exactly two calendars
        self.assertEqual(count, 2)

if __name__ == '__main__':
    unittest.main()