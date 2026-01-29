import tempfile
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.database import init_db, create_user, create_calendar, create_event, set_db_path
import sqlite3

def debug_user_id():
    """Debug user_id inclusion in database queries"""
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
    cal1 = create_calendar(user1.id, 'http://example.com/cal1.ics')
    
    # Add event using SQLite's datetime function
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT datetime('now', '+5 minutes') as event_time")
    event_time = cursor.fetchone()[0]
    conn.close()
    
    event1 = create_event(cal1.id, 'event1', 'Test Event 1', '', '', event_time, event_time, False)
    
    # Check the database directly
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Test the query that includes user_id
    cursor.execute('''
        SELECT e.*, u.user_id as user_id FROM events e
        JOIN calendars c ON e.calendar_id = c.id
        JOIN users u ON c.user_id = u.id
        WHERE e.notified = FALSE
    ''')
    
    rows = cursor.fetchall()
    print(f"Found {len(rows)} events with user_id join")
    for row in rows:
        print(f"  - Event: {row['title']}")
        print(f"    user_id: {row['user_id']}")
        print(f"    All columns: {list(row.keys())}")
    
    conn.close()
    
    # Clean up
    os.unlink(db_path)

if __name__ == '__main__':
    debug_user_id()