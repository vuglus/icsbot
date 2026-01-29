import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import from services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.database import init_db, create_user, create_calendar, create_event, get_db_connection

def debug_query():
    # Use an in-memory database for testing
    os.environ['DB_PATH'] = ':memory:'
    
    # Set a larger notification window for testing
    os.environ['NOTIFY_BEFORE_MINUTES'] = '60'  # 1 hour
    
    # Initialize the database
    init_db()
    
    # Create users
    user1 = create_user('user1')
    user2 = create_user('user2')
    
    # Create calendars
    calendar1 = create_calendar(user1.id, 'http://example.com/cal1.ics')
    calendar2 = create_calendar(user2.id, 'http://example.com/cal2.ics')
    
    # Create events that are in the future but within the notification window
    # Create events that are 5 minutes in the future (within the 60-minute window)
    # Make sure to use UTC time to match the database
    future_time = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    
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
    
    # Execute the query directly
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate notification window (10 minutes before event by default)
    notify_before_minutes = int(os.environ.get('NOTIFY_BEFORE_MINUTES', 10))
    print(f"Notification window: {notify_before_minutes} minutes")
    
    # Test 1: Get all events
    cursor.execute('SELECT * FROM events')
    rows = cursor.fetchall()
    print(f"Total events: {len(rows)}")
    
    # Test 2: Check datetime comparisons
    cursor.execute("SELECT datetime('now'), datetime('now', '+' || ? || ' minutes')", (notify_before_minutes,))
    time_result = cursor.fetchone()
    print(f"Current time in DB: {time_result[0]}")
    print(f"Current time + {notify_before_minutes} minutes in DB: {time_result[1]}")
    
    # Test 3: Check if events are in the future
    cursor.execute('''
        SELECT id, title, start_datetime,
               julianday(start_datetime) > julianday(datetime('now')) as is_future,
               julianday(start_datetime) <= julianday(datetime('now')) + (? / 1440.0) as is_within_window,
               (julianday(start_datetime) - julianday(datetime('now'))) * 1440 as minutes_diff
        FROM events
        ORDER BY id DESC
        LIMIT 5
    ''', (notify_before_minutes,))
    
    rows = cursor.fetchall()
    print("Event datetime checks (last 5 events):")
    for row in rows:
        print(f"  - Event {row['id']}: {row['title']} at {row['start_datetime']}")
        print(f"    Is future: {row['is_future']}, Is within window: {row['is_within_window']}")
        print(f"    Minutes difference: {row['minutes_diff']}")
    
    # Test 4: Execute the query without user filter (using the new julianday logic)
    cursor.execute('''
        SELECT * FROM events
        WHERE notified = FALSE
          AND julianday(start_datetime) <= julianday(datetime('now')) + (? / 1440.0)
          AND julianday(start_datetime) > julianday(datetime('now'))
        ORDER BY start_datetime ASC
    ''', (notify_before_minutes,))
    
    rows = cursor.fetchall()
    print(f"Found {len(rows)} pending events without user filter:")
    for row in rows:
        print(f"  - Event {row['id']}: {row['title']} at {row['start_datetime']}")
    
    # Test 5: Execute the query with user filter (using the new julianday logic)
    cursor.execute('''
        SELECT e.id, e.title, e.start_datetime FROM events e
        JOIN calendars c ON e.calendar_id = c.id
        JOIN users u ON c.user_id = u.id
        WHERE e.notified = FALSE
          AND julianday(e.start_datetime) <= julianday(datetime('now')) + (? / 1440.0)
          AND julianday(e.start_datetime) > julianday(datetime('now'))
          AND u.user_id = ?
        ORDER BY e.start_datetime ASC
    ''', (notify_before_minutes, 'user1'))
    
    rows = cursor.fetchall()
    print(f"Found {len(rows)} pending events for user1:")
    for row in rows:
        print(f"  - Event {row['id']}: {row['title']} at {row['start_datetime']}")
    
    # Test 6: Test the actual get_pending_events function
    print("\nTesting the actual get_pending_events function:")
    from services.database import get_pending_events
    pending_events = get_pending_events()
    print(f"Found {len(pending_events)} pending events using get_pending_events():")
    for event in pending_events:
        print(f"  - Event {event.id}: {event.title} at {event.start_datetime}")
    
    pending_events_user1 = get_pending_events('user1')
    print(f"Found {len(pending_events_user1)} pending events for user1 using get_pending_events('user1'):")
    for event in pending_events_user1:
        print(f"  - Event {event.id}: {event.title} at {event.start_datetime}")
    
    conn.close()

if __name__ == '__main__':
    debug_query()