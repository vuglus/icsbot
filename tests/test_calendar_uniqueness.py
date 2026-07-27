import unittest
import tempfile
import os
from services.database import Database
from services.database_provider import DatabaseProvider
from services.config_service import Config
from entity.base import Calendar


class TestCalendarUniqueness(unittest.TestCase):
    """Test calendar uniqueness constraints"""

    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

    def tearDown(self):
        """Tear down test environment"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_calendar_uniqueness_constraint(self):
        """Test that duplicate (chat_id, url) returns existing calendar"""
        config = Config(
            {
                "DB_PROVIDER": "sqlite",
                "DB_PATH": self.temp_db.name,
            }
        )

        provider = DatabaseProvider(config)
        db = Database(provider, config)

        calendar_entity, _, _ = provider.get_entities()

        calendar1 = calendar_entity.create_calendar(
            "chat1", "tg", "https://example.com/test.ics"
        )
        self.assertIsInstance(calendar1, Calendar)
        self.assertIsNotNone(calendar1.id)

        calendar2 = calendar_entity.create_calendar(
            "chat1", "tg", "https://example.com/test.ics"
        )
        self.assertEqual(calendar1.id, calendar2.id)

        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 1)

        provider.close()

    def test_calendars_for_different_chats_can_have_same_url(self):
        """Test that calendars for different chats can have the same URL"""
        config = Config(
            {
                "DB_PROVIDER": "sqlite",
                "DB_PATH": self.temp_db.name,
            }
        )

        provider = DatabaseProvider(config)
        db = Database(provider, config)

        calendar_entity, _, _ = provider.get_entities()

        calendar1 = calendar_entity.create_calendar(
            "chat1", "tg", "https://example.com/test.ics"
        )
        calendar2 = calendar_entity.create_calendar(
            "chat2", "max", "https://example.com/test.ics"
        )

        self.assertIsInstance(calendar1, Calendar)
        self.assertIsInstance(calendar2, Calendar)
        self.assertIsNotNone(calendar1.id)
        self.assertIsNotNone(calendar2.id)
        self.assertNotEqual(calendar1.id, calendar2.id)

        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 2)

        provider.close()


if __name__ == "__main__":
    unittest.main()
