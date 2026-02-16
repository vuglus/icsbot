from migrations.sqlite.base import SqliteMigration
import logging

# Configure logging
logger = logging.getLogger(__name__)


class AddCalendarTimezoneMigration(SqliteMigration):
    """Add timezone column to calendars table and set default GMT+3 for existing calendars"""
    
    def run(self, connection):
        """Run the migration using the provided SQLite connection"""
        logger.info("Starting add_calendar_timezone migration")
        
        cursor = connection.cursor()
        
        try:
            # Check if timezone column already exists
            cursor.execute("PRAGMA table_info(calendars)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'timezone' not in columns:
                # Add timezone column to calendars table
                cursor.execute('''
                    ALTER TABLE calendars
                    ADD COLUMN timezone TEXT DEFAULT 'GMT+3'
                ''')
            else:
                logger.info("Timezone column already exists in calendars table")
            
            # Update all existing calendars to have GMT+3 timezone (for those that might be NULL)
            cursor.execute('''
                UPDATE calendars
                SET timezone = 'GMT+3'
                WHERE timezone IS NULL
            ''')
            
            connection.commit()
            logger.info("Completed add_calendar_timezone migration")
            
        except Exception as e:
            connection.rollback()
            logger.error(f"Error during add_calendar_timezone migration: {e}")
            raise
        finally:
            cursor.close()
        
        logger.info("Completed add_calendar_timezone migration")