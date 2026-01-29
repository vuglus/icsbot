import sys
import os
import tempfile

# Add the services directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.database import init_db, create_user, create_calendar, get_calendars, set_db_path
import sqlite3

def test_calendar_uniqueness():
    """Test that duplicate calendar entries are prevented"""
    # Create a temporary database for testing
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # Set the database path to our temporary file
        set_db_path(temp_db.name)
        
        # Initialize the database
        init_db()
        
        # Create a user
        user = create_user("test_user")
        
        # Create a calendar
        calendar1 = create_calendar(user.id, "http://example.com/calendar.ics")
        print(f"Created calendar 1 with ID: {calendar1.id}")
        
        # Try to create the same calendar again
        calendar2 = create_calendar(user.id, "http://example.com/calendar.ics")
        print(f"Created calendar 2 with ID: {calendar2.id}")
        
        # Verify that both calendars have the same ID
        assert calendar1.id == calendar2.id, f"Calendar IDs don't match: {calendar1.id} != {calendar2.id}"
        
        # Verify that only one calendar exists in the database
        calendars = get_calendars()
        assert len(calendars) == 1, f"Expected 1 calendar, but found {len(calendars)}"
        
        print("Test passed: Duplicate calendar prevention works correctly")
        return True
        
    finally:
        # Clean up the temporary database
        os.unlink(temp_db.name)

if __name__ == "__main__":
    test_calendar_uniqueness()