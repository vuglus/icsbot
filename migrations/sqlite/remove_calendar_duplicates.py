from migrations.sqlite.base import SqliteMigration
import logging

# Configure logging
logger = logging.getLogger(__name__)


class RemoveCalendarDuplicatesMigration(SqliteMigration):
    """Remove duplicate calendars from the database"""
    
    def run(self, entity):
        """Run the migration using the provided SQLite connection"""
        logger.info("Starting remove_calendar_duplicates migration")
        
        entity.execute(['''
            DELETE FROM calendars
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM calendars
                GROUP BY user_id, url
            )
        '''])
