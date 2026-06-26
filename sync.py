import logging
from services.config_service import Config
from services.calendar_service import CalendarService
from services.database_provider import DatabaseProvider
from services.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    config = Config({})
    # Initialize services
    provider = DatabaseProvider(config)
    db = Database(provider, config)
    calendar_service = CalendarService(db, tzone=config.getTZone())
    logger.info("Application initialized successfully")
    calendar_service.sync_all_calendars()
    logger.info("ICS-Sync done")
