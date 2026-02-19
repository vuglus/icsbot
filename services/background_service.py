import logging
from apscheduler.schedulers.background import BackgroundScheduler
from services.calendar_service import CalendarService
from services.notification_service import NotificationService

# Configure logging
logger = logging.getLogger(__name__)

def start_background_processes(
        calendarService: CalendarService,
        notificationService: NotificationService,
        syncInterval: int,
        notifyInterval: int
):
    """Start background processes"""
    scheduler = BackgroundScheduler()
    
    # Add sync job
    scheduler.add_job(
        calendarService.sync_all_calendars,
        'interval',
        minutes=syncInterval,
        id='ics_sync'
    )
    
    # Add notification check job
    scheduler.add_job(
        notificationService.check_pending_notifications,
        'interval',
        seconds=notifyInterval,
        id='notification_check'
    )
    
    scheduler.start()
    logger.info("Background processes started")
    
    return scheduler