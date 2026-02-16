from migrations.sqlite.base import SqliteMigration
import logging

# Configure logging
logger = logging.getLogger(__name__)


class RemoveCalendarDuplicatesMigration(SqliteMigration):
    """Remove duplicate calendars from the database"""
    
    def run(self, connection):
        """Run the migration using the provided SQLite connection"""
        logger.info("Starting remove_calendar_duplicates migration")
        
        cursor = connection.cursor()
        
        try:
            # Remove duplicate calendars, keeping only the one with the lowest ID
            cursor.execute('''
                DELETE FROM calendars
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM calendars
                    GROUP BY user_id, url
                )
            ''')
            
            deleted_count = cursor.rowcount
            connection.commit()
            
            logger.info(f"Removed {deleted_count} duplicate calendars")
            logger.info("Completed remove_calendar_duplicates migration")
            
        except Exception as e:
            connection.rollback()
            logger.error(f"Error during remove_calendar_duplicates migration: {e}")
            raise
        finally:
            cursor.close()
        
        logger.info("Completed remove_calendar_duplicates migration")