from migrations.sqlite.base import SqliteMigration
import logging
from entity.base import BaseMigrationEntity

logger = logging.getLogger(__name__)


class InitialSchemaMigration(SqliteMigration):
    def run(self, entity: BaseMigrationEntity):
        logger.info("Starting initial_schema migration")
        entity.execute("""
            CREATE TABLE IF NOT EXISTS calendars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                chat_id TEXT,
                chat_type TEXT,
                url TEXT NOT NULL,
                client_type TEXT DEFAULT 'ics',
                last_sync_at TIMESTAMP,
                sync_hash TEXT,
                timezone TEXT DEFAULT 'GMT+3',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, url)
            )
        """)
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
        logger.info("Completed initial_schema migration")
