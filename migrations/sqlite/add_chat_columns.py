from migrations.sqlite.base import SqliteMigration
import logging
from entity.base import BaseMigrationEntity

logger = logging.getLogger(__name__)


class AddChatColumnsMigration(SqliteMigration):
    def run(self, entity: BaseMigrationEntity):
        logger.info("Starting add_chat_columns migration")
        try:
            entity.execute("SELECT chat_id FROM calendars LIMIT 1")
            logger.info("chat_id column already exists, skipping")
        except Exception:
            entity.execute("ALTER TABLE calendars ADD COLUMN chat_id TEXT")
            logger.info("Added chat_id column")

        try:
            entity.execute("SELECT chat_type FROM calendars LIMIT 1")
            logger.info("chat_type column already exists, skipping")
        except Exception:
            entity.execute("ALTER TABLE calendars ADD COLUMN chat_type TEXT")
            logger.info("Added chat_type column")

        try:
            entity.execute("SELECT client_type FROM calendars LIMIT 1")
            logger.info("client_type column already exists, skipping")
        except Exception:
            entity.execute(
                "ALTER TABLE calendars ADD COLUMN client_type TEXT DEFAULT 'ics'"
            )
            logger.info("Added client_type column")

        entity.execute("""
            CREATE TABLE IF NOT EXISTS sent_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calendar_id INTEGER NOT NULL,
                event_uid TEXT NOT NULL,
                chat_id TEXT NOT NULL,
                event_data TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (calendar_id) REFERENCES calendars (id) ON DELETE CASCADE
            )
        """)
        entity.execute(
            "CREATE INDEX IF NOT EXISTS idx_sent_notifications_calendar ON sent_notifications (calendar_id)"
        )
        entity.execute(
            "CREATE INDEX IF NOT EXISTS idx_sent_notifications_event ON sent_notifications (calendar_id, event_uid)"
        )

        entity.execute("DROP TABLE IF EXISTS events")
        entity.execute("DROP TABLE IF EXISTS users")

        logger.info("Completed add_chat_columns migration")
