import requests
import tempfile
import os
import sys
import time
import threading
import subprocess
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.database import init_db, create_user, create_calendar, create_event, set_db_path

def test_api_integration():
    """Test the API integration with user filtering"""
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
    
    # Add events for 5 minutes from now
    event_time = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    event1 = create_event(cal1.id, 'event1', 'Test Event 1', '', '', event_time, event_time, False)
    event2 = create_event(cal2.id, 'event2', 'Test Event 2', '', '', event_time, event_time, False)
    
    # Set environment variables for the API
    os.environ['ICS_GATE_API_KEY'] = 'test-api-key'
    os.environ['DB_PATH'] = db_path
    
    # Start the API server in a separate process
    api_process = subprocess.Popen(['python', 'app.py'])
    
    # Wait a moment for the server to start
    time.sleep(3)
    
    try:
        # Test the API without user filter
        response = requests.get(
            'http://localhost:5800/events/pending',
            headers={'X-API-Key': 'test-api-key'}
        )
        print(f"API response without user filter: {response.status_code}")
        if response.status_code == 200:
            events = response.json()['events']
            print(f"Found {len(events)} events")
            for event in events:
                print(f"  - {event['title']} for user {event.get('user_id', 'unknown')}")
        
        # Test the API with user1 filter
        response = requests.get(
            'http://localhost:5800/events/pending?user_id=user1',
            headers={'X-API-Key': 'test-api-key'}
        )
        print(f"API response with user1 filter: {response.status_code}")
        if response.status_code == 200:
            events = response.json()['events']
            print(f"Found {len(events)} events for user1")
            for event in events:
                print(f"  - {event['title']} for user {event.get('user_id', 'unknown')}")
        
        # Test the API with user2 filter
        response = requests.get(
            'http://localhost:5800/events/pending?user_id=user2',
            headers={'X-API-Key': 'test-api-key'}
        )
        print(f"API response with user2 filter: {response.status_code}")
        if response.status_code == 200:
            events = response.json()['events']
            print(f"Found {len(events)} events for user2")
            for event in events:
                print(f"  - {event['title']} for user {event.get('user_id', 'unknown')}")
        
        # Test the API with nonexistent user
        response = requests.get(
            'http://localhost:5800/events/pending?user_id=nonexistent',
            headers={'X-API-Key': 'test-api-key'}
        )
        print(f"API response with nonexistent user: {response.status_code}")
        
    except Exception as e:
        print(f"Error during API test: {e}")
    finally:
        # Clean up
        api_process.terminate()
        api_process.wait()
        os.unlink(db_path)

if __name__ == '__main__':
    test_api_integration()