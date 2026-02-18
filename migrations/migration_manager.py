import sqlite3
import os
import logging
from typing import List
from entity.base import BaseMigrationEntity

# Configure logging
logger = logging.getLogger(__name__)

# Import migration classes
from migrations.sqlite.initial_schema import InitialSchemaMigration as SqliteInitialSchemaMigration
from migrations.sqlite.remove_calendar_duplicates import RemoveCalendarDuplicatesMigration as SqliteRemoveCalendarDuplicatesMigration

from migrations.ydb.m20260218_migration_table import m20260218_migration_table
from migrations.ydb.initial_schema import InitialSchemaMigration as YdbInitialSchemaMigration

class Migration:
    def __init__(self, id: int, name: str, executed_at: str):
        self.id = id
        self.name = name
        self.executed_at = executed_at


class MigrationManager:
    """Manager for running database migrations"""
    
    def __init__(self, provider: str, migrationEntity: BaseMigrationEntity):
        self.entity = migrationEntity
        self.provider = provider
        self.migrations_table_initialized = False

    def init_migration_table(self):
        """Initialize the migrations table"""
        if self.migrations_table_initialized:
            return
        
        if not self.entity.migration_table_exists(): 
            self.run_migration('InitMigrationsEngine', m20260218_migration_table())
        
        self.migrations_table_initialized = True
    
    def record_migration(self, name: str):
        self.entity.record_migration(name)
    
    def run_migration(self, name: str, migration_instance):
        """Run a migration if it hasn't been executed yet"""
        executed_migrations = self.entity.get_executed_migrations()
        executed_names = [m.name for m in executed_migrations]
        
        if name in executed_names:
            logger.info(f"Migration {name} already executed, skipping")
            return False
        
        logger.info(f"Running migration: {name}")
        migration_instance.run(self.entity)        
        self.record_migration(name)
        return True
    
    def run_all_migrations(self):
        """Run all migrations"""
        logger.info("Running all migrations")
        self.init_migration_table()
        
        try:
            # Get the appropriate migration classes based on provider
            if self.provider == "sqlite":
                migrations = [
                    ("initial_schema", SqliteInitialSchemaMigration()),
                    ("remove_calendar_duplicates", SqliteRemoveCalendarDuplicatesMigration()),
                ]
            elif self.provider == "ydb":
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