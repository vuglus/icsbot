import logging
from services.database import get_db_connection

# Configure logging
logger = logging.getLogger(__name__)

def run():
    logger.info(f"Starting {__file__} migration")
    
    conn = get_db_connection()
    cursor = conn.cursor()    
    try:
        cursor.execute('DELETE FROM events WHERE events.calendar_id NOT IN (SELECT id FROM calendars)')
        conn.commit()
        logger.info("Completed remove_calendar_duplicates migration")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error during migration: {e}")
        raise
    finally:
        conn.close()
    
    logger.info(f"Completed {__file__} migration")