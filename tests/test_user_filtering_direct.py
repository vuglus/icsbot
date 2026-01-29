import tempfile
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.database import init_db, create_user, create_calendar, create_event, get_pending_events, set_db_path
from services.notification_service import get_pending_events_for_api

def test_user_filtering_direct():
    """Test user filtering functionality directly"""
    # Create a temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    db_path = temp_db.name
    
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
    
    # Add events for 5 minutes from now (within the default 10-minute notification window)
    # Use SQLite's datetime function to ensure consistency
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT datetime('now', '+5 minutes') as event_time")
    event_time = cursor.fetchone()[0]
    conn.close()
    
    event1 = create_event(cal1.id, 'event1', 'Test Event 1', '', '', event_time, event_time, False)
    event2 = create_event(cal2.id, 'event2', 'Test Event 2', '', '', event_time, event_time, False)
    
    # Test getting all pending events
    all_events = get_pending_events()
    print(f"Found {len(all_events)} total pending events")
    for event in all_events:
        print(f"  - {event.title}")
        # Print all attributes of the event
        print(f"    Attributes: {vars(event)}")
    
    # Test getting pending events for user1
    user1_events = get_pending_events('user1')
    print(f"Found {len(user1_events)} pending events for user1")
    for event in user1_events:
        print(f"  - {event.title}")
        # Print all attributes of the event
        print(f"    Attributes: {vars(event)}")
    
    # Test getting pending events for user2
    user2_events = get_pending_events('user2')
    print(f"Found {len(user2_events)} pending events for user2")
    for event in user2_events:
        print(f"  - {event.title}")
        # Print all attributes of the event
        print(f"    Attributes: {vars(event)}")
    
    # Test getting pending events for nonexistent user
    try:
        nonexistent_events = get_pending_events('nonexistent')
        print(f"Found {len(nonexistent_events)} pending events for nonexistent user (unexpected)")
    except ValueError as e:
        print(f"Correctly caught error for nonexistent user: {e}")
    
    # Test the API function
    api_all_events = get_pending_events_for_api()
    print(f"API found {len(api_all_events)} total pending events")
    
    api_user1_events = get_pending_events_for_api('user1')
    print(f"API found {len(api_user1_events)} pending events for user1")
    
    # Check that user_id is included in the events
    if api_user1_events:
        event = api_user1_events[0]
        print(f"API event attributes: {vars(event)}")
        if hasattr(event, 'user_id'):
            print(f"Event includes user_id: {event.user_id}")
        else:
            print("Event does not include user_id")
    
    # Clean up
    os.unlink(db_path)
    
    # Verify results
    assert len(all_events) == 2, f"Expected 2 total events, got {len(all_events)}"
    assert len(user1_events) == 1, f"Expected 1 event for user1, got {len(user1_events)}"
    assert len(user2_events) == 1, f"Expected 1 event for user2, got {len(user2_events)}"
    assert user1_events[0].title == 'Test Event 1', f"Expected 'Test Event 1', got '{user1_events[0].title}'"
    assert user2_events[0].title == 'Test Event 2', f"Expected 'Test Event 2', got '{user2_events[0].title}'"
    
    print("All tests passed!")

if __name__ == '__main__':
    test_user_filtering_direct()