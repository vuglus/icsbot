import sys
import os
import tempfile
import sqlite3
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.database import Database
from services.database_provider import DatabaseProvider
from services.config_service import Config


def test_migration_framework():
    """Test the migration framework"""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    try:
        config = Config(
            {
                "DB_PATH": temp_db.name,
                "DB_PROVIDER": "sqlite",
            }
        )

        provider = DatabaseProvider(config)
        db = Database(provider, config)

        conn = sqlite3.connect(temp_db.name)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'"
        )
        table_exists = cursor.fetchone()
        assert table_exists is not None, "Migrations table should exist"

        conn.close()

        print("Test passed: Migration framework works correctly")

    finally:
        try:
            os.unlink(temp_db.name)
        except:
            pass
