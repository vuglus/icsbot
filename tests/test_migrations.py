import sys
import os
import tempfile
import sqlite3
import pytest

# Add the services directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.database import init_db, set_db_path, set_db_provider
from migrations.migration_manager import MigrationManager
from database_provider import DatabaseProvider

def test_migration_framework():
    """Test the migration framework"""
    # Create a temporary database for testing
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # Set the database path to our temporary file
        set_db_path(temp_db.name)
        set_db_provider('sqlite')
        
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
        set_db_provider('sqlite')
        
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
        
        # Create a user
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", ("test_user",))
        user_id = cursor.lastrowid
        conn.commit()
        
        # Insert duplicate calendars directly
        cursor.execute(
            'INSERT INTO calendars (id, user_id, url) VALUES (?, ?, ?)',
            (1, user_id, "http://example.com/calendar.ics")
        )
        calendar_id_1 = cursor.lastrowid
        
        cursor.execute(
            'INSERT INTO calendars (id, user_id, url) VALUES (?, ?, ?)',
            (2, user_id, "http://example.com/calendar.ics")
        )
        calendar_id_2 = cursor.lastrowid
        
        cursor.execute(
            'INSERT INTO calendars (id, user_id, url) VALUES (?, ?, ?)',
            (3, user_id, "http://example.com/calendar2.ics")
        )
        calendar_id_3 = cursor.lastrowid
        
        conn.commit()
        
        # Verify we have duplicates
        cursor.execute("SELECT COUNT(*) FROM calendars")
        count_before = cursor.fetchone()[0]
        print(f"Calendars before migration: {count_before}")
        assert count_before == 3, f"Expected 3 calendars before migration, but found {count_before}"
        
        # Close the connection
        conn.close()
        
        # Run the migration manager
        # For this test, we'll manually run the remove duplicates migration
        from migrations.sqlite.remove_calendar_duplicates import RemoveCalendarDuplicatesMigration
        migration = RemoveCalendarDuplicatesMigration()
        
        # Create a new connection for the migration
        conn = sqlite3.connect(temp_db.name)
        migration.run(conn)
        conn.close()
        
        # Verify duplicates were removed
        conn = sqlite3.connect(temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM calendars")
        count_after = cursor.fetchone()[0]
        print(f"Calendars after migration: {count_after}")
        assert count_after == 2, f"Expected 2 calendars after migration, but found {count_after}"
        
        # Check which calendars remain
        cursor.execute("SELECT id FROM calendars ORDER BY id")
        remaining_ids = [row[0] for row in cursor.fetchall()]
        assert 1 in remaining_ids, "First calendar should be kept"
        assert 2 not in remaining_ids, "Duplicate calendar should be removed"
        assert 3 in remaining_ids, "Unique calendar should be kept"
        
        conn.close()
        
        print("Test passed: Remove calendar duplicates migration works correctly")
        
    finally:
        # Clean up the temporary database
        try:
            os.unlink(temp_db.name)
        except:
            pass  # Ignore errors during cleanup

if __name__ == "__main__":
    try:
        test_migration_framework()
        test_remove_calendar_duplicates_migration()
        print("All migration tests passed!")
    except Exception as e:
        print(f"Migration tests failed: {e}")
        sys.exit(1)