from migrations.sqlite.base import SqliteMigration
import logging
from entity.base import BaseMigrationEntity


# Configure logging
logger = logging.getLogger(__name__)


class InitialSchemaMigration(SqliteMigration):
    """Initialize the database with required tables"""
    
    def run(self, entity: BaseMigrationEntity):
        """Run the migration using the provided SQLite connection"""
        logger.info("Starting initial_schema migration")
        
        try:
            # Create users table
            entity.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create calendars table
            entity.execute('''
                CREATE TABLE IF NOT EXISTS calendars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    last_sync_at TIMESTAMP,
                    sync_hash TEXT,
                    timezone TEXT DEFAULT 'GMT+3',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(user_id, url)
                )
            ''')
            
            # Create events table
            entity.execute('''
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
                    FOREIGN KEY (calendar_id) REFERENCES calendars (id) ON DELETE CASCADE,
                    UNIQUE(uid, calendar_id)
                )
            ''')
            
            # Create indexes
            entity.execute('CREATE INDEX IF NOT EXISTS idx_calendars_user_id ON calendars (user_id)')
            entity.execute('CREATE INDEX IF NOT EXISTS idx_events_calendar_id ON events (calendar_id)')
            entity.execute('CREATE INDEX IF NOT EXISTS idx_events_start_datetime ON events (start_datetime)')
            entity.execute('CREATE INDEX IF NOT EXISTS idx_events_notified ON events (notified)')
            
            entity.commit()
            logger.info("Completed initial_schema migration")
            
        except Exception as e:
            entity.rollback()
            logger.error(f"Error during initial_schema migration: {e}")
            raise
        
        logger.info("Completed initial_schema migration")