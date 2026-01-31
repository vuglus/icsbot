import logging
from services.database import get_db_connection

# Configure logging
logger = logging.getLogger(__name__)

def run():
    """Add timezone column to calendars table and set default GMT+3 for existing calendars"""
    logger.info("Starting add_calendar_timezone migration")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
        
        conn.commit()
        logger.info("Completed add_calendar_timezone migration")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error during add_calendar_timezone migration: {e}")
        raise
    finally:
        conn.close()
    
    logger.info("Completed add_calendar_timezone migration")