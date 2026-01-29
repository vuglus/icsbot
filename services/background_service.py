import logging
from apscheduler.schedulers.background import BackgroundScheduler
from .calendar_service import sync_all_calendars
from .notification_service import check_pending_notifications

# Configure logging
logger = logging.getLogger(__name__)

# Global variables
SYNC_INTERVAL_MINUTES = None  # This will be set from the main app
NOTIFY_INTERVAL_SECONDS = None  # This will be set from the main app

def start_background_processes():
    """Start background processes"""
    scheduler = BackgroundScheduler()
    
    # Add sync job
    scheduler.add_job(
        sync_all_calendars,
        'interval',
        minutes=SYNC_INTERVAL_MINUTES,
        id='ics_sync'
    )
    
    # Add notification check job
    scheduler.add_job(
        check_pending_notifications,
        'interval',
        seconds=NOTIFY_INTERVAL_SECONDS,
        id='notification_check'
    )
    
    scheduler.start()
    logger.info("Background processes started")
    
    return scheduler