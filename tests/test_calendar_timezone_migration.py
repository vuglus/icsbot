import unittest
import tempfile
import os
from services.database import Database
from services.database_provider import DatabaseProvider
from services.config_service import Config


class TestCalendarTimezoneMigration(unittest.TestCase):
    """Test migration framework works with new schema"""

    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

    def tearDown(self):
        """Tear down test environment"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_calendar_migration_framework(self):
        """Test that migration framework correctly creates tables"""
        config = Config(
            {
                "DB_PROVIDER": "sqlite",
                "DB_PATH": self.temp_db.name,
            }
        )

        provider = DatabaseProvider(config)
        db = Database(provider, config)

        calendar_entity, sent_notification_entity, migration_entity = (
            provider.get_entities()
        )

        calendar = calendar_entity.create_calendar(
            "test_chat", "tg", "https://example.com/test.ics"
        )

        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 1)

        self.assertEqual(calendars[0].chat_id, "test_chat")
        self.assertEqual(calendars[0].chat_type, "tg")

        provider.close()


if __name__ == "__main__":
    unittest.main()
