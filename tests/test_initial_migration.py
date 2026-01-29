import unittest
import sqlite3
import os
import tempfile
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database import init_db, get_db_connection, set_db_path
from migrations.migration_manager import run_all_migrations

class TestInitialMigration(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        set_db_path(self.temp_db.name)
        
        # Set up logging to see what's happening
        logging.basicConfig(level=logging.INFO)

    def tearDown(self):
        # Clean up the temporary database file
        os.unlink(self.temp_db.name)

    def test_initial_migration_creates_tables(self):
        """Test that the initial migration creates all required tables"""
        # Run the migrations
        run_all_migrations()
        
        # Check that tables were created
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check users table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        self.assertIsNotNone(cursor.fetchone(), "users table should exist")
        
        # Check calendars table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='calendars'")
        self.assertIsNotNone(cursor.fetchone(), "calendars table should exist")
        
        # Check events table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
        self.assertIsNotNone(cursor.fetchone(), "events table should exist")
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_calendars_user_id'")
        self.assertIsNotNone(cursor.fetchone(), "idx_calendars_user_id index should exist")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_events_calendar_id'")
        self.assertIsNotNone(cursor.fetchone(), "idx_events_calendar_id index should exist")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_events_start_datetime'")
        self.assertIsNotNone(cursor.fetchone(), "idx_events_start_datetime index should exist")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_events_notified'")
        self.assertIsNotNone(cursor.fetchone(), "idx_events_notified index should exist")
        
        conn.close()

    def test_init_db_runs_migrations(self):
        """Test that init_db function runs migrations successfully"""
        # This should run without errors
        init_db()
        
        # Check that tables were created
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check that at least one table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        self.assertGreater(len(tables), 0, "Should have created at least one table")
        
        conn.close()

if __name__ == '__main__':
    unittest.main()