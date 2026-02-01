import logging
from services.database import get_db_connection

# Configure logging
logger = logging.getLogger(__name__)

def run():
    """Enforce unique constraint on calendars (user_id, url) and remove duplicates"""
    logger.info("Starting enforce_calendar_unique_constraint migration")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First, remove any remaining duplicate calendars
        # Find duplicate calendars (same user_id and url)
        cursor.execute('''
            SELECT user_id, url, COUNT(*) as count
            FROM calendars
            GROUP BY user_id, url
            HAVING COUNT(*) > 1
        ''')
        
        duplicates = cursor.fetchall()
        logger.info(f"Found {len(duplicates)} sets of duplicate calendars")
        
        removed_count = 0
        for duplicate in duplicates:
            user_id, url, count = duplicate
            
            # Get all IDs for this duplicate set, ordered by ID (ascending)
            cursor.execute('''
                SELECT id
                FROM calendars
                WHERE user_id = ? AND url = ?
                ORDER BY id ASC
            ''', (user_id, url))
            
            calendar_ids = [row['id'] for row in cursor.fetchall()]
            
            # Keep the first one (smallest ID), delete the rest
            ids_to_delete = calendar_ids[1:]  # All except the first
            
            # Delete duplicate calendars (this will also delete their events due to CASCADE)
            for calendar_id in ids_to_delete:
                cursor.execute('DELETE FROM calendars WHERE id = ?', (calendar_id,))
                removed_count += 1
                logger.info(f"Deleted duplicate calendar {calendar_id} for user {user_id}")
        
        if removed_count > 0:
            conn.commit()
            logger.info(f"Removed {removed_count} duplicate calendars")
        else:
            logger.info("No duplicate calendars found")
        
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_calendars_user_url_unique ON calendars (user_id, url)')        
        conn.commit()
        logger.info("Completed enforce_calendar_unique_constraint migration")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error during migration: {e}")
        raise
    finally:
        conn.close()
    
    logger.info("Completed enforce_calendar_unique_constraint migration")