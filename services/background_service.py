import logging
from apscheduler.schedulers.background import BackgroundScheduler
from services.calendar_service import CalendarService
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)


def start_background_processes(
    notificationService: NotificationService, notifyInterval: int
):
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        notificationService.check_pending_notifications,
        "interval",
        seconds=notifyInterval,
        id="notification_check",
    )

    scheduler.start()
    logger.info("Background processes started")
    return scheduler
