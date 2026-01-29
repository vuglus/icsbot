#!/usr/bin/env python3
"""
Core functionality tests for ICS-Gate
"""

import os
import sys
import tempfile
import yaml
from datetime import datetime, timedelta

# Add the current directory to the path so we can import app.py
sys.path.insert(0, '.')

# Import the services directly for testing
from services.database import init_db, create_user, get_db_connection
from services.ics_parser import parse_ics_content
from services.config_service import load_config

def test_database_initialization():
    """Test database initialization"""
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        tmp_db_path = tmp_db.name
    
    try:
        # Set the database path to the temporary file
        import services.database as db_service
        db_service.DB_PATH = tmp_db_path
        
        # Initialize the database
        init_db()
        
        # Check that tables were created
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check that users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is not None, "Users table not created"
        
        # Check that calendars table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='calendars'")
        assert cursor.fetchone() is not None, "Calendars table not created"
        
        # Check that events table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
        assert cursor.fetchone() is not None, "Events table not created"
        
        conn.close()
        
        print("✓ Database initialization test passed")
        
    finally:
        # Clean up the temporary database file
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)

def test_user_creation():
    """Test user creation"""
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        tmp_db_path = tmp_db.name
    
    try:
        # Set the database path to the temporary file
        import services.database as db_service
        db_service.DB_PATH = tmp_db_path
        init_db()
        
        # Create a user
        user = create_user("test_user_123")
        assert user.id is not None, "User ID should not be None"
        assert user.user_id == "test_user_123", "User ID should match"
        
        # Try to create the same user again (should return existing)
        user2 = create_user("test_user_123")
        assert user2.id == user.id, "Should return the same user"
        
        print("✓ User creation test passed")
        
    finally:
        # Clean up the temporary database file
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)

def test_ics_parsing():
    """Test ICS parsing"""
    # Sample ICS content
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:1234567890@example.com
DTSTART:20230615T100000Z
DTEND:20230615T110000Z
SUMMARY:Team Meeting
DESCRIPTION:Weekly team meeting to discuss project progress
LOCATION:Conference Room 3
END:VEVENT
END:VCALENDAR"""
    
    # Parse the ICS content
    events = parse_ics_content(ics_content)
    
    # Check that we got one event
    assert len(events) == 1, f"Expected 1 event, got {len(events)}"
    
    # Check event properties
    event = events[0]
    assert event['uid'] == '1234567890@example.com', f"Unexpected UID: {event['uid']}"
    assert event['summary'] == 'Team Meeting', f"Unexpected summary: {event['summary']}"
    assert event['description'] == 'Weekly team meeting to discuss project progress', f"Unexpected description: {event['description']}"
    assert event['location'] == 'Conference Room 3', f"Unexpected location: {event['location']}"
    assert event['start'] is not None, "Start time should not be None"
    assert event['end'] is not None, "End time should not be None"
    
    print("✓ ICS parsing test passed")

def test_config_loading():
    """Test configuration loading"""
    # Create a temporary config file
    config_data = {
        'api_key': 'test-api-key',
        'SYNC_INTERVAL_MINUTES': 10,
        'NOTIFY_INTERVAL_SECONDS': 30,
        'calendars': {
            'user1': 'https://example.com/calendar1.ics',
            'user2': 'https://example.com/calendar2.ics'
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as tmp_config:
        yaml.dump(config_data, tmp_config)
        tmp_config_path = tmp_config.name
    
    try:
        # Set the config path
        import services.config_service as config_service
        config_service.CONFIG_PATH = tmp_config_path
        
        # Load the configuration
        config = load_config()
        
        # Check that the configuration was loaded correctly
        assert config['api_key'] == 'test-api-key', "API key should match"
        assert config['SYNC_INTERVAL_MINUTES'] == 10, "Sync interval should match"
        assert config['NOTIFY_INTERVAL_SECONDS'] == 30, "Notify interval should match"
        assert 'calendars' in config, "Calendars should be in config"
        assert len(config['calendars']) == 2, "Should have 2 calendars"
        
        print("✓ Configuration loading test passed")
        
    finally:
        # Clean up the temporary config file
        if os.path.exists(tmp_config_path):
            os.unlink(tmp_config_path)

def run_all_tests():
    """Run all tests"""
    print("Running core functionality tests...")
    
    test_database_initialization()
    test_user_creation()
    test_ics_parsing()
    test_config_loading()
    
    print("All tests passed! ✓")

if __name__ == '__main__':
    run_all_tests()