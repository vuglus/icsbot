import sqlite3
import os
import logging
from typing import List
from services.database import get_db_connection

# Configure logging
logger = logging.getLogger(__name__)

class Migration:
    def __init__(self, id: int, name: str, executed_at: str):
        self.id = id
        self.name = name
        self.executed_at = executed_at

def init_migration_table():
    """Initialize the migrations table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()

def get_executed_migrations() -> List[Migration]:
    """Get list of executed migrations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM migrations ORDER BY id')
        rows = cursor.fetchall()
        conn.close()
        
        return [Migration(row['id'], row['name'], row['executed_at']) for row in rows]
    except Exception as e:
        logger.error(f"Error getting executed migrations: {e}")
        return []

def record_migration(name: str):
    """Record a migration as executed"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO migrations (name) VALUES (?)', (name,))
        conn.commit()
        logger.info(f"Recorded migration: {name}")
    except sqlite3.IntegrityError:
        logger.warning(f"Migration {name} already recorded")
    finally:
        conn.close()

def run_migration(name: str, migration_func):
    """Run a migration if it hasn't been executed yet"""
    executed_migrations = get_executed_migrations()
    executed_names = [m.name for m in executed_migrations]
    
    if name in executed_names:
        logger.info(f"Migration {name} already executed, skipping")
        return False
    
    logger.info(f"Running migration: {name}")
    migration_func()
    record_migration(name)
    return True

def run_all_migrations():
    """Run all migrations"""
    logger.info("Running all migrations")
    init_migration_table()
    
    try:
        # Import migrations here to avoid circular imports
        from migrations import initial_schema
        from migrations import remove_calendar_duplicates
        from migrations import add_calendar_timezone
        from migrations import enforce_calendar_unique_constraint
        from migrations import m20260201_unique_event
        from migrations import m202602021223_event_fix_calendsar
        
        
        # Run migrations in order
        run_migration("initial_schema", initial_schema.run)
        run_migration("remove_calendar_duplicates", remove_calendar_duplicates.run)
        run_migration("add_calendar_timezone", add_calendar_timezone.run)
        run_migration("enforce_calendar_unique_constraint", enforce_calendar_unique_constraint.run)
        run_migration("migrations/m20260201_unique_event", m20260201_unique_event.run)
        run_migration("m20260201_unique_event", m20260201_unique_event.run)
        run_migration("m202602021223_event_fix_calendsar", m202602021223_event_fix_calendsar.run)
        
        logger.info("All migrations completed")
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise