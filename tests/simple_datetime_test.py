import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import from services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.database import get_db_connection

def simple_datetime_test():
    # Use an in-memory database for testing
    os.environ['DB_PATH'] = ':memory:'
    
    # Initialize the database
    from services.database import init_db
    init_db()
    
    # Get current time
    current_time = datetime.utcnow()
    future_time = current_time + timedelta(minutes=5)
    
    print(f"Current time: {current_time.isoformat()}")
    print(f"Future time: {future_time.isoformat()}")
    
    # Insert a test event
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create a simple events table for testing
    cursor.execute('''
        CREATE TABLE test_events (
            id INTEGER PRIMARY KEY,
            start_datetime TEXT
        )
    ''')
    
    # Insert the future time
    cursor.execute('''
        INSERT INTO test_events (start_datetime) VALUES (?)
    ''', (future_time.isoformat(),))
    
    conn.commit()
    
    # Test different datetime comparisons
    print("\nTesting datetime comparisons:")
    
    # Test 1: Direct comparison
    cursor.execute('''
        SELECT id, start_datetime,
               start_datetime > datetime('now') as is_future,
               start_datetime <= datetime('now', '+60 minutes') as is_within_window
        FROM test_events
    ''')
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"  Event {row['id']}: {row['start_datetime']}")
        print(f"    Is future: {row['is_future']}, Is within window: {row['is_within_window']}")
    
    # Test 2: Using julianday
    cursor.execute('''
        SELECT id, start_datetime,
               julianday(start_datetime) > julianday(datetime('now')) as is_future,
               julianday(start_datetime) <= julianday(datetime('now', '+60 minutes')) as is_within_window
        FROM test_events
    ''')
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"  Event {row['id']}: {row['start_datetime']}")
        print(f"    Is future (julianday): {row['is_future']}, Is within window (julianday): {row['is_within_window']}")
    
    conn.close()

if __name__ == '__main__':
    simple_datetime_test()