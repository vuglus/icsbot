import sqlite3
import os
import logging
from typing import List

# Configure logging
logger = logging.getLogger(__name__)

# Import migration classes
from migrations.sqlite.initial_schema import InitialSchemaMigration as SqliteInitialSchemaMigration
from migrations.sqlite.remove_calendar_duplicates import RemoveCalendarDuplicatesMigration as SqliteRemoveCalendarDuplicatesMigration
from migrations.sqlite.add_calendar_timezone import AddCalendarTimezoneMigration as SqliteAddCalendarTimezoneMigration
from migrations.sqlite.enforce_calendar_unique_constraint import EnforceCalendarUniqueConstraintMigration as SqliteEnforceCalendarUniqueConstraintMigration
from migrations.sqlite.m20260201_unique_event import M20260201UniqueEventMigration as SqliteM20260201UniqueEventMigration
from migrations.sqlite.m202602021223_event_fix_calendsar import M202602021223EventFixCalendarMigration as SqliteM202602021223EventFixCalendarMigration

from migrations.ydb.initial_schema import InitialSchemaMigration as YdbInitialSchemaMigration

class Migration:
    def __init__(self, id: int, name: str, executed_at: str):
        self.id = id
        self.name = name
        self.executed_at = executed_at


class MigrationManager:
    """Manager for running database migrations"""
    
    def __init__(self, db_provider: str, db_connection=None, ydb_session=None):
        self.db_provider = db_provider
        self.db_connection = db_connection
        self.ydb_session = ydb_session
        self.migrations_table_initialized = False
    
    def init_migration_table(self):
        """Initialize the migrations table"""
        if self.migrations_table_initialized:
            return
        
        if self.db_provider == "sqlite":
            cursor = self.db_connection.cursor()
            
            # Check if migrations table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                cursor.execute('''
                    CREATE TABLE migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                logger.info("Created migrations table")
            else:
                logger.info("Migrations table already exists")
            
            self.db_connection.commit()
            cursor.close()
        elif self.db_provider == "ydb":
            # For YDB, we'll use a simple approach for tracking migrations
            # In a real implementation, you would need a more robust solution
            logger.info("Migration tracking for YDB would be implemented differently")
        
        self.migrations_table_initialized = True
    
    def get_executed_migrations(self) -> List[Migration]:
        """Get list of executed migrations"""
        if self.db_provider == "sqlite":
            try:
                cursor = self.db_connection.cursor()
                
                cursor.execute('SELECT * FROM migrations ORDER BY id')
                rows = cursor.fetchall()
                cursor.close()
                
                return [Migration(row['id'], row['name'], row['executed_at']) for row in rows]
            except Exception as e:
                logger.error(f"Error getting executed migrations: {e}")
                return []
        elif self.db_provider == "ydb":
            # For YDB, return empty list for now
            # In a real implementation, you would need to implement this
            return []
    
    def record_migration(self, name: str):
        """Record a migration as executed"""
        if self.db_provider == "sqlite":
            cursor = self.db_connection.cursor()
            
            try:
                cursor.execute('INSERT INTO migrations (name) VALUES (?)', (name,))
                self.db_connection.commit()
                logger.info(f"Recorded migration: {name}")
            except sqlite3.IntegrityError:
                logger.warning(f"Migration {name} already recorded")
            finally:
                cursor.close()
        elif self.db_provider == "ydb":
            # For YDB, just log for now
            # In a real implementation, you would need to implement this
            logger.info(f"Would record migration: {name}")
    
    def run_migration(self, name: str, migration_instance):
        """Run a migration if it hasn't been executed yet"""
        executed_migrations = self.get_executed_migrations()
        executed_names = [m.name for m in executed_migrations]
        
        if name in executed_names:
            logger.info(f"Migration {name} already executed, skipping")
            return False
        
        logger.info(f"Running migration: {name}")
        if self.db_provider == "sqlite":
            migration_instance.run(self.db_connection)
        elif self.db_provider == "ydb":
            migration_instance.run(self.ydb_session)
        
        self.record_migration(name)
        return True
    
    def run_all_migrations(self):
        """Run all migrations"""
        logger.info("Running all migrations")
        self.init_migration_table()
        
        try:
            # Get the appropriate migration classes based on provider
            if self.db_provider == "sqlite":
                migrations = [
                    ("initial_schema", SqliteInitialSchemaMigration()),
                    ("remove_calendar_duplicates", SqliteRemoveCalendarDuplicatesMigration()),
                    ("add_calendar_timezone", SqliteAddCalendarTimezoneMigration()),
                    ("enforce_calendar_unique_constraint", SqliteEnforceCalendarUniqueConstraintMigration()),
                    ("m20260201_unique_event", SqliteM20260201UniqueEventMigration()),
                    ("m202602021223_event_fix_calendar", SqliteM202602021223EventFixCalendarMigration()),
                ]
            elif self.db_provider == "ydb":
                migrations = [
                    ("initial_schema", YdbInitialSchemaMigration()),
                ]
            # Run migrations in order
            for name, migration_instance in migrations:
                self.run_migration(name, migration_instance)
            
            logger.info("All migrations completed")
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            raise