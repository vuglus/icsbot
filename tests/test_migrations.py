import sys
import os
import tempfile
import sqlite3

# Add the services directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.database import init_db, create_user, create_calendar, get_calendars, set_db_path
from migrations.migration_manager import init_migration_table, get_executed_migrations, record_migration
from migrations.remove_calendar_duplicates import run as run_remove_calendar_duplicates

def test_migration_framework():
    """Test the migration framework"""
    # Create a temporary database for testing
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # Set the database path to our temporary file
        set_db_path(temp_db.name)
        
        # Initialize the database
        init_db()
        
        # Check that migrations table was created
        conn = sqlite3.connect(temp_db.name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
        table_exists = cursor.fetchone()
        assert table_exists is not None, "Migrations table should exist"
        
        # Close the connection before proceeding
        conn.close()
        
        print("Test passed: Migration framework works correctly")
        return True
        
    finally:
        # Clean up the temporary database
        try:
            os.unlink(temp_db.name)
        except:
            pass  # Ignore errors during cleanup

def test_remove_calendar_duplicates_migration():
    """Test the remove_calendar_duplicates migration"""
    # Create a temporary database for testing
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # Set the database path to our temporary file
        set_db_path(temp_db.name)
        
        # Initialize the database without running migrations
        conn = sqlite3.connect(temp_db.name)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create calendars table WITHOUT the unique constraint for testing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                last_sync_at TIMESTAMP,
                sync_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calendar_id INTEGER NOT NULL,
                uid TEXT NOT NULL,
                title TEXT,
                description TEXT,
                location TEXT,
                start_datetime TIMESTAMP NOT NULL,
                end_datetime TIMESTAMP NOT NULL,
                all_day BOOLEAN DEFAULT FALSE,
                notified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (calendar_id) REFERENCES calendars (id) ON DELETE CASCADE
            )
        ''')
        
        # Create migrations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Create a user
        user = create_user("test_user")
        
        # Manually insert duplicate calendars
        conn = sqlite3.connect(temp_db.name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Insert duplicate calendars directly
        cursor.execute(
            'INSERT INTO calendars (id, user_id, url) VALUES (?, ?, ?)',
            (1, user.id, "http://example.com/calendar.ics")
        )
        calendar_id_1 = cursor.lastrowid
        
        cursor.execute(
            'INSERT INTO calendars (id, user_id, url) VALUES (?, ?, ?)',
            (2, user.id, "http://example.com/calendar.ics")
        )
        calendar_id_2 = cursor.lastrowid
        
        cursor.execute(
            'INSERT INTO calendars (id, user_id, url) VALUES (?, ?, ?)',
            (3, user.id, "http://example.com/calendar2.ics")
        )
        calendar_id_3 = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Verify we have duplicates
        calendars_before = get_calendars()
        print(f"Calendars before migration: {len(calendars_before)}")
        assert len(calendars_before) == 3, f"Expected 3 calendars before migration, but found {len(calendars_before)}"
        
        # Run the migration
        run_remove_calendar_duplicates()
        
        # Reinitialize database connection to get fresh data
        set_db_path(temp_db.name)
        
        # Verify duplicates were removed
        calendars_after = get_calendars()
        print(f"Calendars after migration: {len(calendars_after)}")
        assert len(calendars_after) == 2, f"Expected 2 calendars after migration, but found {len(calendars_after)}"
        
        # Verify that the first calendar (smallest ID) was kept
        calendar_ids_after = [c.id for c in calendars_after]
        assert calendar_id_1 in calendar_ids_after, "First calendar should be kept"
        assert calendar_id_2 not in calendar_ids_after, "Duplicate calendar should be removed"
        assert calendar_id_3 in calendar_ids_after, "Unique calendar should be kept"
        
        print("Test passed: Remove calendar duplicates migration works correctly")
        return True
        
    finally:
        # Clean up the temporary database
        try:
            os.unlink(temp_db.name)
        except:
            pass  # Ignore errors during cleanup

if __name__ == "__main__":
    test_migration_framework()
    test_remove_calendar_duplicates_migration()
    print("All migration tests passed!")