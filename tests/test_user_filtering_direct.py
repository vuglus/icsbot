import unittest
import tempfile
import os
from services.database import Database
from services.database_provider import DatabaseProvider
from services.config_service import Config


class TestCalendarFilteringDirect(unittest.TestCase):
    """Test calendar filtering functionality directly"""

    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

    def tearDown(self):
        """Tear down test environment"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_get_calendars_with_chat_direct(self):
        """Test getting calendars with chat_id directly"""
        config = Config(
            {
                "DB_PROVIDER": "sqlite",
                "DB_PATH": self.temp_db.name,
            }
        )

        provider = DatabaseProvider(config)
        db = Database(provider, config)

        calendar_entity, _, _ = provider.get_entities()

        calendar_entity.create_calendar("chat1", "tg", "https://example.com/cal1.ics")
        calendar_entity.create_calendar("chat2", "max", "https://example.com/cal2.ics")

        calendars_with_chat = calendar_entity.get_calendars_with_chat()

        self.assertEqual(len(calendars_with_chat), 2)
        chat_ids = [c.chat_id for c in calendars_with_chat]
        self.assertIn("chat1", chat_ids)
        self.assertIn("chat2", chat_ids)

        provider.close()


if __name__ == "__main__":
    unittest.main()
