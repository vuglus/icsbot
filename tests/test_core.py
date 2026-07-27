import unittest
import tempfile
import os
import sqlite3
from services.database import Database
from services.database_provider import DatabaseProvider
from services.config_service import Config
from entity.base import Calendar, SentNotification


class TestCore(unittest.TestCase):
    """Test core functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

    def tearDown(self):
        """Tear down test environment"""
        if os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except PermissionError:
                pass

    def test_database_initialization(self):
        """Test database initialization"""
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

        self.assertIsNotNone(calendar_entity)
        self.assertIsNotNone(sent_notification_entity)
        self.assertIsNotNone(migration_entity)

    def test_calendar_operations(self):
        """Test calendar CRUD operations"""
        config = Config(
            {
                "DB_PROVIDER": "sqlite",
                "DB_PATH": self.temp_db.name,
            }
        )

        provider = DatabaseProvider(config)
        db = Database(provider, config)
        calendar_entity, _, _ = provider.get_entities()

        calendar = calendar_entity.create_calendar(
            "chat1", "tg", "https://example.com/test.ics"
        )
        self.assertIsInstance(calendar, Calendar)
        self.assertIsNotNone(calendar.id)
        self.assertEqual(calendar.chat_id, "chat1")
        self.assertEqual(calendar.chat_type, "tg")
        self.assertEqual(calendar.url, "https://example.com/test.ics")

        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 1)

        calendars_with_chat = calendar_entity.get_calendars_with_chat()
        self.assertEqual(len(calendars_with_chat), 1)

        calendar2 = calendar_entity.create_calendar(
            "chat1", "tg", "https://example.com/test.ics"
        )
        self.assertEqual(calendar.id, calendar2.id)

        calendar3 = calendar_entity.create_calendar(
            "chat2", "max", "https://example.com/test.ics"
        )
        self.assertNotEqual(calendar.id, calendar3.id)

        calendars = calendar_entity.get_calendars()
        self.assertEqual(len(calendars), 2)

        by_id = calendar_entity.get_calendar_by_id(calendar.id)
        self.assertIsNotNone(by_id)
        self.assertEqual(by_id.id, calendar.id)

        deleted = calendar_entity.delete_calendar(calendar.id)
        self.assertTrue(deleted)
        self.assertIsNone(calendar_entity.get_calendar_by_id(calendar.id))

        provider.close()

    def test_sent_notification_operations(self):
        """Test sent notification entity operations"""
        config = Config(
            {
                "DB_PROVIDER": "sqlite",
                "DB_PATH": self.temp_db.name,
            }
        )

        provider = DatabaseProvider(config)
        db = Database(provider, config)
        calendar_entity, sent_entity, _ = provider.get_entities()

        calendar = calendar_entity.create_calendar(
            "chat1", "tg", "https://example.com/test.ics"
        )

        self.assertFalse(sent_entity.is_event_sent(calendar.id, "event-uid-1"))

        sent_entity.record_sent(calendar.id, "event-uid-1", "chat1", '{"test": "data"}')

        self.assertTrue(sent_entity.is_event_sent(calendar.id, "event-uid-1"))
        self.assertFalse(sent_entity.is_event_sent(calendar.id, "event-uid-2"))

        notifications = sent_entity.get_sent_notifications()
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].event_uid, "event-uid-1")
        self.assertEqual(notifications[0].chat_id, "chat1")

        provider.close()


if __name__ == "__main__":
    unittest.main()
