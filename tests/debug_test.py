import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import from services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.database import init_db, create_user, create_calendar, create_event, get_pending_events

def debug_test():
    # Use an in-memory database for testing
    os.environ['DB_PATH'] = ':memory:'
    
    # Set a larger notification window for testing
    os.environ['NOTIFY_BEFORE_MINUTES'] = '60'
    
    # Initialize the database
    init_db()
    
    # Create users
    user1 = create_user('user1')
    user2 = create_user('user2')
    
    # Create calendars
    calendar1 = create_calendar(user1.id, 'http://example.com/cal1.ics')
    calendar2 = create_calendar(user2.id, 'http://example.com/cal2.ics')
    
    # Create events that are in the future but within the notification window
    future_time = (datetime.now() + timedelta(minutes=30)).isoformat()
    
    event1 = create_event(
        calendar1.id, 
        'event1', 
        'User 1 Event', 
        'Description 1', 
        'Location 1',
        future_time, 
        future_time, 
        False
    )
    
    event2 = create_event(
        calendar2.id, 
        'event2', 
        'User 2 Event', 
        'Description 2', 
        'Location 2',
        future_time, 
        future_time, 
        False
    )
    
    print(f"Created event1: {event1.title} at {event1.start_datetime}")
    print(f"Created event2: {event2.title} at {event2.start_datetime}")
    
    # Print current time for reference
    current_time = datetime.now().isoformat()
    print(f"Current time: {current_time}")
    
    # Let's also check all events in the database
    from services.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events')
    rows = cursor.fetchall()
    print(f"Total events in database: {len(rows)}")
    for row in rows:
        print(f"  - Event {row['id']}: {row['title']} at {row['start_datetime']}")
    conn.close()
    
    # Check pending events
    pending_events = get_pending_events()
    print(f"Found {len(pending_events)} pending events:")
    for event in pending_events:
        print(f"  - {event.title} at {event.start_datetime}")
    
    # Check pending events for user1
    pending_events_user1 = get_pending_events('user1')
    print(f"Found {len(pending_events_user1)} pending events for user1:")
    for event in pending_events_user1:
        print(f"  - {event.title} at {event.start_datetime}")

if __name__ == '__main__':
    debug_test()