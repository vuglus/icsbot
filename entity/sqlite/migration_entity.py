import sqlite3
import logging
from datetime import datetime
from typing import List
from entity.base import BaseMigrationEntity, Migration

# Configure logging
logger = logging.getLogger(__name__)


class MigrationEntity(BaseMigrationEntity):
    """SQLite implementation for migration-related database operations"""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_migration_table(self):
        """Create the migrations table"""
        cursor = self.db_connection.cursor()
        
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.db_connection.commit()
            logger.info("Migrations table created or already exists")
        except Exception as e:
            logger.error(f"Error creating migrations table: {e}")
            raise
        finally:
            cursor.close()

    def migration_table_exists(self) -> bool:
        return self.db_connection.execute('SELECT 1 FROM migrations LIMIT 1').fetchone() is not None
    
    def get_executed_migrations(self) -> List[Migration]:
        """Get list of executed migrations"""
        cursor = self.db_connection.cursor()
        
        try:
            cursor.execute('SELECT id, name, executed_at FROM migrations ORDER BY id')
            rows = cursor.fetchall()
            return [Migration(row['id'], row['name'], row['executed_at']) for row in rows]
        except Exception as e:
            logger.error(f"Error getting executed migrations: {e}")
            return []
        finally:
            cursor.close()
    
    def record_migration(self, name: str):
        """Record a migration as executed"""
        cursor = self.db_connection.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO migrations (name) VALUES (?)',
                (name,)
            )
            self.db_connection.commit()
            logger.info(f"Recorded migration: {name}")
        except sqlite3.IntegrityError:
            logger.warning(f"Migration {name} already recorded")
        except Exception as e:
            logger.error(f"Error recording migration {name}: {e}")
            raise
        finally:
            cursor.close()
    
    def is_migration_executed(self, name: str) -> bool:
        """Check if a migration has been executed"""
        cursor = self.db_connection.cursor()
        
        try:
            cursor.execute('SELECT 1 FROM migrations WHERE name = ?', (name,))
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking if migration {name} is executed: {e}")
            return False
        finally:
            cursor.close()

    def execute(self, queries):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute('SELECT 1 FROM migrations WHERE name = ?', (name,))
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking if migration {name} is executed: {e}")
            return False
        finally:
            cursor.close()
        