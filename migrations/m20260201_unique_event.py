import logging
from services.database import get_db_connection

# Configure logging
logger = logging.getLogger(__name__)

def run():
    logger.info(f"Starting {__file__} migration")
    
    conn = get_db_connection()
    cursor = conn.cursor()    
    try:
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_calendars_events_unique ON events (calendar_id, uid)')
        conn.commit()
        logger.info("Completed idx_calendars_events_unique migration")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error during migration: {e}")
        raise
    finally:
        conn.close()
    
    logger.info(f"Completed {__file__} migration")