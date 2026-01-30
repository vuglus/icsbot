import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.database import init_db, create_user, create_calendar, create_event, set_db_path
from services.api_service import get_pending_events_for_api
from services.config_service import get_api_key

def test_api_user_filtering_logic():
    """Test the API user filtering logic without running the actual service"""
    # Create a temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    db_path = temp_db.name
    
    try:
        # Set the database path
        set_db_path(db_path)
        
        # Initialize the database
        init_db()
        
        # Add test data
        user1 = create_user('user1')
        user2 = create_user('user2')
        
        # Add calendars
        cal1 = create_calendar(user1.id, 'http://example.com/cal1.ics')
        cal2 = create_calendar(user2.id, 'http://example.com/cal2.ics')
        
        # Add events for 5 minutes from now
        event_time = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        create_event(cal1.id, 'event1', 'Test Event 1', '', '', event_time, event_time, False)
        create_event(cal2.id, 'event2', 'Test Event 2', '', '', event_time, event_time, False)
        
        # Test the API logic without user filter
        events_all = get_pending_events_for_api()
        print(f"Found {len(events_all)} events without user filter")
        for event in events_all:
            print(f"  - {event.title} for user {event.user_id}")
        
        # Test the API logic with user1 filter
        events_user1 = get_pending_events_for_api('user1')
        print(f"Found {len(events_user1)} events for user1")
        for event in events_user1:
            print(f"  - {event.title}")
        
        # Test the API logic with user2 filter
        events_user2 = get_pending_events_for_api('user2')
        print(f"Found {len(events_user2)} events for user2")
        for event in events_user2:
            print(f"  - {event.title}")
        
        # Test the API logic with nonexistent user
        try:
            events_nonexistent = get_pending_events_for_api('nonexistent')
            print(f"Found {len(events_nonexistent)} events for nonexistent user (unexpected)")
        except ValueError as e:
            print(f"Correctly caught error for nonexistent user: {e}")
        
        # Verify results
        assert len(events_all) == 2, f"Expected 2 events, got {len(events_all)}"
        assert len(events_user1) == 1, f"Expected 1 event for user1, got {len(events_user1)}"
        assert len(events_user2) == 1, f"Expected 1 event for user2, got {len(events_user2)}"
        
        # Verify event titles
        if events_user1:
            assert events_user1[0].title == 'Test Event 1', f"Expected 'Test Event 1', got '{events_user1[0].title}'"
        if events_user2:
            assert events_user2[0].title == 'Test Event 2', f"Expected 'Test Event 2', got '{events_user2[0].title}'"
            
        print("All tests passed!")
        
    finally:
        # Clean up
        os.unlink(db_path)

if __name__ == '__main__':
    # Mock the API key for testing
    with patch('services.config_service.get_api_key', return_value='test-api-key'):
        test_api_user_filtering_logic()