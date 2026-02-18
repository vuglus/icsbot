import logging
import ydb
import uuid
from datetime import datetime
from typing import List
from entity.base import BaseMigrationEntity, Migration

# Configure logging
logger = logging.getLogger(__name__)


class MigrationEntity(BaseMigrationEntity):
    """YDB implementation for migration-related database operations"""
    
    def __init__(self, session):
        self.session = session
    
    def create_migration_table(self):
        """Create the migrations table"""
        def callee(session):
            try:
                query = """
                CREATE TABLE migrations (
                    id Utf8,
                    name Utf8,
                    executed_at Timestamp,
                    PRIMARY KEY (id)
                )
                """
                session.execute(query)
                logger.info("Migrations table created")
            except Exception as e:
                # Check if table already exists
                if "already exists" in str(e):
                    logger.info("Migrations table already exists")
                else:
                    logger.error(f"Error creating migrations table: {e}")
                    raise
        
        return self.session.retry_operation_sync(callee)
    
    def get_executed_migrations(self) -> List[Migration]:
        """Get list of executed migrations"""
        def callee(session):
            try:
                query = """
                SELECT id, name, executed_at FROM migrations ORDER BY id;
                """
                prepared_query = session.prepare(query)
                result = session.transaction().execute(
                    prepared_query,
                    commit_tx=True,
                )
                
                migrations = []
                for row in result[0].rows:
                    # Convert YDB timestamp to string
                    executed_at = str(row.executed_at) if row.executed_at else ""
                    migrations.append(Migration(row.id, row.name, executed_at))
                
                return migrations
            except Exception as e:
                logger.error(f"Error getting executed migrations: {e}")
                return []
        
        return self.session.retry_operation_sync(callee)
    
    def record_migration(self, name: str):
        """Record a migration as executed"""
        def callee(session):
            try:
                # Generate a UUID for the migration ID since YDB doesn't have auto-increment
                migration_id = uuid.uuid4().hex
                
                query = """
                DECLARE $id AS Utf8;
                DECLARE $name AS Utf8;
                UPSERT INTO migrations (id, name, executed_at) VALUES ($id, $name, CurrentUtcTimestamp());
                """
                prepared_query = session.prepare(query)
                session.transaction().execute(
                    prepared_query,
                    parameters={
                        "$id": migration_id,
                        "$name": name
                    },
                    commit_tx=True,
                )
                logger.info(f"Recorded migration: {name}")
            except Exception as e:
                logger.error(f"Error recording migration {name}: {e}")
                raise
        
        return self.session.retry_operation_sync(callee)
    
    def is_migration_executed(self, name: str) -> bool:
        """Check if a migration has been executed"""
        def callee(session):
            try:
                query = """
                DECLARE $name AS Utf8;
                SELECT 1 FROM migrations WHERE name = $name;
                """
                prepared_query = session.prepare(query)
                result = session.transaction().execute(
                    prepared_query,
                    parameters={"$name": name},
                    commit_tx=True,
                )
                
                return len(result[0].rows) > 0
            except Exception as e:
                logger.error(f"Error checking if migration {name} is executed: {e}")
                return False
        
        return self.session.retry_operation_sync(callee)
    
    def migration_table_exists(self) -> bool: 
        def callee(session):
            try:
                session.describe_table("migrations")
                return True
            except ydb.SchemeError:
                return False

        return self.session.retry_operation_sync(callee)

    def execute(self, queries: List): 
        def callee(session):
            try:
                for query in queries: 
                    logger.info(f"executing migration: {query}")
                    session.execute_scheme(query)
            except Exception as e:
                logger.error(f"Error executing migration {query}: {e}")
                raise

        return self.session.retry_operation_sync(callee)
