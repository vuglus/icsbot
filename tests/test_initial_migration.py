import unittest
import sqlite3
import os
import tempfile
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database import Database
from services.database_provider import DatabaseProvider
from services.config_service import Config
from migrations.migration_manager import MigrationManager


class TestInitialMigration(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        logging.basicConfig(level=logging.INFO)

    def tearDown(self):
        os.unlink(self.temp_db.name)

    def test_initial_migration_creates_tables(self):
        """Test that the initial migration creates all required tables"""
        config = Config(
            {
                "DB_PATH": self.temp_db.name,
                "DB_PROVIDER": "sqlite",
            }
        )

        provider = DatabaseProvider(config)
        db = Database(provider, config)

        conn = provider.getConnection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='calendars'"
        )
        self.assertIsNotNone(cursor.fetchone(), "calendars table should exist")

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sent_notifications'"
        )
        self.assertIsNotNone(cursor.fetchone(), "sent_notifications table should exist")

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'"
        )
        self.assertIsNotNone(cursor.fetchone(), "migrations table should exist")

        conn.close()

    def test_old_tables_do_not_exist(self):
        """Test that old tables (users, events) are not created"""
        config = Config(
            {
                "DB_PATH": self.temp_db.name,
                "DB_PROVIDER": "sqlite",
            }
        )

        provider = DatabaseProvider(config)
        db = Database(provider, config)

        conn = provider.getConnection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        self.assertIsNone(cursor.fetchone(), "users table should NOT exist")

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
        )
        self.assertIsNone(cursor.fetchone(), "events table should NOT exist")

        conn.close()

    def test_init_db_runs_migrations(self):
        """Test that init_db function runs migrations successfully"""
        config = Config(
            {
                "DB_PATH": self.temp_db.name,
                "DB_PROVIDER": "sqlite",
            }
        )

        provider = DatabaseProvider(config)
        db = Database(provider, config)

        conn = provider.getConnection()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        self.assertGreater(len(tables), 0, "Should have created at least one table")

        conn.close()


if __name__ == "__main__":
    unittest.main()
